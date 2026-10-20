<!--
# ─── CGRF Header ───────────────────────────────────────────────
# File: .bits/srs/SRS-CN-INTELLIGENCE-BUILD-001.md
# Stage: 04_HYPOTHESIZE
# SRS: SRS-CN-INTELLIGENCE-BUILD-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-BUILD-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: .bits/srs_registry.yml
# EnumType: Doc
# EnumEdges: DEPENDS_ON .bits/srs_registry.yml
# DAG Node: none
# Intent: Bound the operator-authorized build repair and its acceptance criteria.
# ───────────────────────────────────────────────────────────────
-->

# Intelligence Guild build tooling repair

SRS: SRS-CN-INTELLIGENCE-BUILD-001
Dispatch: DISP-BUILD-intelligence
Status: in_progress. Mode: staging. Seat: BITS-CODEGEN.

The authenticated operator Dmitry Richard authorized a separate build-repair
branch and PR after governance PR #21 merged. This specification transcribes
that directive; it does not create an independent USO blueprint.

## Acceptance

- Resolve the existing SDK/NATS dependency graph and commit a generated
  lockfile so a clean npm ci succeeds. Do not fabricate packages, integrity
  hashes or ambient declarations to disguise missing runtime dependencies.
- Pin Node consistently in .nvmrc, package engines, CI and the Docker build.
- Declare compiler, linter and test tooling; strict typecheck all source and
  tests. Repair malformed source syntax without replacing the runtime SDK.
- Keep all 12 governance tests and both CodeQL and secret scanning.
- Fix GitHub expression syntax for Docker/GHCR login. Preserve the separate
  unprivileged build and signing jobs, and attest only actual compiled output.
- Report npm ci, lint, typecheck, test and build outcomes, including blockers.

## Scope and bounds

Tooling, source syntax fixes needed to compile, regression tests, CI,
provenance readiness docs, and dispatch evidence are authorized. Existing
CGRF headers and governance tests remain intact; companion memory file line
counts may be refreshed to preserve their consistency assertions.
No deployments, pushes to main, settings changes, secrets or unrelated SRS work.
Native source/test/config paths are authorized by this directive; use logical
CKET 07_BUILD/08_TEST for source/tests and 11_COMMIT for build configuration.
CKS review target B+/75. CKS/CAPS/CK remain pending.

## Continuation acceptance

- Manual-only hosted lockfile resolution with scoped GitHub Packages auth,
  all five npm gates, and a dedicated bits/lockfile-refresh PR branch.
- Read-only post-signing verification of the real artifact, requiring rejection
  of tampering and an incorrect signer identity. Preserve all 12 governance tests.
- BUILD.md documents package access, ruleset activation, Actions OIDC and
  attestation permissions, bot PR behavior and remaining offline blockers.
- Continue on the session's bound branch based on merged PR #22; do not replay
  already merged governance/build commits into the new PR.
