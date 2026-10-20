<!--
# ─── CGRF Header ───────────────────────────────────────────────
# File: .bits/context.md
# Stage: 11_COMMIT
# SRS: SRS-CN-INTELLIGENCE-GOVERNANCE-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-GOVERNANCE-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: AGENTS.md
# EnumType: ConfigDoc
# EnumEdges: DEPENDS_ON AGENTS.md
# DAG Node: none
# Intent: Bound bootstrap paths and validation to the authorized governance SRS.
# ───────────────────────────────────────────────────────────────
-->

# Current staging context

Active SRS: `SRS-CN-INTELLIGENCE-BUILD-001`.
Active dispatch: `DISP-BUILD-intelligence` (`in_progress`).
The operator authorized this separate staging build repair after PR #21 merged.
Seat: BITS-CODEGEN. Authorization: explicit 2026-10-20 operator directive.
The living-world SRS and dispatch remain unchanged and out of scope.

## Logical CKET placement

This repo uses native root, `.github/`, and `.bits/` paths. For this
bootstrap the operator-authorized prerequisite conventions map these paths
onto CKET stages; do not relocate GitHub discovery files into stage folders:

- `04_HYPOTHESIZE`: AGENTS.md, CLAUDE.md, `.bits/srs/`.
- `06_PLAN`: GOVERNANCE.md, PROVENANCE.md, `.github/CODEOWNERS`.
- `11_COMMIT`: `.bits/` registry, context, queue, tests, output and
  `.github/` rulesets/workflows; JSON metadata inherits the payload stage.

The build directive authorizes compiler-required source fixes and regression
tests in native paths (logical 07_BUILD and 08_TEST), plus tooling under
11_COMMIT. Private CNWB, deployment and signing-key code remain out of scope.
CK, CAPS, and CKS results remain pending; the review target is B+/75.
Missing application lockfile, compiler/test dependencies and configuration
are existing scaffold blockers. This dispatch repairs them; do not conceal blockers or invent build output.
The governance smoke suite uses Python unittest and PyYAML; npm checks
remain required for a real build and are reported separately.
