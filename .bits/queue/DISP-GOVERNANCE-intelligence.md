<!--
# ─── CGRF Header ───────────────────────────────────────────────
# File: .bits/queue/DISP-GOVERNANCE-intelligence.md
# Stage: 11_COMMIT
# SRS: SRS-CN-INTELLIGENCE-GOVERNANCE-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-GOVERNANCE-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: .bits/srs/SRS-CN-INTELLIGENCE-GOVERNANCE-001.md
# EnumType: Doc
# EnumEdges: DEPENDS_ON .bits/srs/SRS-CN-INTELLIGENCE-GOVERNANCE-001.md
# DAG Node: none
# Intent: Record the exact staging authorization and executable acceptance gates.
# ───────────────────────────────────────────────────────────────
-->

# DISP-GOVERNANCE-intelligence

- srs: SRS-CN-INTELLIGENCE-GOVERNANCE-001
- guild: intelligence
- champion: Oracle (GitLab `oracle`)
- seat: BITS-CODEGEN
- mode: staging
- status: in_progress
- brief: .bits/srs/SRS-CN-INTELLIGENCE-GOVERNANCE-001.md
- authorization_source: authenticated operator directive in this Bits AI session, 2026-10-20
- operator: Dmitry Richard, mr.nobody@citadel-nexus.com

## Authorization record

The operator's directive, "create those", explicitly authorizes creating the
missing local SRS registry entry, SRS document and this dispatch, plus missing
prerequisite governance files for this work. The follow-up directive names
SRS-CN-INTELLIGENCE-GOVERNANCE-001 and DISP-GOVERNANCE-intelligence with
status `in_progress`. This record represents local staging authorization;
it does not claim a VCC database update or an external USO approval.

Bounds: one branch/PR for this SRS; no production, deploy, push to main,
GitHub settings changes or secrets. Follow CGRF, commit and test conventions.

## Task table

| Phase | Task | Gate |
| --- | --- | --- |
| A | Bootstrap prerequisites, charter and ownership | governance tests |
| B | Disabled importable ruleset and isolated signed-provenance workflow | workflow/packaging tests |
| C | Verification docs, memory payload, report and PR metadata | full smoke suite |

## Smoke test

```bash
python -m unittest discover -s .bits/tests -p 'test_governance.py' -v && echo 'PASS: governance smoke' || { echo 'FAIL: governance smoke'; exit 1; }
```

Requires Python 3.11+ and PyYAML 6.0.3. Run `npm ci`, `npm test`,
`npm run lint`, and `npm run build` separately; record each existing blocker.
Do not emit a signing attestation until a real build succeeds on GitHub.

## Memory Brief

The supplied conversation requests guild ownership governance and signed
provenance. No USO_MCP Memory Brief or prior-art memory payload was supplied;
none is invented or recalled for this bootstrap. Preserve the queued
living-world dispatch. Hand off toolchain repair to a separate dispatch.
