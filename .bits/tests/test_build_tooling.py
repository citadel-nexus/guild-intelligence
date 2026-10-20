# ─── CGRF Header ───────────────────────────────────────────────
# File: .bits/tests/test_build_tooling.py
# Stage: 11_COMMIT
# SRS: SRS-CN-INTELLIGENCE-BUILD-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-BUILD-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: package.json, .github/workflows/build-provenance.yml, .github/workflows/ci.yml, .github/workflows/security-scan.yml
# EnumType: Test
# EnumEdges: DEPENDS_ON package.json; DEPENDS_ON .github/workflows/build-provenance.yml; DEPENDS_ON .github/workflows/ci.yml; DEPENDS_ON .github/workflows/security-scan.yml
# DAG Node: none
# Intent: Guard runtime pins, quality-gated provenance, GitHub expressions and preserved security scans.
# ───────────────────────────────────────────────────────────────

"""Validate build/runtime alignment without substituting runtime dependencies."""

import json
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


class BuildToolingTests(unittest.TestCase):
    def test_node_pin_matches_ci_and_container(self) -> None:
        version = (ROOT / '.nvmrc').read_text().strip()
        package = json.loads((ROOT / 'package.json').read_text())
        self.assertEqual(package['engines']['node'], version)
        self.assertEqual((ROOT / 'docker/Dockerfile').read_text().count(f'FROM node:{version}-alpine'), 2)
        ignored = set((ROOT / '.dockerignore').read_text().splitlines())
        self.assertTrue({'node_modules', 'dist', '.env', '.git'} <= ignored)
        for name in ['ci.yml', 'release.yml', 'build-provenance.yml', 'security-scan.yml']:
            workflow = yaml.load((ROOT / '.github/workflows' / name).read_text(), Loader=yaml.BaseLoader)
            setups = [step for job in workflow['jobs'].values() for step in job['steps']
                      if step.get('uses', '').startswith('actions/setup-node@')]
            self.assertTrue(setups, name)
            for step in setups:
                self.assertEqual(step['with']['node-version-file'], '.nvmrc')
                self.assertNotIn('node-version', step['with'])

    def test_real_build_must_pass_quality_gates_before_upload(self) -> None:
        workflow = yaml.load((ROOT / '.github/workflows/build-provenance.yml').read_text(), Loader=yaml.BaseLoader)
        steps = workflow['jobs']['build']['steps']
        required = ['npm ci', 'npm run lint', 'npm run typecheck', 'npm test', 'npm run build']
        indices = [next(i for i, step in enumerate(steps) if step.get('run') == command) for command in required]
        self.assertEqual(indices, sorted(indices))
        upload = next(i for i, step in enumerate(steps) if step.get('id') == 'upload')
        self.assertLess(indices[-1], upload)
        self.assertFalse(any('continue-on-error' in step for step in steps))
        self.assertEqual(workflow['jobs']['attest']['needs'], 'build')

    def test_ghcr_credentials_are_expressions_and_scanners_remain(self) -> None:
        workflow = yaml.load((ROOT / '.github/workflows/ci.yml').read_text(), Loader=yaml.BaseLoader)
        login = next(step for step in workflow['jobs']['docker']['steps']
                     if step.get('uses', '').startswith('docker/login-action@'))
        self.assertEqual(login['with']['username'], '${{ github.actor }}')
        self.assertEqual(login['with']['password'], '${{ secrets.GITHUB_TOKEN }}')
        security = yaml.load((ROOT / '.github/workflows/security-scan.yml').read_text(), Loader=yaml.BaseLoader)
        actions = [step.get('uses', '') for job in security['jobs'].values() for step in job['steps']]
        self.assertTrue(any(action.startswith('github/codeql-action/analyze@') for action in actions))
        self.assertTrue(any(action.startswith('trufflesecurity/trufflehog@') for action in actions))
        self.assertIn('secret-scan', security['jobs'])

    def test_typechecking_covers_source_and_tests_and_emission_fails_closed(self) -> None:
        config = json.loads((ROOT / 'tsconfig.json').read_text())
        build = json.loads((ROOT / 'tsconfig.build.json').read_text())
        self.assertTrue(config['compilerOptions']['strict'])
        self.assertTrue(config['compilerOptions']['noEmitOnError'])
        self.assertTrue({'src/**/*.ts', 'tests/**/*.ts'} <= set(config['include']))
        self.assertEqual(build['compilerOptions']['rootDir'], 'src')
        self.assertEqual(build['compilerOptions']['outDir'], 'dist')
        self.assertEqual(build['include'], ['src/**/*.ts'])


if __name__ == '__main__':
    unittest.main()
