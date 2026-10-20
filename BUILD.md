<!--
# ─── CGRF Header ───────────────────────────────────────────────
# File: BUILD.md
# Stage: 06_PLAN
# SRS: SRS-CN-INTELLIGENCE-BUILD-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-BUILD-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: .github/workflows/lockfile-refresh.yml, .github/rulesets/default-branch.json, PROVENANCE.md
# EnumType: Doc
# EnumEdges: DEPENDS_ON .github/workflows/lockfile-refresh.yml; DEPENDS_ON .github/rulesets/default-branch.json; DEPENDS_ON PROVENANCE.md
# DAG Node: none
# Intent: Explain the gated hosted lockfile flow and required administrator activation.
# ───────────────────────────────────────────────────────────────
-->

# Intelligence Guild build and lockfile flow

SRS: SRS-CN-INTELLIGENCE-BUILD-001. Dispatch: DISP-BUILD-intelligence.
Use Node 22.17.0 from `.nvmrc`; package engines enforce the same pin.

## Generate the real lockfile on GitHub

After this workflow is merged, an authorized maintainer runs **Lockfile refresh**
from Actions using **Run workflow**, selecting the default branch. It is
`workflow_dispatch` only and refuses other refs and fork repositories.
It uses the checked-out `.nvmrc`, routes `@citadel-guilds` to GitHub Packages,
and uses the job's `GITHUB_TOKEN` with `packages: read` for the SDK. Unscoped
NATS and the public dev tools resolve through npmjs.org. No credential value
is stored in repository configuration or the lockfile.

The package owner must grant this repository Actions access to the SDK package
and make the requested version available. If the approved SDK is hosted
elsewhere, an admin must first adapt the scoped registry configuration. An
administrator-managed read-only secret, `GUILD_PACKAGES_READ_TOKEN`, is wired
into CI/provenance installs and CodeQL autobuild so these jobs retain their
existing token permissions. Provisioning it with access to the SDK is an admin
TODO; no secret is created or changed here. Fork PRs do not receive this secret
and cannot install a private SDK without an approved package-access strategy.
The existing release job uses its GITHUB_TOKEN, which already has package
write permission, for installation as well as publication. The manual refresh
uses only its package-read GITHUB_TOKEN and does not require this optional
credential if the package grants this repository Actions read access.

The read-only refresh job runs:

```bash
npm install --package-lock-only --ignore-scripts
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```

Only after every command succeeds does it record CGRF/memory evidence and
upload the real lockfile plus those metadata files. A separate publisher job
has only `contents: write` and `pull-requests: write`, downloads that exact
artifact ID, and opens/updates **bits/lockfile-refresh** against the default
branch. It never writes to main and never auto-merges. If main has advanced
since validation, publishing fails; rerun the manual workflow. Concurrent
refresh runs are serialized. Every successful run records a new validation
event, so a repeat run can update PR evidence even when lockfile bytes are
unchanged.
Reserve this bot branch for this workflow; do not place human work on it.

The publisher requests GitHub-signed commits and stages only package-lock.json,
package-lock.cgrf.yaml and the build dispatch memory payload. An admin must
enable **Allow GitHub Actions to create and approve pull requests** if disabled
by repository/organization policy. No setting is changed here. GITHUB_TOKEN
PRs normally do not trigger other PR workflows automatically. A maintainer
must arrange a human-triggered PR event (for example close/reopen) or an
approved GitHub App token before requiring the resulting PR's checks to pass;
do not disable required checks. No App credential is provisioned here.

## Administrator prerequisites

- Apply `.github/rulesets/default-branch.json` after reviewing its disabled
  staging state and observing the required contexts. Enable protection, code
  owner reviews, required checks and signed commits; confirm bot signatures.
- Grant this repository package read access and permit the pinned Actions.
  Ordinary build jobs must also be able to resolve any private SDK package.
- Permit `attestations: write` and `id-token: write` for the isolated signer.
  Keep the build and verification jobs read-only. The verifier uses bundled
  provenance and may need network access to obtain Sigstore trust roots.
- Enable workflow PR creation as described above. No production deploy or
  package publication is part of the lockfile workflow.

## Provenance verification

The **Build provenance** workflow signs only successful main push builds.
Its separate **Verify attestation** job downloads the exact build and signed
bundle IDs from the same run, verifies the real artifact, and then requires
rejection of a tampered copy and a wrong signer workflow identity. All three
checks must behave as expected for that job to succeed. It does not run code
from the archive or put shell commands in the privileged signer.
See `PROVENANCE.md` for consumer verification commands and trust constraints.

## Local validation and current limits

With a generated lockfile and approved registry credentials, run the six
commands above (skip lockfile generation for a normal clean build), then:

```bash
python -m unittest discover -s .bits/tests -p 'test_*.py' -v
```

In this sandbox, package downloads are restricted and SDK/NATS/Vitest are not
cached. Offline npm ci, full typecheck, application tests and build remain
blocked; diagnostic lint uses exact preinstalled tool versions. The hosted
refresh and attestation checks have not been run here. No placeholder lockfile
or runtime dependency substitute is used. The dispatch remains in_progress.
