<!--
# ─── CGRF Header ───────────────────────────────────────────────
# File: .bits/srs/SRS-CN-INTELLIGENCE-GOVERNANCE-001.md
# Stage: 04_HYPOTHESIZE
# SRS: SRS-CN-INTELLIGENCE-GOVERNANCE-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-GOVERNANCE-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: .bits/srs_registry.yml
# EnumType: Doc
# EnumEdges: DEPENDS_ON .bits/srs_registry.yml
# DAG Node: none
# Intent: Make the operator governance directive reviewable as a bounded SRS.
# ───────────────────────────────────────────────────────────────
-->

# Intelligence Guild ownership governance and signed build provenance

SRS: SRS-CN-INTELLIGENCE-GOVERNANCE-001
Dispatch: DISP-GOVERNANCE-intelligence
Owner: Citadel Nexus Inc. Guildmaster: Oracle (GitLab `oracle`).

## Requirements and acceptance

1. Preserve SDK co-ownership and identify the guildmaster's GitHub ownership
   route without assuming a GitLab username is a GitHub identity.
2. Document charter, scope, approvals and guildmasters-group escalation.
3. Supply an importable, initially disabled default-branch ruleset requiring
   two reviews, code-owner approval, signed commits and required PR checks.
   Explain the admin activation work; make no settings changes.
4. Build the existing npm project and archive only build output and public
   package metadata. Fail closed if build prerequisites are missing.
5. Sign SLSA v1 provenance with GitHub artifact attestations and Sigstore
   keyless identity for successful default-branch push builds only. Separate
   the unprivileged build from signing; PRs never receive signing permission.
6. Document verification of repository, workflow, source ref, source SHA,
   predicate type and artifact digest, plus a tampering rejection check.
7. Add automated governance/workflow/packaging tests and the three-type
   memory payload. Report scaffold failures and unexecuted hosted checks.

## Bounds

Staging only; one branch/PR. No production, deployment, secrets, settings
mutations, direct publishing, private-stack changes or unrelated SRS work.
This specification transcribes the operator directive; it is not a new USO
blueprint. CKS review target B+/75; computed CKS/CAPS/CK remain pending.
Numeric CAPS minimum requires guildmaster confirmation, not an invented score.
