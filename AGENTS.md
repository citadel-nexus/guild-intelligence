<!--
# ─── CGRF Header ───────────────────────────────────────────────
# File: AGENTS.md
# Stage: 04_HYPOTHESIZE
# SRS: SRS-CN-INTELLIGENCE-GOVERNANCE-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-GOVERNANCE-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: none
# EnumType: ConfigDoc
# EnumEdges: DEPENDS_ON SRS-CN-INTELLIGENCE-GOVERNANCE-001
# DAG Node: none
# Intent: Define the operator-authorized staging bootstrap without granting future authority.
# ───────────────────────────────────────────────────────────────
-->

# Intelligence Guild agent conventions

Owner: Citadel Nexus Inc. Guildmaster: Oracle (GitLab `oracle`).
Datadog team: `guild-intelligence`. This checkout is the public
`citadel-nexus/guild-intelligence` repository, not the CNWB monorepo.

Read `CLAUDE.md`, `.bits/context.md`, `.bits/srs_registry.yml`, the SRS,
and its dispatch before implementation. Preserve unrelated dispatches.

## Scoped governance bootstrap

The authenticated operator Dmitry Richard (`mr.nobody@citadel-nexus.com`)
authorized creating the missing prerequisites for
`SRS-CN-INTELLIGENCE-GOVERNANCE-001` in the 2026-10-20 session directive.
This is a staging-only exception for `DISP-GOVERNANCE-intelligence`;
it does not grant authority for future SRS work or production actions.
The directive is recorded in that dispatch. No prior local bootstrap
exception existed in this checkout.

Use CGRF headers (HTML comments in Markdown, native comments elsewhere;
JSON has a sibling `.cgrf.yaml`). Use logical CKET stages as mapped in
`.bits/context.md`; GitHub discovery paths remain in their native locations.
Do not edit pre-existing CGRF-governed files outside this dispatch.
Never touch protected CNWB code, production, secrets, or GitHub settings.

Use one branch/PR for this SRS. Follow the global conventional commit
format and include Phase, Files, Smoke, SRS, Dispatch, and CK footers.
Keep configured signing enabled. Workflow actions must be pinned to
commit SHAs. Test the trust boundary and artifact packaging, and disclose
existing application-toolchain failures without claiming a signed build.
