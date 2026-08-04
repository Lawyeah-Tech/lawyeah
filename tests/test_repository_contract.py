import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tooling" / "validate_repository.py"


class RepositoryContractTests(unittest.TestCase):
    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(root)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_current_repository_satisfies_contract(self):
        result = self.run_validator(ROOT)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("22 domains", result.stdout)
        self.assertIn("P0=8, P1=8, P2=6", result.stdout)

    def copy_valid_fixture(self, fixture: Path) -> None:
        shutil.copytree(ROOT / "catalog", fixture / "catalog")
        shutil.copytree(ROOT / "schemas", fixture / "schemas")
        shutil.copy2(ROOT / "release-manifest.json", fixture)
        for filename in (
            "README.md",
            "LICENSE",
            "NOTICE",
            ".gitignore",
            ".gitattributes",
        ):
            shutil.copy2(ROOT / filename, fixture)

    def test_duplicate_domain_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            self.copy_valid_fixture(fixture)
            catalog_path = fixture / "catalog" / "domains.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["domains"][1]["id"] = catalog["domains"][0]["id"]
            catalog_path.write_text(
                json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate domain id", result.stderr)

    def test_active_domain_without_runtime_pack_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            self.copy_valid_fixture(fixture)
            catalog_path = fixture / "catalog" / "domains.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["domains"][0]["status"] = "active"
            catalog_path.write_text(
                json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("active pack is missing", result.stderr)

    def test_missing_initialization_artifacts_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            self.copy_valid_fixture(fixture)

            result = self.run_validator(fixture)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("templates/domain-pack/SKILL.md.tmpl", result.stderr)
        self.assertIn(".github/workflows/validate.yml", result.stderr)

if __name__ == "__main__":
    unittest.main()
