# ─── CGRF Header ───────────────────────────────────────────────
# File: .bits/tests/test_hosted_build.py
# Stage: 11_COMMIT
# SRS: SRS-CN-INTELLIGENCE-BUILD-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-BUILD-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: .github/workflows/lockfile-refresh.yml, .github/workflows/build-provenance.yml, .bits/scripts/record_lockfile.py
# EnumType: Test
# EnumEdges: DEPENDS_ON .github/workflows/lockfile-refresh.yml; DEPENDS_ON .github/workflows/build-provenance.yml; DEPENDS_ON .bits/scripts/record_lockfile.py
# DAG Node: none
# Intent: Test manual refresh privileges, exact artifact verification and rejection paths without network access.
# ───────────────────────────────────────────────────────────────

"""Test hosted build policy and verifier failure handling without network access."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_workflow(name: str) -> dict:
    return yaml.load((ROOT / '.github/workflows' / name).read_text(), Loader=yaml.BaseLoader)


class HostedBuildTests(unittest.TestCase):
    def test_manual_refresh_has_separate_read_and_write_jobs(self) -> None:
        flow = load_workflow('lockfile-refresh.yml')
        self.assertEqual(set(flow['on']), {'workflow_dispatch'})
        self.assertEqual(flow['permissions'], {'contents': 'read'})
        refresh, publish = flow['jobs']['refresh'], flow['jobs']['publish']
        self.assertEqual(refresh['permissions'], {'contents': 'read', 'packages': 'read'})
        self.assertEqual(publish['permissions'], {'contents': 'write', 'pull-requests': 'write'})
        self.assertIn("github.repository == 'citadel-nexus/guild-intelligence'", refresh['if'])
        self.assertIn('github.event.repository.default_branch', refresh['if'])
        self.assertEqual(publish['needs'], 'refresh')
        self.assertEqual(flow['concurrency']['cancel-in-progress'], 'false')
        setup = next(s for s in refresh['steps'] if s.get('uses', '').startswith('actions/setup-node@'))
        self.assertEqual(setup['with'], {'node-version-file': '.nvmrc',
                                        'registry-url': 'https://npm.pkg.github.com', 'scope': '@citadel-guilds'})
        self.assertFalse(any('npm ' in s.get('run', '') for s in publish['steps']))
        for job in flow['jobs'].values():
            for step in job['steps']:
                if 'uses' in step:
                    self.assertRegex(step['uses'], r'^[\w-]+/[\w-]+@[0-9a-f]{40}$')
                if step.get('uses', '').startswith('actions/checkout@'):
                    self.assertEqual(step['with']['persist-credentials'], 'false')

    def test_lockfile_is_published_only_after_all_gates(self) -> None:
        jobs = load_workflow('lockfile-refresh.yml')['jobs']
        steps = jobs['refresh']['steps']
        commands = [s['run'] for s in steps if 'run' in s]
        self.assertEqual(commands, ['npm install --package-lock-only --ignore-scripts', 'npm ci',
                                    'npm run lint', 'npm run typecheck', 'npm test', 'npm run build',
                                    'python .bits/scripts/record_lockfile.py'])
        for step in steps:
            self.assertNotIn('continue-on-error', step)
            if step.get('run') in commands[:2]:
                self.assertEqual(step['env']['NODE_AUTH_TOKEN'], '${{ secrets.GITHUB_TOKEN }}')
        publish = jobs['publish']['steps']
        self.assertIn('test "$(git rev-parse HEAD)" = "$VALIDATED_SHA"', publish[1]['run'])
        self.assertIn("test \"$DEFAULT_BRANCH\" != 'bits/lockfile-refresh'", publish[1]['run'])
        self.assertEqual(publish[2]['with']['artifact-ids'], '${{ needs.refresh.outputs.artifact-id }}')
        pr = publish[-1]['with']
        self.assertEqual(pr['branch'], 'bits/lockfile-refresh')
        self.assertEqual(pr['base'], '${{ github.event.repository.default_branch }}')
        self.assertEqual(pr['sign-commits'], 'true')
        self.assertEqual(set(pr['add-paths'].split()), {'package-lock.json', 'package-lock.cgrf.yaml',
                         '.bits/out/DISP-BUILD-intelligence/memory.json'})

    def test_verifier_uses_exact_artifacts_without_signing_permissions(self) -> None:
        flow = load_workflow('build-provenance.yml')
        verifier = flow['jobs']['verify']
        self.assertEqual(set(verifier['needs']), {'build', 'attest'})
        self.assertEqual(verifier.get('permissions', flow['permissions']), {'contents': 'read'})
        self.assertEqual(verifier['steps'][0]['with']['artifact-ids'], '${{ needs.build.outputs.artifact-id }}')
        self.assertEqual(verifier['steps'][1]['with']['artifact-ids'], '${{ needs.attest.outputs.bundle-id }}')
        script = verifier['steps'][2]['run']
        for flag in ['--bundle', '--repo', '--signer-workflow', '--source-ref refs/heads/main',
                     '--source-digest', '--predicate-type https://slsa.dev/provenance/v1', '--deny-self-hosted-runners']:
            self.assertIn(flag, script)
        self.assertFalse(any('run' in step for step in flow['jobs']['attest']['steps']))
        install = next(step for step in flow['jobs']['build']['steps'] if step.get('run') == 'npm ci')
        self.assertEqual(install['env']['NODE_AUTH_TOKEN'], '${{ secrets.GUILD_PACKAGES_READ_TOKEN }}')
        self.assertNotIn('permissions', flow['jobs']['build'])

    def test_verifier_fails_closed_for_unexpected_results(self) -> None:
        script = load_workflow('build-provenance.yml')['jobs']['verify']['steps'][2]['run']
        for mode, expected_exit, calls in [('correct', 0, 3), ('positive_failure', 1, 1),
                                           ('accept_tamper', 1, 2), ('accept_wrong_signer', 1, 3)]:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                artifact = root / 'verification/artifact/guild-intelligence-abc.tar.gz'
                artifact.parent.mkdir(parents=True)
                artifact.write_bytes(b'actual artifact bytes for control-flow testing')
                bundle = root / 'verification/bundle/bundle.jsonl'
                bundle.parent.mkdir(parents=True)
                bundle.write_text('{}\n')
                bindir = root / 'bin'
                bindir.mkdir()
                fake = bindir / 'gh'
                fake.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with Path(os.environ['CALL_LOG']).open('a') as log:
    log.write(json.dumps(args) + '\\n')
mode = os.environ['VERIFY_MODE']
if mode == 'positive_failure': sys.exit(1)
tampered = args[2].endswith('.tampered')
wrong = args[args.index('--signer-workflow') + 1].endswith('/wrong-signer.yml')
if tampered: sys.exit(0 if mode == 'accept_tamper' else 1)
if wrong: sys.exit(0 if mode == 'accept_wrong_signer' else 1)
sys.exit(0)
''')
                fake.chmod(0o755)
                log = root / 'calls.jsonl'
                env = {**os.environ, 'PATH': str(bindir) + os.pathsep + os.environ['PATH'],
                       'RUNNER_TEMP': str(root), 'GITHUB_SHA': 'abc',
                       'GITHUB_REPOSITORY': 'citadel-nexus/guild-intelligence',
                       'VERIFY_MODE': mode, 'CALL_LOG': str(log)}
                result = subprocess.run(['bash', '-c', script], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, expected_exit, result.stderr)
                self.assertEqual(len(log.read_text().splitlines()), calls)
                if mode != 'positive_failure':
                    self.assertNotEqual(Path(str(artifact) + '.tampered').read_bytes(), artifact.read_bytes())

    def _record_fixture(self, root: Path, invalid: str = '') -> subprocess.CompletedProcess:
        manifest = {'dependencies': {'example': '1.0.0'}}
        (root / 'package.json').write_text(json.dumps(manifest))
        lock = {'lockfileVersion': 3, 'packages': {'': manifest, 'node_modules/example': {
            'version': '1.0.0', 'resolved': 'https://registry.npmjs.org/example/-/example-1.0.0.tgz'}}}
        if invalid == 'credentials':
            lock['packages']['node_modules/example']['resolved'] = 'https://user:password@example.test/pkg.tgz'
        if invalid == 'mismatch':
            lock['packages'][''] = {'dependencies': {'example': '2.0.0'}}
        (root / 'package-lock.json').write_text(json.dumps(lock))
        memory = root / '.bits/out/DISP-BUILD-intelligence/memory.json'
        memory.parent.mkdir(parents=True)
        memory.write_text(json.dumps({'vectors': [], 'summary': {'ioo_compliance': True, 'dkg_orphans': 0}}))
        return subprocess.run(['python', str(ROOT / '.bits/scripts/record_lockfile.py')], cwd=root,
                              capture_output=True, text=True)

    def test_generated_lock_metadata_records_real_files_and_edges(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self._record_fixture(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((root / '.bits/out/DISP-BUILD-intelligence/memory.json').read_text())
            self.assertEqual(data['summary']['type_a_count'], 2)
            self.assertEqual(data['summary']['type_b_count'], 2)
            self.assertEqual(data['summary']['type_c_count'], 1)
            header = (root / 'package-lock.cgrf.yaml').read_text()
            for record in data['vectors']:
                if record['type'] == 'A':
                    self.assertEqual(record['lines'], len((root / record['file_path']).read_text().splitlines()))
                    self.assertIn('# File: ' + record['file_path'], header)
                    self.assertIn('# Intent: ' + record['intent_statement'], header)
                    self.assertTrue(any(v['type'] == 'B' and v['source'] == record['file_path'] for v in data['vectors']))

    def test_lock_metadata_rejects_credentials_and_manifest_mismatch(self) -> None:
        for invalid in ['credentials', 'mismatch']:
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                result = self._record_fixture(root, invalid)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((root / 'package-lock.cgrf.yaml').exists())


if __name__ == '__main__':
    unittest.main()
