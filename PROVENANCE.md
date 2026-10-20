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
builds the Node 22.17.0 npm project on PRs and pushes to `main`.
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

## Automated positive and negative verification

After signing, a separate read-only **Verify attestation** job downloads the
build artifact and signed bundle by their exact same-run artifact IDs. It
runs `gh attestation verify` with repository, signer workflow, source ref,
source SHA, SLSA v1 predicate and hosted-runner constraints. A valid artifact
must verify first. The job then appends bytes to a copy of the artifact and
requires verification to fail, and verifies the original with a deliberately
wrong signer workflow identity and requires that to fail too. Unexpected
acceptance of either negative case fails the job. No artifact is executed.

The verifier inherits only `contents: read`; it has no OIDC or write token.
The signer still has no shell or checkout steps. The job is a post-merge gate
and is not a required PR context. These hosted checks remain unexecuted in
this sandbox; local tests exercise their control flow, not real signatures.

## Current readiness and administrator work

The staging build repair declares the compiler, lint and test tools, pins
Node 22.17.0, adds strict TypeScript/ESLint configuration, and repairs the
malformed NATS source. The workflow now requires lint, typecheck and tests
before compilation and packaging. It still cannot issue an attestation until
all gates pass with resolved runtime dependencies.

Dependency resolution is currently blocked: this sandbox has no SDK/NATS/
Vitest cache and outbound package downloads are restricted. No generated
lockfile is available yet, so clean npm ci, full typechecking, application
tests and a real distribution build remain blocked. Local lint uses the exact
declared preinstalled compiler/linter packages for diagnostics, not a claimed
clean install. No hosted signing run has been performed. See
`BUILD.md` for the manual **Lockfile refresh** workflow and its package/PR
permission prerequisites, and `.bits/queue/DISP-BUILD-intelligence.md` for
the authorized follow-up.

The operator-confirmed guildmaster owner is `@citadel-nexus/guild-intelligence`;
Oracle's automation identity and expected governance actor is the GitHub App
`oracle-intelligence-guildmaster`. The ruleset records this actor descriptively;
it grants no bypass. Provenance still uses the GitHub Actions workflow's OIDC
identity, so the verification constraints below must not be replaced with the
app slug. See `GOVERNANCE.md` for Actions permissions and ruleset settings an
administrator must enable. There are no deployment steps in this workflow.

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
