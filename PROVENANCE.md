<!--
# ─── CGRF Header ───────────────────────────────────────────────
# File: PROVENANCE.md
# Stage: 06_PLAN
# SRS: SRS-CN-INTELLIGENCE-GOVERNANCE-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-GOVERNANCE-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: .github/workflows/build-provenance.yml, GOVERNANCE.md
# EnumType: Doc
# EnumEdges: DEPENDS_ON .github/workflows/build-provenance.yml; DEPENDS_ON GOVERNANCE.md
# DAG Node: none
# Intent: Enable consumers to verify signed artifact identity and digest without confusing configuration with evidence.
# ───────────────────────────────────────────────────────────────
-->

# Signed build provenance

`.github/workflows/build-provenance.yml` runs governance policy checks and
builds the existing Node 20 npm project on PRs and pushes to `main`.
`npm ci` and `npm run build` must succeed before packaging. The tarball
contains only `dist/`, `package.json`, `LICENSE` and `README.md`, not the
checkout, environment files, node_modules, or governance output. This is a
compiled distribution archive, not an npm release or container image.
Existing package/container publication workflows are outside this SRS and
are not covered by these attestations.

The build job has only `contents: read`. A separate GitHub-hosted signing
job downloads the exact artifact ID from that build in the same run and
uses `actions/attest-build-provenance` to issue a signed in-toto statement
with SLSA provenance v1 (`https://slsa.dev/provenance/v1`). GitHub OIDC and
Sigstore bind the tarball's SHA-256 digest to the repository/workflow and
source commit. This signed digest is the artifact signature; there is no
separate stored private key or unsigned checksum masquerading as a signature.
The signer does not check out code or execute the artifact. It runs only
for pushes to this repository's `main`, never for PRs, forks, tags or manual
dispatches. Actions are pinned to immutable commits.

No SLSA assurance level is claimed. Provenance proves identity and digest,
not that code is vulnerability-free or that tests passed. The existing `build`
CI job remains the separate lint/test gate enforced by branch protection.
New workflow files do not retrofit signatures onto older artifacts.

## Current readiness and administrator work

The checkout lacks a lockfile, declared TypeScript/Vitest toolchain and
TypeScript/ESLint configuration. The existing npm install/test/lint/build
checks fail. The workflow intentionally fails closed until a separate
build-toolchain dispatch repairs that scaffold; it cannot issue a real
attestation yet. No GitHub-hosted signing run was performed in this session.
See `GOVERNANCE.md` for the identity, Actions permissions and ruleset settings
an administrator must enable. There are no deployment steps in this workflow.

## Verify a trusted artifact

Use a current GitHub CLI with `gh attestation verify` and GitHub authentication
that can read this repo and its Actions artifacts. Choose a successful
**Build provenance** push run on `main` and obtain its full source commit SHA
from the trusted PR/commit record. Do not choose identity constraints based
only on untrusted metadata shipped with a downloaded file.

```bash
set -euo pipefail
REPO=citadel-nexus/guild-intelligence
RUN_ID='<successful push run id>'
EXPECTED_SHA='<full trusted commit SHA>'
DOWNLOAD_DIR="$(mktemp -d)"
gh run view "$RUN_ID" --repo "$REPO" --json event,headBranch,headSha,conclusion
# Confirm push, main, EXPECTED_SHA and success before continuing.
gh run download "$RUN_ID" --repo "$REPO" \
  --name "guild-intelligence-$EXPECTED_SHA" --dir "$DOWNLOAD_DIR"
ARTIFACT="$DOWNLOAD_DIR/guild-intelligence-$EXPECTED_SHA.tar.gz"
gh attestation verify "$ARTIFACT" --repo "$REPO" \
  --signer-workflow "$REPO/.github/workflows/build-provenance.yml" \
  --source-ref refs/heads/main --source-digest "$EXPECTED_SHA" \
  --predicate-type https://slsa.dev/provenance/v1 --deny-self-hosted-runners
```

Require exit status 0 before extracting/using the tarball. The verifier checks
the signed statement, trusted certificate/identity and actual file digest;
checking the filename or running `sha256sum` alone is insufficient.

The same run retains a `provenance-<SHA>` artifact containing the Sigstore
JSONL bundle for 30 days (repository limits may shorten this). Download it
before expiration and keep it with the tarball for longer retention:

```bash
gh run download "$RUN_ID" --repo "$REPO" \
  --name "provenance-$EXPECTED_SHA" --dir "$DOWNLOAD_DIR/bundle"
# Set BUNDLE to the downloaded JSONL file, preserving its contents.
BUNDLE='<path to downloaded JSONL bundle>'
gh attestation verify "$ARTIFACT" --bundle "$BUNDLE" --repo "$REPO" \
  --signer-workflow "$REPO/.github/workflows/build-provenance.yml" \
  --source-ref refs/heads/main --source-digest "$EXPECTED_SHA" \
  --predicate-type https://slsa.dev/provenance/v1 --deny-self-hosted-runners
```

Bundle verification avoids fetching the attestation from GitHub, but trust
root retrieval may still require network access. Test tamper rejection on a
copy after the positive verification succeeds:

```bash
cp "$ARTIFACT" "$ARTIFACT.tampered"
printf '\nmodified\n' >> "$ARTIFACT.tampered"
if gh attestation verify "$ARTIFACT.tampered" --bundle "$BUNDLE" --repo "$REPO" \
  --signer-workflow "$REPO/.github/workflows/build-provenance.yml" \
  --source-ref refs/heads/main --source-digest "$EXPECTED_SHA" \
  --predicate-type https://slsa.dev/provenance/v1 --deny-self-hosted-runners; then
  echo 'FAIL: tampered artifact accepted'
  exit 1
fi
echo 'PASS: tampered artifact rejected'
```

Repeat verification with an incorrect source SHA or signer workflow and
require failure. These hosted acceptance checks remain pending until a real
trusted build is available; local policy tests do not prove signing works.
