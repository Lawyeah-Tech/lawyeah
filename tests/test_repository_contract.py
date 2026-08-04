import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tooling" / "validate_repository.py"
PACK_ID = "review-draft-contracts"
GUIDE_ID = "lawyeah-contracts-guide"
ATOMIC_ID = "lawyeah-contracts-review"


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

    def copy_complete_fixture(self, fixture: Path) -> None:
        self.copy_valid_fixture(fixture)
        shutil.copytree(ROOT / "templates", fixture / "templates")
        shutil.copytree(ROOT / "docs", fixture / "docs")
        (fixture / ".github" / "workflows").mkdir(parents=True)
        shutil.copy2(
            ROOT / ".github" / "workflows" / "validate.yml",
            fixture / ".github" / "workflows" / "validate.yml",
        )

    def activate_domain_with_valid_pack(self, fixture: Path) -> Path:
        catalog_path = fixture / "catalog" / "domains.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        domain = next(item for item in catalog["domains"] if item["id"] == PACK_ID)
        domain["status"] = "active"
        catalog_path.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        pack_root = fixture / "packs" / PACK_ID
        for skill_id in (GUIDE_ID, ATOMIC_ID):
            (pack_root / "skills" / skill_id).mkdir(parents=True)
            (pack_root / "skills" / skill_id / "SKILL.md").write_text(
                f"---\nname: {skill_id}\n"
                f"description: Use when testing {skill_id}.\n---\n\n# Fixture\n",
                encoding="utf-8",
            )

        manifest = {
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
        }
        (pack_root / "pack.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return pack_root

    def add_valid_boundaries_to_catalog(self, fixture: Path) -> Path:
        catalog_path = fixture / "catalog" / "domains.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["schemaVersion"] = 2
        for domain in catalog["domains"]:
            domain.pop("scope", None)
            domain.update(
                {
                    "purpose": f"处理{domain['displayName']}领域的主要客户目标",
                    "inScope": [f"{domain['displayName']}领域事项"],
                    "outOfScope": ["其他领域具有独立主要成果的事项"],
                    "primaryDeliverables": [f"{domain['displayName']}专业成果"],
                    "ownershipRule": "以用户主要目标和最终专业成果确定归属",
                    "relatedDomains": [],
                }
            )
        catalog_path.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return catalog_path

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
        self.assertIn("templates/domain-pack/skills/guide/SKILL.md.tmpl", result.stderr)
        self.assertIn("templates/domain-pack/skills/atomic/SKILL.md.tmpl", result.stderr)
        self.assertIn(".github/workflows/validate.yml", result.stderr)

    def test_active_multi_skill_pack_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            self.copy_complete_fixture(fixture)
            self.activate_domain_with_valid_pack(fixture)

            result = self.run_validator(fixture)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_declared_guide_skill_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            self.copy_complete_fixture(fixture)
            pack_root = self.activate_domain_with_valid_pack(fixture)
            shutil.rmtree(pack_root / "skills" / GUIDE_ID)

            result = self.run_validator(fixture)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("declared skill directory is missing", result.stderr)

    def test_skill_frontmatter_name_must_match_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            self.copy_complete_fixture(fixture)
            pack_root = self.activate_domain_with_valid_pack(fixture)
            (pack_root / "skills" / ATOMIC_ID / "SKILL.md").write_text(
                "---\nname: lawyeah-contracts-wrong\n"
                "description: Use when testing mismatch.\n---\n",
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("frontmatter name must match skill directory", result.stderr)

    def test_relation_to_unknown_skill_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            self.copy_complete_fixture(fixture)
            pack_root = self.activate_domain_with_valid_pack(fixture)
            manifest_path = pack_root / "pack.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["skills"][1]["relations"]["depends-on"] = [
                {
                    "skill": "lawyeah-contracts-missing",
                    "requiredResult": "已确认的合同类型",
                }
            ]
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("relation target is not declared", result.stderr)

    def test_cross_skill_runtime_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            self.copy_complete_fixture(fixture)
            pack_root = self.activate_domain_with_valid_pack(fixture)
            (pack_root / "skills" / ATOMIC_ID / "SKILL.md").write_text(
                f"---\nname: {ATOMIC_ID}\n"
                "description: Use when testing references.\n---\n\n"
                "Read [another skill](../lawyeah-contracts-guide/SKILL.md).\n",
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cross-skill runtime reference", result.stderr)

    def test_non_ascii_runtime_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            self.copy_complete_fixture(fixture)
            pack_root = self.activate_domain_with_valid_pack(fixture)
            chinese_path = pack_root / "skills" / ATOMIC_ID / "references" / "规范.md"
            chinese_path.parent.mkdir()
            chinese_path.write_text("# 规范\n", encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("runtime path must use ASCII", result.stderr)

    def test_domain_boundary_fields_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            self.copy_complete_fixture(fixture)
            catalog_path = self.add_valid_boundaries_to_catalog(fixture)
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["domains"][0].pop("purpose")
            catalog_path.write_text(
                json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("purpose must be non-empty", result.stderr)

    def test_related_domain_must_exist_and_be_reciprocal(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            self.copy_complete_fixture(fixture)
            catalog_path = self.add_valid_boundaries_to_catalog(fixture)
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            first = catalog["domains"][0]
            second = catalog["domains"][1]
            first["relatedDomains"] = [
                {
                    "id": second["id"],
                    "relation": "related-to",
                    "boundary": "以主要交付成果区分",
                }
            ]
            catalog_path.write_text(
                json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("related domain relation must be reciprocal", result.stderr)

if __name__ == "__main__":
    unittest.main()
