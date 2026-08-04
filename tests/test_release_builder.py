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


class ReleaseBuilderTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary_directory.name)
        self.output = self.repo / "first.zip"
        self.second_output = self.repo / "second.zip"

        (self.repo / "catalog").mkdir()
        (self.repo / "packs" / PACK_ID / "references").mkdir(parents=True)
        (self.repo / "packs" / PACK_ID / "tests").mkdir()
        (self.repo / "packs" / PACK_ID / "SKILL.md").write_text(
            "---\nname: review-draft-contracts\n"
            "description: Review and draft contracts.\n---\n\n# Contracts\n",
            encoding="utf-8",
        )
        (self.repo / "packs" / PACK_ID / "pack.json").write_text(
            '{"id":"review-draft-contracts","version":"1.0.0"}\n',
            encoding="utf-8",
        )
        (self.repo / "packs" / PACK_ID / "references" / "workflow.md").write_text(
            "# Workflow\n",
            encoding="utf-8",
        )
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
                    "schemaVersion": 1,
                    "required": ["SKILL.md", "pack.json"],
                    "rootInclude": ["LICENSE", "NOTICE"],
                    "include": [
                        "SKILL.md",
                        "pack.json",
                        "agents/**",
                        "references/**",
                        "scripts/**",
                        "assets/**",
                    ],
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
                    f"{PACK_ID}/SKILL.md",
                    f"{PACK_ID}/pack.json",
                    f"{PACK_ID}/references/workflow.md",
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


if __name__ == "__main__":
    unittest.main()
