#!/usr/bin/env python3
"""Validate Lawyeah repository governance, catalogs, schemas, and active packs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


PACK_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
EXPECTED_COUNTS = {"P0": 8, "P1": 8, "P2": 6}
ALLOWED_STATUSES = {"planned", "active", "deprecated"}
REQUIRED_ROOT_PATHS = (
    "README.md",
    "LICENSE",
    "NOTICE",
    ".gitignore",
    ".gitattributes",
    "release-manifest.json",
    "catalog/domains.json",
    "catalog/bundles.json",
    "catalog/platforms.json",
    "schemas/pack.schema.json",
    "schemas/mcp-capabilities.schema.json",
    "schemas/adapter.schema.json",
    "templates/domain-pack/SKILL.md.tmpl",
    "templates/domain-pack/pack.json.tmpl",
    "templates/domain-pack/agents/openai.yaml.tmpl",
    "templates/domain-pack/references/ROUTING.md",
    "docs/architecture/repository.md",
    ".github/workflows/validate.yml",
)


def load_json(path: Path, errors: List[str]) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path}")
        return {}
    except json.JSONDecodeError as error:
        errors.append(f"invalid JSON in {path}: {error}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"expected JSON object in {path}")
        return {}
    return value


def validate_domain_catalog(root: Path, errors: List[str]) -> Counter[str]:
    catalog = load_json(root / "catalog" / "domains.json", errors)
    if catalog.get("schemaVersion") != 1:
        errors.append("domain catalog schemaVersion must be 1")
    if not re.fullmatch(r"\d{4}\.\d{2}", str(catalog.get("catalogVersion", ""))):
        errors.append("domain catalog catalogVersion must use YYYY.MM")

    domains = catalog.get("domains")
    if not isinstance(domains, list):
        errors.append("domain catalog domains must be an array")
        return Counter()
    if len(domains) != 22:
        errors.append(f"domain catalog must contain exactly 22 domains, found {len(domains)}")

    identifiers: set[str] = set()
    display_names: set[str] = set()
    priorities: Counter[str] = Counter()
    for index, domain in enumerate(domains):
        label = f"domain[{index}]"
        if not isinstance(domain, dict):
            errors.append(f"{label} must be an object")
            continue
        identifier = domain.get("id")
        if not isinstance(identifier, str) or not PACK_ID_PATTERN.fullmatch(identifier):
            errors.append(f"{label} has invalid id: {identifier}")
        elif identifier in identifiers:
            errors.append(f"duplicate domain id: {identifier}")
        else:
            identifiers.add(identifier)

        display_name = domain.get("displayName")
        if not isinstance(display_name, str) or not display_name.strip():
            errors.append(f"{label} displayName must be non-empty")
        elif display_name in display_names:
            errors.append(f"duplicate domain displayName: {display_name}")
        else:
            display_names.add(display_name)

        priority = domain.get("priority")
        priorities[str(priority)] += 1
        if priority not in EXPECTED_COUNTS:
            errors.append(f"{label} has invalid priority: {priority}")
        if domain.get("jurisdiction") != "CN-mainland":
            errors.append(f"{label} jurisdiction must be CN-mainland")
        if domain.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{label} has invalid status: {domain.get('status')}")
        if not isinstance(domain.get("scope"), str) or not domain["scope"].strip():
            errors.append(f"{label} scope must be non-empty")

        if domain.get("status") == "active" and isinstance(identifier, str):
            pack_root = root / "packs" / identifier
            if not pack_root.is_dir():
                errors.append(f"active pack is missing: {identifier}")
            else:
                for required in ("SKILL.md", "pack.json"):
                    if not (pack_root / required).is_file():
                        errors.append(f"active pack {identifier} is missing {required}")
                validate_pack_manifest(pack_root / "pack.json", identifier, errors)

    for priority, expected in EXPECTED_COUNTS.items():
        actual = priorities[priority]
        if actual != expected:
            errors.append(f"priority count {priority} must be {expected}, found {actual}")
    return priorities


def validate_pack_manifest(path: Path, expected_id: str, errors: List[str]) -> None:
    manifest = load_json(path, errors)
    if manifest.get("id") != expected_id:
        errors.append(f"pack manifest id must match directory: {expected_id}")
    if not SEMVER_PATTERN.fullmatch(str(manifest.get("version", ""))):
        errors.append(f"pack {expected_id} version must use semantic versioning")
    if manifest.get("license") != "Apache-2.0":
        errors.append(f"pack {expected_id} license must be Apache-2.0")
    if manifest.get("entrypoint") != "SKILL.md":
        errors.append(f"pack {expected_id} entrypoint must be SKILL.md")


def validate_release_manifest(root: Path, errors: List[str]) -> None:
    manifest = load_json(root / "release-manifest.json", errors)
    if manifest.get("schemaVersion") != 1:
        errors.append("release manifest schemaVersion must be 1")
    required = manifest.get("required")
    root_include = manifest.get("rootInclude")
    include = manifest.get("include")
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        errors.append("release manifest required must be an array of paths")
    elif set(required) != {"SKILL.md", "pack.json"}:
        errors.append("release manifest must require SKILL.md and pack.json")
    if not isinstance(include, list) or not all(isinstance(item, str) for item in include):
        errors.append("release manifest include must be an array of paths")
    elif not set(required or []).issubset(set(include)):
        errors.append("every required release file must also be allowlisted")
    if not isinstance(root_include, list) or set(root_include) != {"LICENSE", "NOTICE"}:
        errors.append("release manifest rootInclude must contain LICENSE and NOTICE")


def validate_schemas(root: Path, errors: List[str]) -> None:
    for name in ("pack.schema.json", "mcp-capabilities.schema.json", "adapter.schema.json"):
        schema = load_json(root / "schemas" / name, errors)
        if schema and schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{name} must declare JSON Schema Draft 2020-12")


def validate_repository(root: Path) -> List[str]:
    errors: List[str] = []
    for relative in REQUIRED_ROOT_PATHS:
        if not (root / relative).is_file():
            errors.append(f"missing required path: {relative}")

    license_path = root / "LICENSE"
    if license_path.is_file():
        license_text = license_path.read_text(encoding="utf-8")
        if "Apache License" not in license_text or "Version 2.0" not in license_text:
            errors.append("LICENSE must contain Apache License 2.0")

    validate_domain_catalog(root, errors)
    validate_release_manifest(root, errors)
    validate_schemas(root, errors)
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Repository root")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    errors = validate_repository(root)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("repository valid: 22 domains; P0=8, P1=8, P2=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
