import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tooling" / "build_release.py"
PACK_ID = "review-draft-contracts"
GUIDE_ID = "lawyeah-contracts-guide"
ATOMIC_ID = "lawyeah-contracts-review"


class ReleaseBuilderTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary_directory.name)
        self.output = self.repo / "first.zip"
        self.second_output = self.repo / "second.zip"

        (self.repo / "catalog").mkdir()
        (self.repo / "packs" / PACK_ID / "skills" / GUIDE_ID).mkdir(parents=True)
        (self.repo / "packs" / PACK_ID / "skills" / ATOMIC_ID / "references").mkdir(
            parents=True
        )
        (self.repo / "packs" / PACK_ID / "skills" / ATOMIC_ID / "assets" / "templates").mkdir(
            parents=True
        )
        (self.repo / "packs" / PACK_ID / "tests").mkdir()
        (self.repo / "packs" / PACK_ID / "skills" / GUIDE_ID / "SKILL.md").write_text(
            f"---\nname: {GUIDE_ID}\n"
            "description: Use when the user asks what the contracts pack can do.\n"
            "---\n\n# Contracts guide\n",
            encoding="utf-8",
        )
        (self.repo / "packs" / PACK_ID / "skills" / GUIDE_ID / "agents").mkdir()
        (self.repo / "packs" / PACK_ID / "skills" / GUIDE_ID / "agents" / "openai.yaml").write_text(
            "interface:\n  display_name: \"Guide\"\n",
            encoding="utf-8",
        )
        (self.repo / "packs" / PACK_ID / "skills" / ATOMIC_ID / "SKILL.md").write_text(
            f"---\nname: {ATOMIC_ID}\n"
            "description: Use when the user asks to review a contract.\n"
            "---\n\n# Review contracts\n",
            encoding="utf-8",
        )
        (self.repo / "packs" / PACK_ID / "skills" / ATOMIC_ID / "agents").mkdir()
        (self.repo / "packs" / PACK_ID / "skills" / ATOMIC_ID / "agents" / "openai.yaml").write_text(
            "interface:\n  display_name: \"Review\"\n",
            encoding="utf-8",
        )
        (self.repo / "packs" / PACK_ID / "pack.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 2,
                    "id": PACK_ID,
                    "displayName": "合同审查与起草",
                    "description": "合同审查与起草领域包",
                    "version": "1.0.0",
                    "license": "Apache-2.0",
                    "jurisdiction": "CN-mainland",
                    "contentModel": "multi-skill-progressive-disclosure",
                    "reinstallStrategy": "replace",
                    "scope": {
                        "purpose": "支持合同审查与起草业务",
                        "inScope": ["合同审查"],
                        "outOfScope": ["合同争议诉讼代理"],
                        "primaryDeliverables": ["合同审查意见"],
                    },
                    "guideSkill": GUIDE_ID,
                    "mcp": {"contractRange": ">=1.0 <2.0"},
                    "skills": [
                        {
                            "id": GUIDE_ID,
                            "kind": "guide",
                            "displayName": "合同业务能力导航",
                            "goal": "说明领域能力、边界和原子能力全貌",
                            "notFor": ["直接完成合同审查"],
                            "deliverables": ["能力定位结果"],
                            "path": f"skills/{GUIDE_ID}",
                            "relations": {
                                "depends-on": [],
                                "related-to": [ATOMIC_ID],
                                "excludes": [],
                            },
                            "mcpDecisionNodes": [],
                        },
                        {
                            "id": ATOMIC_ID,
                            "kind": "atomic",
                            "displayName": "合同审查",
                            "goal": "审查具体合同并形成风险意见",
                            "notFor": ["代理合同争议诉讼"],
                            "deliverables": ["合同审查意见"],
                            "path": f"skills/{ATOMIC_ID}",
                            "relations": {
                                "depends-on": [],
                                "related-to": [GUIDE_ID],
                                "excludes": [],
                            },
                            "mcpDecisionNodes": [],
                        },
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (
            self.repo
            / "packs"
            / PACK_ID
            / "skills"
            / ATOMIC_ID
            / "references"
            / "review-standard.md"
        ).write_text(
            "# Workflow\n",
            encoding="utf-8",
        )
        (
            self.repo
            / "packs"
            / PACK_ID
            / "skills"
            / ATOMIC_ID
            / "assets"
            / "templates"
            / "review-report.docx"
        ).write_bytes(b"template fixture")
        (self.repo / "packs" / PACK_ID / "tests" / "internal.md").write_text(
            "not for release\n",
            encoding="utf-8",
        )
        (self.repo / "packs" / PACK_ID / ".env").write_text(
            "DO_NOT_PACKAGE=yes\n",
            encoding="utf-8",
        )
        (self.repo / "LICENSE").write_text("Apache License 2.0 fixture\n", encoding="utf-8")
        (self.repo / "NOTICE").write_text("Lawyeah fixture notice\n", encoding="utf-8")
        (self.repo / "catalog" / "domains.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "catalogVersion": "2026.08",
                    "domains": [{"id": PACK_ID, "status": "active"}],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (self.repo / "release-manifest.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 2,
                    "required": ["pack.json"],
                    "rootInclude": ["LICENSE", "NOTICE"],
                    "include": ["pack.json", "skills/**"],
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def run_builder(self, pack_id: str, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(BUILDER),
                "--root",
                str(self.repo),
                "--pack",
                pack_id,
                "--output",
                str(output),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_release_contains_only_allowlisted_runtime_files(self):
        result = self.run_builder(PACK_ID, self.output)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(
                archive.namelist(),
                [
                    f"{PACK_ID}/LICENSE",
                    f"{PACK_ID}/NOTICE",
                    f"{PACK_ID}/pack.json",
                    f"{PACK_ID}/skills/{GUIDE_ID}/SKILL.md",
                    f"{PACK_ID}/skills/{GUIDE_ID}/agents/openai.yaml",
                    f"{PACK_ID}/skills/{ATOMIC_ID}/SKILL.md",
                    f"{PACK_ID}/skills/{ATOMIC_ID}/agents/openai.yaml",
                    f"{PACK_ID}/skills/{ATOMIC_ID}/assets/templates/review-report.docx",
                    f"{PACK_ID}/skills/{ATOMIC_ID}/references/review-standard.md",
                ],
            )
        digest = hashlib.sha256(self.output.read_bytes()).hexdigest()
        self.assertEqual(
            self.output.with_suffix(".zip.sha256").read_text(encoding="utf-8"),
            f"{digest}  {self.output.name}\n",
        )

    def test_rebuilding_same_pack_is_byte_identical(self):
        first_result = self.run_builder(PACK_ID, self.output)
        second_result = self.run_builder(PACK_ID, self.second_output)

        self.assertEqual(first_result.returncode, 0, first_result.stdout + first_result.stderr)
        self.assertEqual(second_result.returncode, 0, second_result.stdout + second_result.stderr)
        self.assertEqual(self.output.read_bytes(), self.second_output.read_bytes())

    def test_unknown_pack_is_rejected_without_archive(self):
        result = self.run_builder("unknown-pack", self.output)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown or inactive pack", result.stderr)
        self.assertFalse(self.output.exists())

    def test_path_traversal_pack_id_is_rejected(self):
        result = self.run_builder("../secrets", self.output)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid pack id", result.stderr)
        self.assertFalse(self.output.exists())

    def test_undeclared_runtime_skill_is_rejected(self):
        undeclared = self.repo / "packs" / PACK_ID / "skills" / "lawyeah-contracts-hidden"
        undeclared.mkdir()
        (undeclared / "SKILL.md").write_text(
            "---\nname: lawyeah-contracts-hidden\n"
            "description: Use when hidden.\n---\n",
            encoding="utf-8",
        )

        result = self.run_builder(PACK_ID, self.output)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("undeclared runtime skill", result.stderr)
        self.assertFalse(self.output.exists())

    def test_release_rejects_private_research_inside_declared_skill(self):
        leaked = (
            self.repo
            / "packs"
            / PACK_ID
            / "skills"
            / ATOMIC_ID
            / "evals"
            / "raw-output.md"
        )
        leaked.parent.mkdir()
        leaked.write_text("internal evaluation\n", encoding="utf-8")

        result = self.run_builder(PACK_ID, self.output)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forbidden runtime path", result.stderr)
        self.assertFalse(self.output.exists())

    def test_release_rejects_credential_file_inside_declared_skill(self):
        leaked = (
            self.repo
            / "packs"
            / PACK_ID
            / "skills"
            / ATOMIC_ID
            / "scripts"
            / "service.key"
        )
        leaked.parent.mkdir()
        leaked.write_text("PRIVATE KEY FIXTURE\n", encoding="utf-8")

        result = self.run_builder(PACK_ID, self.output)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("credential file", result.stderr)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
