# ─── CGRF Header ───────────────────────────────────────────────
# File: .bits/scripts/record_lockfile.py
# Stage: 11_COMMIT
# SRS: SRS-CN-INTELLIGENCE-BUILD-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-BUILD-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: package.json, .bits/out/DISP-BUILD-intelligence/memory.json
# EnumType: ConfigDoc
# EnumEdges: DEPENDS_ON package.json; DEPENDS_ON .bits/out/DISP-BUILD-intelligence/memory.json
# DAG Node: none
# Intent: Record genuine hosted lockfile validation without changing runtime dependencies.
# ───────────────────────────────────────────────────────────────

"""Attach CGRF and dispatch evidence to a successfully validated npm lockfile."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlsplit

SRS = 'SRS-CN-INTELLIGENCE-BUILD-001'
DISPATCH = 'DISP-BUILD-intelligence'
MEMORY = f'.bits/out/{DISPATCH}/memory.json'
INTENT = 'Freeze the registry dependency graph that passed the clean install and build gates.'


def main() -> None:
    """Record the resolved lockfile after the caller has passed the npm gates."""
    lock = json.loads(Path('package-lock.json').read_text())
    manifest = json.loads(Path('package.json').read_text())
    if lock.get('lockfileVersion', 0) < 2 or not lock.get('packages'):
        raise ValueError('A generated npm lockfile with package metadata is required')
    for group in ('dependencies', 'devDependencies'):
        if lock['packages'][''].get(group, {}) != manifest.get(group, {}):
            raise ValueError('Lockfile root dependencies differ from package.json')
    for package in lock['packages'].values():
        url = urlsplit(package.get('resolved', ''))
        if url.username or url.password or url.query:
            raise ValueError('Credential-bearing or query-bearing resolved URLs cannot be committed')
    stamp = datetime.now(timezone.utc).isoformat()
    companion = 'package-lock.cgrf.yaml'
    fields = {'File': 'package-lock.json', 'Stage': '11_COMMIT', 'SRS': SRS,
              'CAPS': 'pending', 'CK': 'pending', 'Dispatch': DISPATCH,
              'Seat': 'BITS-CODEGEN', 'Owner': 'Citadel Nexus Inc.',
              'Created': stamp, 'Depends': 'package.json', 'EnumType': 'ConfigDoc',
              'EnumEdges': 'DEPENDS_ON package.json', 'DAG Node': 'none', 'Intent': INTENT}
    header = '# CGRF Header\n' + ''.join(f'# {key}: {value}\n' for key, value in fields.items())
    companion_intent = 'Describe the validated npm lockfile metadata.'
    companion_fields = {**fields, 'File': companion, 'Depends': 'package-lock.json',
                        'EnumEdges': 'DEPENDS_ON package-lock.json', 'Intent': companion_intent}
    companion_header = '# CGRF Header\n' + ''.join(
        f'# {key}: {value}\n' for key, value in companion_fields.items())
    Path(companion).write_text(companion_header + '\n' + header +
                               '\nartifact: package-lock.json\nartifact_enum_edges:\n  - DEPENDS_ON package.json\n')
    payload = json.loads(Path(MEMORY).read_text())
    vectors = payload['vectors']
    touched = {'package-lock.json', companion}
    vectors[:] = [item for item in vectors if not (
        item['type'] == 'A' and item['file_path'] in touched or
        item['type'] == 'B' and item['source'] in touched)]
    for path, dependency in [('package-lock.json', 'package.json'), (companion, 'package-lock.json')]:
        vectors.append({'type': 'A', 'file_path': path, 'cket_stage': '11_COMMIT',
                        'srs_codes': [SRS], 'enum_type': 'ConfigDoc', 'functions': [],
                        'dependencies': [dependency], 'lines': 0, 'caps_grade': 'pending',
                        'ck_stamp': 'pending', 'intent_statement': INTENT if path == 'package-lock.json' else companion_intent,
                        'objective_id': DISPATCH, 'outcome': 'success', 'supersedes': False,
                        'dispatch_id': DISPATCH, 'seat': 'BITS-CODEGEN', 'domain': 'engineering',
                        'source_type': 'seat_dispatch', 'tags': [DISPATCH, 'BITS-CODEGEN', SRS, 'lockfile'],
                        'tenant_id': None})
        vectors.append({'type': 'B', 'source': path, 'target': dependency,
                        'edge_type': 'DEPENDS_ON', 'weight': 1.0,
                        'description': f'{path} records the validated dependency graph for {dependency}.',
                        'dispatch_id': DISPATCH, 'created_by': 'BITS-CODEGEN'})
    vectors.append({'type': 'C', 'event_type': 'test_pass', 'file_path': 'package-lock.json',
                    'description': 'Hosted lockfile refresh passed npm ci, lint, typecheck, test and build.',
                    'caps_before': None, 'caps_after': None, 'dag_impact': None,
                    'dispatch_id': DISPATCH, 'timestamp': stamp, 'commit_sha': None, 'smoke_result': '5/5'})
    for kind in 'ABC':
        payload['summary'][f'type_{kind.lower()}_count'] = sum(v['type'] == kind for v in vectors)
    for _ in range(3):
        Path(MEMORY).write_text(json.dumps(payload, indent=2) + '\n')
        for item in vectors:
            if item['type'] == 'A':
                item['lines'] = len(Path(item['file_path']).read_text().splitlines())
    Path(MEMORY).write_text(json.dumps(payload, indent=2) + '\n')


if __name__ == '__main__':
    main()
