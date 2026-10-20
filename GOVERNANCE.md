<!--
# ─── CGRF Header ───────────────────────────────────────────────
# File: GOVERNANCE.md
# Stage: 06_PLAN
# SRS: SRS-CN-INTELLIGENCE-GOVERNANCE-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-GOVERNANCE-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: .github/rulesets/default-branch.json, PROVENANCE.md
# EnumType: Doc
# EnumEdges: DEPENDS_ON .github/rulesets/default-branch.json; DEPENDS_ON PROVENANCE.md
# DAG Node: none
# Intent: Assign guild accountability and explicit admin activation requirements.
# ───────────────────────────────────────────────────────────────
-->

# Intelligence Guild governance

Owner: Citadel Nexus Inc. Guildmaster: **Oracle** (GitLab user `oracle`).
Datadog team handle: `guild-intelligence`. The operator confirmed these
GitHub identities through that team's links:

- Guildmaster code owner: [@citadel-nexus/guild-intelligence](https://github.com/orgs/citadel-nexus/teams/guild-intelligence).
- Oracle's automation identity and expected governance actor:
  [oracle-intelligence-guildmaster](https://github.com/apps/oracle-intelligence-guildmaster)
  (GitHub App).

GitHub Apps cannot be CODEOWNERS; the confirmed team owns code on Oracle's
behalf.

## Charter and scope

The guild owns threat watch through Nemesis, Suricata and Wazuh, governance
audits, and memory systems. This public repository carries public-safe
contracts and automation; private enforcement logic, credentials and
production operations remain outside the staging bootstrap.

## Decisions and approvals

The guildmaster is accountable for technical direction, ownership and risk
acceptance. Contributors propose a focused SRS-linked PR with tests and a
risk/rollback note. Require two independent approvals, including a code
owner; security-affecting work also requires the guildmaster or an explicitly
recorded delegate. Authors cannot approve their own work. New pushes dismiss
stale reviews, the latest pusher cannot provide the final required approval,
and review threads must be resolved. Governance/policy changes follow these
same rules. Record the decision and any delegation in the PR.

`.github/CODEOWNERS` routes guildmaster ownership through the confirmed
`@citadel-nexus/guild-intelligence` team. The
`oracle-intelligence-guildmaster` app is Oracle's automation identity,
not an individual reviewer or a substitute for required team reviews.
The SDK team remains a co-owner of `src/index.ts`; GitHub accepts approval
from either listed owner, so the additional guildmaster requirement is a
human review policy.

Escalate cross-guild decisions, ownership conflicts, disputed risk acceptance
or unavailable/conflicted guildmaster approvals to the **guildmasters group**
through the established internal review channel. Record its decision on the
PR before merging; do not invent a public team slug or bypass protection.
Vulnerabilities go to `security@citadel-nexus.com`, not public issues.

## Default-branch protection: administrator activation required

The verified default branch is `main`. `.github/rulesets/default-branch.json`
is a GitHub branch-ruleset import document, **not automatically applied
configuration**. It targets `~DEFAULT_BRANCH` and ships with enforcement
`disabled` for staging. The JSON's `name` records
`oracle-intelligence-guildmaster` as the expected governance automation actor;
its companion `.cgrf.yaml` also records the actor and code-owner team as
structured metadata. GitHub's branch-ruleset schema has no generic
`expected_actor` constraint. This is descriptive identity metadata, not actor
enforcement or a bypass grant. The app remains subject to required reviews,
signed commits and status checks; `bypass_actors` remains empty. Required
status-check publisher IDs continue to identify GitHub Actions, which runs
the build and attestation workflow, rather than Oracle's app.

An admin must:

1. Ensure the confirmed guild team and SDK co-owner team have the visibility
   and repository write access required by CODEOWNERS. Inspect GitHub's
   CODEOWNERS diagnostics after the file is on the base branch.
2. Repair the existing npm scaffold in a separate SRS: a reproducible lockfile,
   declared compiler/test/lint tools, TypeScript/ESLint configs and runnable tests.
   This PR does not relax checks to conceal those failures.
3. In Settings → Rules → Rulesets, import the JSON, review it, and set
   enforcement to **Active**. Require two approvals, code-owner review,
   resolved threads, stale-review dismissal, approval after the latest push,
   signed commits, and block deletion and force pushes. No bypass actors
   are proposed. Confirm organization policy/plan supports these rules.
4. Require the exact GitHub Actions job contexts `build` (existing CI),
   `Governance policy`, and `Build artifact` (new workflow), bound to the
   GitHub Actions integration. Require the branch to be up to date. Bootstrap
   this workflow on the base branch and observe PR runs before enabling the
   checks, to avoid requiring a context that has never run.
5. Confirm signed commit identities are trusted by GitHub and choose a merge
   method that preserves verified signatures. A local signature alone does
   not prove GitHub considers it verified.
6. Permit the pinned Actions and job-scoped `id-token: write` and
   `attestations: write` for the signing job, subject to organization policy.
   Verify repository visibility/plan supports GitHub artifact attestations.
   No stored signing key or new secret is required. Run the verification
   checks in `PROVENANCE.md` after the first successful trusted build.

`Attest artifact` runs only after a default-branch push, so it is **not** a
required PR check. Existing CodeQL/secret scans do not run on PRs and are not
listed as required contexts here. If the default branch changes, update
workflow event filters as well as the verification examples. Settings remain
unchanged by this PR; merging files alone does not enforce protection.

## Rollback

Revert this SRS's changes through a reviewed PR. An admin separately reverts
any subsequently enabled ruleset if necessary. Previously issued attestations
remain verifiable statements about their original digests; a revert does not
revoke them. No production deployment or package publication is added.
