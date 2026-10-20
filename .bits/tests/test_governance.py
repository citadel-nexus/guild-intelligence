# ─── CGRF Header ───────────────────────────────────────────────
# File: .bits/tests/test_governance.py
# Stage: 11_COMMIT
# SRS: SRS-CN-INTELLIGENCE-GOVERNANCE-001
# CAPS: pending
# CK: pending
# Dispatch: DISP-GOVERNANCE-intelligence
# Seat: BITS-CODEGEN
# Owner: Citadel Nexus Inc.
# Created: 2026-10-20
# Depends: .github/workflows/build-provenance.yml, .github/rulesets/default-branch.json
# EnumType: Test
# EnumEdges: DEPENDS_ON .github/workflows/build-provenance.yml; DEPENDS_ON .github/rulesets/default-branch.json
# DAG Node: none
# Intent: Exercise signing authorization, archive inclusion, staged protections and governance evidence consistency.
# ───────────────────────────────────────────────────────────────

"""Validate staging governance, signing trust boundaries, and archive contents."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/build-provenance.yml"
SRS = "SRS-CN-INTELLIGENCE-GOVERNANCE-001"
DISPATCH = "DISP-GOVERNANCE-intelligence"


def workflow() -> dict:
    """Load GitHub's YAML without YAML 1.1 boolean coercion of `on`."""
    return yaml.load(WORKFLOW.read_text(), Loader=yaml.BaseLoader)


