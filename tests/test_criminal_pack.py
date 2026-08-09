import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK_ID = "conduct-criminal-defense"
GUIDE_ID = "lawyeah-conduct-criminal-defense"
ATOMIC_IDS = {
    "lawyeah-criminal-apply-bail",
    "lawyeah-criminal-assess-criminal-accusation",
    "lawyeah-criminal-assess-criminal-appeal",
    "lawyeah-criminal-assess-plea-leniency",
    "lawyeah-criminal-challenge-non-filing-or-delay",
    "lawyeah-criminal-emergency-defense-response",
    "lawyeah-criminal-prepare-arrest-review-opinion",
    "lawyeah-criminal-prepare-criminal-accusation",
    "lawyeah-criminal-prepare-first-custody-meeting",
    "lawyeah-criminal-prepare-non-prosecution-opinion",
    "lawyeah-criminal-prepare-victim-prosecution-agency",
    "lawyeah-criminal-review-case-file-evidence",
    "lawyeah-criminal-screen-engagement-authority-conflicts",
}


class CriminalPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack_root = ROOT / "packs" / PACK_ID
        cls.manifest = json.loads(
            (cls.pack_root / "pack.json").read_text(encoding="utf-8")
        )

    def test_domain_is_active_and_pack_identity_is_stable(self):
        catalog = json.loads(
            (ROOT / "catalog" / "domains.json").read_text(encoding="utf-8")
        )
        domain = next(item for item in catalog["domains"] if item["id"] == PACK_ID)

        self.assertEqual(domain["status"], "active")
        self.assertEqual(self.manifest["id"], PACK_ID)
        self.assertEqual(self.manifest["guideSkill"], GUIDE_ID)
        self.assertEqual(self.manifest["version"], "0.1.0")

    def test_pack_contains_one_guide_and_exactly_thirteen_frozen_atomics(self):
        guide_ids = {
            item["id"] for item in self.manifest["skills"] if item["kind"] == "guide"
        }
        atomic_ids = {
            item["id"] for item in self.manifest["skills"] if item["kind"] == "atomic"
        }

        self.assertEqual(guide_ids, {GUIDE_ID})
        self.assertEqual(atomic_ids, ATOMIC_IDS)
        self.assertEqual(len(self.manifest["skills"]), 14)

    def test_atomics_are_independent_and_guide_is_navigation_only(self):
        entries = {item["id"]: item for item in self.manifest["skills"]}

        self.assertEqual(entries[GUIDE_ID]["relations"]["depends-on"], [])
        self.assertEqual(set(entries[GUIDE_ID]["relations"]["related-to"]), ATOMIC_IDS)
        for skill_id in ATOMIC_IDS:
            self.assertEqual(entries[skill_id]["relations"]["depends-on"], [])
            self.assertIn(GUIDE_ID, entries[skill_id]["relations"]["related-to"])

    def test_every_runtime_skill_has_progressive_disclosure_files(self):
        for skill_id in ATOMIC_IDS:
            skill_root = self.pack_root / "skills" / skill_id
            self.assertTrue((skill_root / "SKILL.md").is_file(), skill_id)
            self.assertTrue((skill_root / "agents" / "openai.yaml").is_file(), skill_id)
            self.assertEqual(
                {path.name for path in (skill_root / "references").iterdir()},
                {"method.md", "output-contract.md", "routing.md"},
                skill_id,
            )

    def test_runtime_does_not_explain_private_development_process(self):
        forbidden = (
            "私有研究目录",
            "研发检索",
            "专家评审记录",
            "gpt-luna",
            "Lawyeah_Library",
            "retrieval.lawyeah.cn/app/services/knowledge_search",
        )
        for path in (self.pack_root / "skills").rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".yaml", ".yml"}:
                continue
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                self.assertNotIn(marker, text, str(path.relative_to(ROOT)))

    def test_openai_metadata_uses_portable_interface_fields_only(self):
        for metadata in (self.pack_root / "skills").glob("*/agents/openai.yaml"):
            text = metadata.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("interface:\n"), str(metadata))
            self.assertNotIn("\ntools:\n", text, str(metadata))


if __name__ == "__main__":
    unittest.main()
