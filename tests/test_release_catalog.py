import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "tooling" / "build_release_catalog.py"
PACK_ID = "handle-labor-employment"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_release_catalog", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load release catalog builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "catalog").mkdir()
        (self.root / "catalog" / "domains.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 2,
                    "catalogVersion": "2026.08",
                    "domains": [
                        {
                            "id": PACK_ID,
                            "displayName": "劳动与用工",
                            "status": "active",
                        },
                        {
                            "id": "defend-criminal-cases",
                            "displayName": "刑事辩护",
                            "status": "active",
                        },
                        {
                            "id": "handle-marriage-family-litigation",
                            "displayName": "婚家诉讼",
                            "status": "planned",
                        },
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        self.archive = self.root / "labor.zip"
        manifest = {
            "schemaVersion": 2,
            "id": PACK_ID,
            "displayName": "劳动与用工",
            "version": "1.2.3",
        }
        with zipfile.ZipFile(self.archive, "w") as archive:
            archive.writestr(
                f"{PACK_ID}/pack.json",
                json.dumps(manifest, ensure_ascii=False),
            )
            archive.writestr(f"{PACK_ID}/skills/lawyeah-labor-guide/SKILL.md", "guide")
        self.output = self.root / "metadata"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_builds_canonical_payloads_for_active_domains_only(self):
        builder = load_builder()
        builder.build_payloads(
            root=self.root,
            artifacts=[self.archive],
            output=self.output,
            minimum_installer_version="1.0.0",
        )

        catalog_bytes = (self.output / "catalog.payload.json").read_bytes()
        self.assertEqual(
            catalog_bytes,
            json.dumps(
                json.loads(catalog_bytes),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8"),
        )
        catalog = json.loads(catalog_bytes)
        self.assertEqual(
            [domain["id"] for domain in catalog["domains"]],
            ["defend-criminal-cases", PACK_ID],
        )
        labor = next(domain for domain in catalog["domains"] if domain["id"] == PACK_ID)
        self.assertEqual(labor["name"], "劳动与用工")
        self.assertEqual(
            labor["latestURL"],
            f"https://downloads.lawyeah.cn/domains/{PACK_ID}/latest.json",
        )

        latest_path = self.output / "domains" / PACK_ID / "latest.payload.json"
        latest_bytes = latest_path.read_bytes()
        latest = json.loads(latest_bytes)
        self.assertEqual(latest["version"], "1.2.3")
        self.assertEqual(
            latest["packURL"],
            f"https://downloads.lawyeah.cn/domains/{PACK_ID}/1.2.3/pack.zip",
        )
        self.assertEqual(
            latest["fallbackPackURL"],
            "https://github.com/Lawyeah-Tech/lawyeah/releases/download/"
            f"{PACK_ID}-v1.2.3/pack.zip",
        )
        self.assertRegex(latest["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(latest["sha256"], hashlib.sha256(self.archive.read_bytes()).hexdigest())
        self.assertEqual(latest["size"], self.archive.stat().st_size)

        checksum = latest_path.with_suffix(".json.sha256").read_text(encoding="ascii")
        self.assertEqual(checksum, hashlib.sha256(latest_bytes).hexdigest() + "\n")

    def test_rejects_untrusted_release_origins(self):
        builder = load_builder()
        with self.assertRaises(builder.BuildError):
            builder.ReleaseOrigins(
                primary="https://attacker.example",
                fallback="https://github.com/Lawyeah-Tech/lawyeah/releases/download",
            ).validate()

    def test_rejects_nonsemantic_or_mismatched_archive(self):
        builder = load_builder()
        bad_archive = self.root / "bad.zip"
        with zipfile.ZipFile(bad_archive, "w") as archive:
            archive.writestr(
                "wrong-domain/pack.json",
                json.dumps({"id": "wrong-domain", "version": "latest"}),
            )
        with self.assertRaises(builder.BuildError):
            builder.build_payloads(
                root=self.root,
                artifacts=[bad_archive],
                output=self.output,
                minimum_installer_version="1.0.0",
            )

    def test_public_schemas_match_installer_payload_fields(self):
        catalog_schema = json.loads(
            (ROOT / "schemas" / "release-catalog.schema.json").read_text(encoding="utf-8")
        )
        latest_schema = json.loads(
            (ROOT / "schemas" / "release-latest.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(catalog_schema["required"]),
            {"schemaVersion", "minimumInstallerVersion", "domains"},
        )
        self.assertEqual(
            set(latest_schema["required"]),
            {
                "schemaVersion",
                "domainID",
                "version",
                "packURL",
                "fallbackPackURL",
                "sha256",
                "size",
            },
        )
        self.assertFalse(catalog_schema["additionalProperties"])
        self.assertFalse(latest_schema["additionalProperties"])

    def test_protected_workflow_publishes_fixed_objects_last(self):
        workflow = (ROOT / ".github" / "workflows" / "release-domain.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("environment: release-production", workflow)
        self.assertIn("ED25519_PRIVATE_KEY_BASE64: ${{ secrets.ED25519_PRIVATE_KEY_BASE64 }}", workflow)
        self.assertNotIn("--private-key", workflow)
        self.assertIn("group: static-release-catalog", workflow)
        self.assertIn("rollback_fixed", workflow)
        self.assertIn("Verify existing active latest objects", workflow)
        self.assertIn("actions/upload-artifact@v7", workflow)
        immutable = workflow.index("Upload immutable version objects")
        verify = workflow.index("Verify immutable remote objects")
        fixed = workflow.index("Update fixed latest and catalog objects last")
        self.assertLess(immutable, verify)
        self.assertLess(verify, fixed)

    def test_domain_release_workflow_defaults_to_first_installer_compatibility_floor(self):
        workflow = (ROOT / ".github" / "workflows" / "release-domain.yml").read_text(
            encoding="utf-8"
        )
        default = re.search(
            r"^      minimum_installer_version:\n"
            r"(?:^        .*\n)*?"
            r'^        default: "([^"]+)"$',
            workflow,
            flags=re.MULTILINE,
        )
        self.assertIsNotNone(default)
        self.assertEqual(default.group(1), "0.1.0")


if __name__ == "__main__":
    unittest.main()