def signing_policy(document: dict) -> None:
    """Reject configuration that widens signing authority or executes build code."""
    assert set(document["on"]) == {"push", "pull_request"}
    for event in document["on"].values():
        assert event["branches"] == ["main"]
    assert document["permissions"] == {"contents": "read"}
    jobs = document["jobs"]
    assert jobs["build"]["needs"] == "policy"
    assert jobs["attest"]["needs"] == "build"
    assert jobs["attest"]["if"] == (
        "github.event_name == 'push' && "
        "github.repository == 'citadel-nexus/guild-intelligence' && "
        "github.ref == 'refs/heads/main'"
    )
    for name, job in jobs.items():
        assert job["runs-on"] == "ubuntu-latest"
        assert "secrets" not in job
        if name != "attest":
            assert job.get("permissions", document["permissions"]) == {"contents": "read"}
        for step in job["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"[\w-]+/[\w-]+@[0-9a-f]{40}", step["uses"])
                if step["uses"].startswith("actions/checkout@"):
                    assert step["with"]["persist-credentials"] == "false"
    signer = jobs["attest"]
    assert signer["permissions"] == {
        "contents": "read", "actions": "read", "id-token": "write", "attestations": "write"
    }
    # No shell, checkout, local actions, or arbitrary repository code in the signer.
    assert [step["uses"].split("@")[0] for step in signer["steps"]] == [
        "actions/download-artifact", "actions/attest-build-provenance", "actions/upload-artifact"
    ]
    assert all("run" not in step for step in signer["steps"])
    download, attest, bundle = signer["steps"]
    assert download["with"]["artifact-ids"] == "${{ needs.build.outputs.artifact-id }}"
    assert "run-id" not in download["with"]
    assert "repository" not in download["with"]
    assert attest["with"]["subject-path"] == (
        "${{ runner.temp }}/artifact/guild-intelligence-${{ github.sha }}.tar.gz"
    )
    assert bundle["with"]["path"] == "${{ steps.attest.outputs.bundle-path }}"
    assert bundle["with"]["if-no-files-found"] == "error"


class GovernanceTests(unittest.TestCase):
    def test_ruleset_is_staged_and_targets_default_branch(self) -> None:
        ruleset = json.loads((ROOT / ".github/rulesets/default-branch.json").read_text())
        self.assertEqual(ruleset["enforcement"], "disabled")
        self.assertEqual(ruleset["bypass_actors"], [])
        self.assertEqual(ruleset["conditions"]["ref_name"], {"include": ["~DEFAULT_BRANCH"], "exclude": []})
        rules = {rule["type"]: rule.get("parameters", {}) for rule in ruleset["rules"]}
        self.assertTrue({"required_signatures", "non_fast_forward", "deletion"} <= rules.keys())
        reviews = rules["pull_request"]
        self.assertGreaterEqual(reviews["required_approving_review_count"], 2)
        for requirement in ("require_code_owner_review", "dismiss_stale_reviews_on_push",
                            "require_last_push_approval", "required_review_thread_resolution"):
            self.assertIs(reviews[requirement], True)
        self.assertIs(rules["required_status_checks"]["strict_required_status_checks_policy"], True)

    def test_required_contexts_exist_on_prs(self) -> None:
        contexts = set()
        for name in ("ci.yml", "build-provenance.yml"):
            document = yaml.load((ROOT / ".github/workflows" / name).read_text(), Loader=yaml.BaseLoader)
            self.assertIn("main", document["on"]["pull_request"]["branches"])
            for key, job in document["jobs"].items():
                if "if" not in job:
                    contexts.add(job.get("name", key))
        ruleset = json.loads((ROOT / ".github/rulesets/default-branch.json").read_text())
        checks = next(rule["parameters"]["required_status_checks"] for rule in ruleset["rules"]
                      if rule["type"] == "required_status_checks")
        self.assertEqual({check["context"] for check in checks}, {"build", "Governance policy", "Build artifact"})
        self.assertTrue({check["context"] for check in checks} <= contexts)
        self.assertTrue(all(check["integration_id"] == 15368 for check in checks))

    def test_ownership_does_not_invent_a_github_identity(self) -> None:
        owners = (ROOT / ".github/CODEOWNERS").read_text()
        active = [line for line in owners.splitlines() if line and not line.startswith("#")]
        self.assertEqual(active[0], "* @citadel-nexus/guild-intelligence-leads")
        self.assertIn("@citadel-nexus/sdk-core", active[1])
        self.assertIn("@citadel-nexus/guild-intelligence-leads", active[1])
        self.assertNotRegex("\n".join(active), r"(?:^|\s)@oracle(?:\s|$)")
        charter = (ROOT / "GOVERNANCE.md").read_text()
        for term in ("Oracle", "Nemesis", "Suricata", "Wazuh", "memory systems", "guildmasters group"):
            self.assertIn(term, charter)

    def test_operator_authorization_and_registered_srs(self) -> None:
        registry = yaml.safe_load((ROOT / ".bits/srs_registry.yml").read_text())
        self.assertEqual(registry[SRS]["dispatch"], DISPATCH)
        self.assertIn("SRS-CN-INTELLIGENCE-LIVINGWORLD-001", registry)
        dispatch = (ROOT / f".bits/queue/{DISPATCH}.md").read_text()
        for text in ("status: in_progress", "authorization_source:", "mr.nobody@citadel-nexus.com", "staging"):
            self.assertIn(text, dispatch)

    def test_signing_trust_boundary(self) -> None:
        signing_policy(workflow())

    def test_rejects_signing_from_prs_or_other_repos(self) -> None:
        for guard in ("true", "github.event_name == 'pull_request'", "github.ref == 'refs/heads/main'"):
            document = workflow()
            document["jobs"]["attest"]["if"] = guard
            with self.subTest(guard=guard), self.assertRaises(AssertionError):
                signing_policy(document)

    def test_rejects_privileged_build_or_extra_trigger(self) -> None:
        document = workflow()
        document["jobs"]["build"]["permissions"] = {"contents": "read", "id-token": "write"}
        with self.assertRaises(AssertionError):
            signing_policy(document)
        document = workflow()
        document["on"]["pull_request_target"] = {}
        with self.assertRaises(AssertionError):
            signing_policy(document)

    def test_rejects_artifact_substitution_and_signer_execution(self) -> None:
        for mutation in ("different_run", "different_artifact", "execute"):
            document = workflow()
            steps = document["jobs"]["attest"]["steps"]
            if mutation == "different_run":
                steps[0]["with"]["run-id"] = "123"
            elif mutation == "different_artifact":
                steps[0]["with"]["artifact-ids"] = "123"
            else:
                steps[1]["run"] = "npm run build"
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                signing_policy(document)

    def test_build_is_required_before_upload(self) -> None:
        job = workflow()["jobs"]["build"]
        steps = job["steps"]
        install = next(i for i, step in enumerate(steps) if step.get("run") == "npm ci")
        build = next(i for i, step in enumerate(steps) if step.get("run") == "npm run build")
        package = next(i for i, step in enumerate(steps) if step.get("id") == "package")
        upload = next(i for i, step in enumerate(steps) if step.get("id") == "upload")
        self.assertTrue(install < build < package < upload)
        self.assertFalse(any("continue-on-error" in step or "if" in step for step in steps))
        self.assertEqual(job["outputs"]["artifact-id"], "${{ steps.upload.outputs.artifact-id }}")
        self.assertEqual(steps[upload]["with"]["if-no-files-found"], "error")
        self.assertEqual(steps[upload]["with"]["path"],
                         "${{ runner.temp }}/guild-intelligence-${{ github.sha }}.tar.gz")

    def test_package_contains_only_distribution_and_public_metadata(self) -> None:
        script = next(step["run"] for step in workflow()["jobs"]["build"]["steps"]
                      if step.get("id") == "package")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, content in {"dist/index.js": "export {};", "package.json": "{}", "LICENSE": "License",
                                  "README.md": "Public docs", ".env": "PRIVATE_TEST_VALUE",
                                  "node_modules/local/index.js": "excluded", ".bits/internal.txt": "excluded"}.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            output = root / "output"
            output.mkdir()
            result = subprocess.run(["bash", "-c", script], cwd=root, capture_output=True, text=True,
                                    env={**os.environ, "RUNNER_TEMP": str(output), "BUILD_SHA": "a" * 40})
            self.assertEqual(result.returncode, 0, result.stderr)
            with tarfile.open(output / f"guild-intelligence-{'a' * 40}.tar.gz") as archive:
                names = set(archive.getnames())
                self.assertEqual(names, {"dist", "dist/index.js", "package.json", "LICENSE", "README.md"})
                self.assertEqual(archive.extractfile("dist/index.js").read(), b"export {};")

    def test_package_rejects_missing_or_empty_build(self) -> None:
        script = next(step["run"] for step in workflow()["jobs"]["build"]["steps"]
                      if step.get("id") == "package")
        for empty in (False, True):
            with self.subTest(empty=empty), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                if empty:
                    (root / "dist").mkdir()
                result = subprocess.run(["bash", "-c", script], cwd=root, capture_output=True,
                                        env={**os.environ, "RUNNER_TEMP": directory, "BUILD_SHA": "a" * 40})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(list(root.glob("*.tar.gz")), [])

    def test_memory_and_cgrf_headers_are_consistent(self) -> None:
        payload = json.loads((ROOT / f".bits/out/{DISPATCH}/memory.json").read_text())
        vectors = payload["vectors"]
        summary = payload["summary"]
        for kind in "ABC":
            self.assertEqual(summary[f"type_{kind.lower()}_count"], sum(v["type"] == kind for v in vectors))
        self.assertTrue(summary["ioo_compliance"])
        self.assertEqual(summary["dkg_orphans"], 0)
        edges = {(v["source"], v["edge_type"], v["target"]) for v in vectors if v["type"] == "B"}
        for item in (v for v in vectors if v["type"] == "A"):
            path = ROOT / item["file_path"]
            self.assertTrue(path.is_file())
            self.assertEqual(item["lines"], len(path.read_text().splitlines()))
            for field in ("intent_statement", "objective_id", "outcome"):
                self.assertTrue(item[field])
            self.assertIs(item["supersedes"], False)
            self.assertEqual(item["ck_stamp"], "pending")
            self.assertEqual(item["caps_grade"], "pending")
            if path.suffix == ".json":
                header = path.with_suffix(".cgrf.yaml").read_text()
                declared = yaml.safe_load(header)["artifact_enum_edges"]
            else:
                header = path.read_text()
                self.assertIn(f"# File: {item['file_path']}\n", header)
                self.assertIn(f"# Stage: {item['cket_stage']}\n", header)
                self.assertIn(f"# Intent: {item['intent_statement']}\n", header)
                declared = re.search(r"^# EnumEdges: (.+)$", header, re.MULTILINE).group(1).split("; ")
            self.assertIn("# Owner: Citadel Nexus Inc.\n", header)
            self.assertIn(f"# SRS: {SRS}\n", header)
            expected = {(item["file_path"], *edge.split(" ", 1)) for edge in declared}
            actual = {edge for edge in edges if edge[0] == item["file_path"]}
            self.assertEqual(actual, expected)
            self.assertTrue(actual)


if __name__ == "__main__":
    unittest.main()
