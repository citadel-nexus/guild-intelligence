<!--
# ─── CGRF Header ───────────────────────────────────────────────
# File: .bits/out/DISP-BUILD-intelligence/report.md
# Stage: 11_COMMIT
# SRS: SRS-CN-INTELLIGENCE-BUILD-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-BUILD-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: .bits/queue/DISP-BUILD-intelligence.md, package.json, .github/workflows/build-provenance.yml
# EnumType: Doc
# EnumEdges: DEPENDS_ON .bits/queue/DISP-BUILD-intelligence.md; DEPENDS_ON package.json; DEPENDS_ON .github/workflows/build-provenance.yml
# DAG Node: none
# Intent: Record measured build-repair results without conflating offline diagnostics with a clean install.
# ───────────────────────────────────────────────────────────────
-->

# Build repair validation and remaining blocker

SRS: SRS-CN-INTELLIGENCE-BUILD-001
Dispatch: DISP-BUILD-intelligence
Status: PARTIAL. Mode: staging. CK/CAPS/CKS: pending.
Base: a080580836081136b3512e7ff627b5cd92c8dd78, which contains merged PR #21.

## Results

| Command | Result | Evidence and limitation |
| --- | --- | --- |
| npm ci | BLOCKED | EUSAGE: no generated lockfile; run with npm_config_offline=true |
| npm install --package-lock-only --ignore-scripts --no-audit --no-fund | BLOCKED | ENOTCACHED for @citadel-guilds/sdk metadata in offline mode |
| npm run lint | PASS | ESLint 9.16.0 / TypeScript ESLint 8.18.0, exact declared preinstalled tools linked locally for diagnostics |
| npm run typecheck | BLOCKED | TS2307 for SDK, NATS and Vitest; no unresolved syntax diagnostics |
| npm test | BLOCKED | Vitest is not cached/installed |
| npm run build | BLOCKED | TS2307 for SDK and NATS; noEmitOnError prevents distribution output |
| python -m unittest discover -s .bits/tests -p 'test_*.py' -v | PASS | 12 unchanged governance cases and 4 new build-policy cases |

Node: 22.17.0, matching .nvmrc, engines, all Node CI setup steps and Docker.
Local npm: 9.8.1. Compiler diagnostics used preinstalled TypeScript 5.7.3
and Node types 22.19.19, matching the declared versions. Ignored node_modules
symlinks were diagnostic aids, not a successful npm installation or vendored
runtime dependencies. No SDK/NATS implementation or declaration stub was added.
No application tests, full compiled artifact, hosted signing, container build,
package publication or deployment has been claimed as successful.

## Repair scope

Strict Node ESM configs include all source and tests; build output is limited
to src and cannot emit when type errors exist. NATS imports/options syntax
and CML patch-marker corruption are repaired. Regression tests cover SDK
initialization, health timestamps, message decoding, task correlation and
failure behavior. Test doubles isolate network/service side effects only.

CI now uses the Node pin, runs typecheck, and has valid GitHub GHCR expressions.
The provenance build also requires lint/typecheck/tests before emitting and
uploading the real distribution. Its signing job remains unchanged. CodeQL
and TruffleHog remain present, as do the original 12 governance tests.
Governance memory line counts were refreshed to satisfy its existing live
metadata assertions; assertions, event history and ownership were preserved.

## Required continuation

The dependency cache lacks SDK/NATS/Vitest. Shell outbound package downloads
are restricted. The managed SDK repository attachment was separately rejected
because public and private repositories cannot be mixed in this session.
Obtain the approved @citadel-guilds/sdk source/version and access to its registry
plus registry.npmjs.org, or provide a complete dependency cache. No online
package request was attempted and no secrets/configured credentials were read.

Then generate the lockfile with npm, review its resolved URLs and integrity
metadata, remove diagnostic dependency links, and run a clean npm ci followed
by lint, typecheck, test, test:coverage and build. Keep failures visible; do not
replace the SDK with a stub or attest a placeholder archive. Repeat the policy
suite and use PROVENANCE.md for hosted attestation verification after merge.

No settings or production changes were made. This build SRS remains
in_progress until its install, application tests and compiled-build gates pass.
