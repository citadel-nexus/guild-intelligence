<!--
# ─── CGRF Header ───────────────────────────────────────────────
# File: .bits/queue/DISP-BUILD-intelligence.md
# Stage: 11_COMMIT
# SRS: SRS-CN-INTELLIGENCE-BUILD-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-BUILD-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: .bits/srs/SRS-CN-INTELLIGENCE-BUILD-001.md
# EnumType: Doc
# EnumEdges: DEPENDS_ON .bits/srs/SRS-CN-INTELLIGENCE-BUILD-001.md
# DAG Node: none
# Intent: Record build-repair authorization, gates and unresolved dependency access.
# ───────────────────────────────────────────────────────────────
-->

# DISP-BUILD-intelligence

- srs: SRS-CN-INTELLIGENCE-BUILD-001
- status: in_progress
- mode: staging
- seat: BITS-CODEGEN
- operator: Dmitry Richard, mr.nobody@citadel-nexus.com
- authorization_source: explicit Bits AI operator directive, 2026-10-20
- brief: .bits/srs/SRS-CN-INTELLIGENCE-BUILD-001.md
- base: f3232d64a48d037ab24a60961319f7a0faf1ce1c (merged build PR #22)
- branch: dd/bits/SRS-CN-INTELLIGENCE-GOVERNANCE-001-provenance (session publication binding)

## Authorization and task table

The operator explicitly authorized fixing the npm lockfile, pinned Node,
TypeScript configuration, ESLint, tests, CI expression syntax, and real-output
provenance under this new SRS. Existing governance tests and security scans
must remain. No prod/deploy, push to main, GitHub settings or secrets changes.

| Phase | Task | Gate |
| --- | --- | --- |
| A | Register dispatch; declare Node/compiler/linter/test configuration | config checks |
| B | Fix source syntax; install resolved dependencies | npm ci; lint; typecheck; test; build |
| C | Align CI, preserve security scans and signing boundary | 12 governance tests and build-policy tests |

```bash
npm ci
npm run lint
npm run typecheck
npm test
npm run build
python -m unittest discover -s .bits/tests -p 'test_*.py' -v
```

## Dependency blocker

Offline resolution of @citadel-guilds/sdk failed with ENOTCACHED: no registry
metadata or SDK/NATS/Vitest packages are cached. Shell network downloads are
restricted in this sandbox. The managed SDK repository attachment was also
rejected because public and private repositories cannot be mixed in this
session. The operator was asked for the approved SDK source and registry
access or a complete dependency cache. No replacement SDK is authorized.

## Memory Brief

Governance PR #21 added a fail-closed provenance workflow and documented the
missing npm scaffold. Its 12 policy/packaging tests must continue to pass.
No additional USO_MCP Memory Brief was supplied.

## Authorized continuation

The operator authorized this same session/dispatch to add a manual-only hosted
lockfile refresh that opens bits/lockfile-refresh after every npm gate passes,
positive/tampered/wrong-signer attestation checks, and BUILD.md prerequisites.
No hosted workflow is dispatched here. Package/PR/settings permissions remain
admin prerequisites, not settings changes performed by this seat.

The bound branch was an ancestor of current main. Build commit a20b142 was
already merged in PR #22, so fast-forwarding to origin/main preserved all
published history and avoided replaying it. The new PR diff contains only
this BUILD continuation. The UI still performs PR creation; no refs are pushed
from the sandbox.
