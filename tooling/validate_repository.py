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
SKILL_ID_PATTERN = re.compile(r"^lawyeah-[a-z0-9]+(?:-[a-z0-9]+)*$")
CAPABILITY_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
EXPECTED_COUNTS = {"P0": 8, "P1": 8, "P2": 6}
ALLOWED_STATUSES = {"planned", "active", "deprecated"}
ALLOWED_SKILL_TOP_LEVEL = {"SKILL.md", "agents", "references", "scripts", "assets"}
FORBIDDEN_RUNTIME_COMPONENTS = {
    "research",
    "evals",
    "tests",
    "test",
    "raw-data",
    "evidence",
    "credentials",
    "secrets",
    ".mcp-auth",
    ".git",
}
PRIVATE_RESEARCH_MARKERS = (
    "Lawyeah_Library",
    "/Users/",
    "retrieval.lawyeah.cn/app/services/knowledge_search",
    "research/mcp/",
    "research/labor/",
)
CREDENTIAL_SUFFIXES = {".pem", ".key", ".token", ".p12", ".pfx", ".jks"}
CREDENTIAL_FILENAMES = {
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "service-account.json",
}
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
    "schemas/domain-catalog.schema.json",
    "schemas/adapter.schema.json",
    "templates/domain-pack/pack.json.tmpl",
    "templates/domain-pack/skills/guide/SKILL.md.tmpl",
    "templates/domain-pack/skills/guide/agents/openai.yaml.tmpl",
    "templates/domain-pack/skills/atomic/SKILL.md.tmpl",
    "templates/domain-pack/skills/atomic/agents/openai.yaml.tmpl",
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
    if catalog.get("schemaVersion") != 2:
        errors.append("domain catalog schemaVersion must be 2")
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
    domain_by_id: Dict[str, Dict[str, Any]] = {}
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
            domain_by_id[identifier] = domain

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
        if not is_non_empty_text(domain.get("purpose")):
            errors.append(f"{label} purpose must be non-empty")
        for field in ("inScope", "outOfScope", "primaryDeliverables"):
            validate_text_list(domain.get(field), f"{label} {field}", errors)
        if not is_non_empty_text(domain.get("ownershipRule")):
            errors.append(f"{label} ownershipRule must be non-empty")
        related_domains = domain.get("relatedDomains")
        if not isinstance(related_domains, list):
            errors.append(f"{label} relatedDomains must be an array")
        else:
            seen_related: set[str] = set()
            for relation_index, relation in enumerate(related_domains):
                relation_label = f"{label} relatedDomains[{relation_index}]"
                if not isinstance(relation, dict):
                    errors.append(f"{relation_label} must be an object")
                    continue
                target = relation.get("id")
                if not isinstance(target, str) or not PACK_ID_PATTERN.fullmatch(target):
                    errors.append(f"{relation_label} has invalid domain id: {target}")
                elif target == identifier:
                    errors.append(f"{relation_label} must not target its own domain")
                elif target in seen_related:
                    errors.append(f"{label} has duplicate related domain: {target}")
                else:
                    seen_related.add(target)
                if relation.get("relation") not in {"related-to", "excludes"}:
                    errors.append(f"{relation_label} has invalid relation")
                if not is_non_empty_text(relation.get("boundary")):
                    errors.append(f"{relation_label} boundary must be non-empty")

        if domain.get("status") == "active" and isinstance(identifier, str):
            pack_root = root / "packs" / identifier
            if not pack_root.is_dir():
                errors.append(f"active pack is missing: {identifier}")
            else:
                for required in ("pack.json",):
                    if not (pack_root / required).is_file():
                        errors.append(f"active pack {identifier} is missing {required}")
                validate_pack_manifest(pack_root, identifier, errors)

    for priority, expected in EXPECTED_COUNTS.items():
        actual = priorities[priority]
        if actual != expected:
            errors.append(f"priority count {priority} must be {expected}, found {actual}")

    for source_id, domain in domain_by_id.items():
        related_domains = domain.get("relatedDomains")
        if not isinstance(related_domains, list):
            continue
        for relation in related_domains:
            if not isinstance(relation, dict):
                continue
            target_id = relation.get("id")
            relation_type = relation.get("relation")
            target = domain_by_id.get(target_id)
            if target is None:
                errors.append(f"related domain does not exist: {source_id} -> {target_id}")
                continue
            reciprocal = target.get("relatedDomains")
            if not isinstance(reciprocal, list) or not any(
                isinstance(item, dict)
                and item.get("id") == source_id
                and item.get("relation") == relation_type
                for item in reciprocal
            ):
                errors.append(
                    "related domain relation must be reciprocal: "
                    f"{source_id} {relation_type} {target_id}"
                )
    return priorities


def frontmatter_name(skill_path: Path) -> str | None:
    try:
        text = skill_path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return None
    match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", text, flags=re.DOTALL)
    if not match:
        return None
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip() == "name":
            return value.strip().strip('"\'')
    return None


def is_non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_text_list(value: Any, label: str, errors: List[str]) -> None:
    if (
        not isinstance(value, list)
        or not value
        or not all(is_non_empty_text(item) for item in value)
    ):
        errors.append(f"{label} must be a non-empty array of text")


def validate_runtime_paths(pack_root: Path, errors: List[str]) -> None:
    for path in pack_root.rglob("*"):
        relative = path.relative_to(pack_root).as_posix()
        try:
            relative.encode("ascii")
        except UnicodeEncodeError:
            errors.append(f"runtime path must use ASCII: {relative}")
        if path.is_symlink():
            errors.append(f"runtime pack must not contain symbolic links: {relative}")


def validate_skill_references(skill_root: Path, skill_id: str, errors: List[str]) -> None:
    for path in skill_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".yaml", ".yml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "../" in text or "..\\" in text:
            relative = path.relative_to(skill_root).as_posix()
            errors.append(f"cross-skill runtime reference in {skill_id}/{relative}")


def validate_skill_runtime_layout(
    skill_root: Path, skill_id: str, errors: List[str]
) -> None:
    agent_metadata = skill_root / "agents" / "openai.yaml"
    if not agent_metadata.is_file():
        errors.append(f"skill {skill_id} is missing agents/openai.yaml")

    for path in skill_root.rglob("*"):
        relative_path = path.relative_to(skill_root)
        parts = relative_path.parts
        relative = relative_path.as_posix()
        if not parts:
            continue

        if parts[0] not in ALLOWED_SKILL_TOP_LEVEL:
            errors.append(f"forbidden runtime path in {skill_id}: {relative}")
        if any(part in FORBIDDEN_RUNTIME_COMPONENTS or part.startswith(".") for part in parts):
            errors.append(f"forbidden runtime path in {skill_id}: {relative}")
        if parts[0] == "agents" and relative != "agents/openai.yaml" and path.is_file():
            errors.append(f"forbidden runtime path in {skill_id}: {relative}")
        if path.is_file() and (
            path.suffix.lower() in CREDENTIAL_SUFFIXES
            or path.name.lower() in CREDENTIAL_FILENAMES
        ):
            errors.append(f"credential file in {skill_id}: {relative}")

        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".json",
            ".yaml",
            ".yml",
            ".txt",
            ".py",
            ".sh",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in PRIVATE_RESEARCH_MARKERS:
            if marker in text:
                errors.append(
                    f"private research marker in {skill_id}/{relative}: {marker}"
                )


def validate_pack_manifest(pack_root: Path, expected_id: str, errors: List[str]) -> None:
    path = pack_root / "pack.json"
    manifest = load_json(path, errors)
    if manifest.get("schemaVersion") != 2:
        errors.append(f"pack {expected_id} schemaVersion must be 2")
    if manifest.get("id") != expected_id:
        errors.append(f"pack manifest id must match directory: {expected_id}")
    if not SEMVER_PATTERN.fullmatch(str(manifest.get("version", ""))):
        errors.append(f"pack {expected_id} version must use semantic versioning")
    if manifest.get("license") != "Apache-2.0":
        errors.append(f"pack {expected_id} license must be Apache-2.0")
    if manifest.get("jurisdiction") != "CN-mainland":
        errors.append(f"pack {expected_id} jurisdiction must be CN-mainland")
    if manifest.get("contentModel") != "multi-skill-progressive-disclosure":
        errors.append(f"pack {expected_id} contentModel is invalid")
    if manifest.get("reinstallStrategy") != "replace":
        errors.append(f"pack {expected_id} reinstallStrategy must be replace")

    scope = manifest.get("scope")
    if not isinstance(scope, dict):
        errors.append(f"pack {expected_id} scope must be an object")
    else:
        if not is_non_empty_text(scope.get("purpose")):
            errors.append(f"pack {expected_id} scope purpose must be non-empty")
        for field in ("inScope", "outOfScope", "primaryDeliverables"):
            validate_text_list(scope.get(field), f"pack {expected_id} scope {field}", errors)

    mcp = manifest.get("mcp")
    if not isinstance(mcp, dict) or not is_non_empty_text(mcp.get("contractRange")):
        errors.append(f"pack {expected_id} mcp contractRange must be non-empty")

    skills = manifest.get("skills")
    if not isinstance(skills, list):
        errors.append(f"pack {expected_id} skills must be an array")
        return

    skill_ids: set[str] = set()
    skill_entries: Dict[str, Dict[str, Any]] = {}
    for index, skill in enumerate(skills):
        label = f"pack {expected_id} skill[{index}]"
        if not isinstance(skill, dict):
            errors.append(f"{label} must be an object")
            continue
        skill_id = skill.get("id")
        if not isinstance(skill_id, str) or not SKILL_ID_PATTERN.fullmatch(skill_id):
            errors.append(f"{label} has invalid skill id: {skill_id}")
            continue
        if skill_id in skill_ids:
            errors.append(f"duplicate skill id in pack {expected_id}: {skill_id}")
            continue
        skill_ids.add(skill_id)
        skill_entries[skill_id] = skill
        expected_path = f"skills/{skill_id}"
        if skill.get("path") != expected_path:
            errors.append(f"{label} path must be {expected_path}")
        if skill.get("kind") not in {"guide", "atomic"}:
            errors.append(f"{label} kind must be guide or atomic")
        for field in ("displayName", "goal"):
            if not is_non_empty_text(skill.get(field)):
                errors.append(f"{label} {field} must be non-empty")
        validate_text_list(skill.get("notFor"), f"{label} notFor", errors)
        validate_text_list(skill.get("deliverables"), f"{label} deliverables", errors)
        if "version" in skill:
            errors.append(f"{label} must not declare an independent version")

    guide_skill = manifest.get("guideSkill")
    guide_entries = [item for item in skill_entries.values() if item.get("kind") == "guide"]
    atomic_entries = [item for item in skill_entries.values() if item.get("kind") == "atomic"]
    if len(guide_entries) != 1:
        errors.append(f"pack {expected_id} must declare exactly one guide skill")
    if not atomic_entries:
        errors.append(f"pack {expected_id} must declare at least one atomic skill")
    if guide_skill not in skill_entries or skill_entries.get(guide_skill, {}).get("kind") != "guide":
        errors.append(f"pack {expected_id} guideSkill must reference its guide entry")

    for skill_id, skill in skill_entries.items():
        skill_root = pack_root / "skills" / skill_id
        skill_path = skill_root / "SKILL.md"
        if not skill_root.is_dir() or not skill_path.is_file():
            errors.append(f"declared skill directory is missing: {skill_id}")
            continue
        actual_name = frontmatter_name(skill_path)
        if actual_name != skill_id:
            errors.append(
                f"frontmatter name must match skill directory: {skill_id} (found {actual_name})"
            )
        validate_skill_references(skill_root, skill_id, errors)
        validate_skill_runtime_layout(skill_root, skill_id, errors)

        relations = skill.get("relations")
        if not isinstance(relations, dict):
            errors.append(f"skill {skill_id} relations must be an object")
        else:
            dependencies = relations.get("depends-on")
            if not isinstance(dependencies, list):
                errors.append(f"skill {skill_id} depends-on must be an array")
            else:
                for dependency in dependencies:
                    if not isinstance(dependency, dict):
                        errors.append(f"skill {skill_id} dependency must be an object")
                        continue
                    target = dependency.get("skill")
                    if target not in skill_ids:
                        errors.append(f"relation target is not declared: {skill_id} -> {target}")
                    if target == skill_id:
                        errors.append(f"skill relation must not target itself: {skill_id}")
                    if not is_non_empty_text(dependency.get("requiredResult")):
                        errors.append(f"skill {skill_id} dependency requiredResult must be non-empty")
            for relation in ("related-to", "excludes"):
                targets = relations.get(relation)
                if not isinstance(targets, list):
                    errors.append(f"skill {skill_id} {relation} must be an array")
                    continue
                for target in targets:
                    if target not in skill_ids:
                        errors.append(f"relation target is not declared: {skill_id} -> {target}")
                    if target == skill_id:
                        errors.append(f"skill relation must not target itself: {skill_id}")

        nodes = skill.get("mcpDecisionNodes")
        if not isinstance(nodes, list):
            errors.append(f"skill {skill_id} mcpDecisionNodes must be an array")
        else:
            node_ids: set[str] = set()
            for node in nodes:
                if not isinstance(node, dict):
                    errors.append(f"skill {skill_id} MCP decision node must be an object")
                    continue
                node_id = node.get("id")
                if not isinstance(node_id, str) or not PACK_ID_PATTERN.fullmatch(node_id):
                    errors.append(f"skill {skill_id} has invalid MCP decision node id: {node_id}")
                elif node_id in node_ids:
                    errors.append(f"skill {skill_id} has duplicate MCP decision node: {node_id}")
                else:
                    node_ids.add(node_id)
                if not is_non_empty_text(node.get("purpose")):
                    errors.append(f"skill {skill_id} MCP decision purpose must be non-empty")
                capability = node.get("capability")
                if not isinstance(capability, str) or not CAPABILITY_PATTERN.fullmatch(capability):
                    errors.append(f"skill {skill_id} has invalid MCP capability: {capability}")
                if node.get("level") not in {"required", "recommended", "optional"}:
                    errors.append(f"skill {skill_id} has invalid MCP dependency level")
                if not is_non_empty_text(node.get("unavailableBehavior")):
                    errors.append(
                        f"skill {skill_id} MCP unavailableBehavior must be non-empty"
                    )

    skills_root = pack_root / "skills"
    actual_skill_ids = {
        child.name
        for child in skills_root.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    } if skills_root.is_dir() else set()
    for undeclared in sorted(actual_skill_ids - skill_ids):
        errors.append(f"undeclared runtime skill: {undeclared}")
    validate_runtime_paths(pack_root, errors)


def validate_release_manifest(root: Path, errors: List[str]) -> None:
    manifest = load_json(root / "release-manifest.json", errors)
    if manifest.get("schemaVersion") != 2:
        errors.append("release manifest schemaVersion must be 2")
    required = manifest.get("required")
    root_include = manifest.get("rootInclude")
    include = manifest.get("include")
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        errors.append("release manifest required must be an array of paths")
    elif set(required) != {"pack.json"}:
        errors.append("release manifest must require pack.json")
    if not isinstance(include, list) or not all(isinstance(item, str) for item in include):
        errors.append("release manifest include must be an array of paths")
    elif set(include) != {"pack.json", "skills/**"}:
        errors.append("release manifest must allow only pack.json and skills/**")
    if not isinstance(root_include, list) or set(root_include) != {"LICENSE", "NOTICE"}:
        errors.append("release manifest rootInclude must contain LICENSE and NOTICE")


def validate_schemas(root: Path, errors: List[str]) -> None:
    for name in (
        "pack.schema.json",
        "mcp-capabilities.schema.json",
        "domain-catalog.schema.json",
        "adapter.schema.json",
    ):
        schema = load_json(root / "schemas" / name, errors)
        if schema and schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{name} must declare JSON Schema Draft 2020-12")


def validate_selected_pack(root: Path, pack_id: str, errors: List[str]) -> None:
    if not PACK_ID_PATTERN.fullmatch(pack_id):
        errors.append(f"invalid selected pack id: {pack_id}")
        return
    catalog = load_json(root / "catalog" / "domains.json", errors)
    domains = catalog.get("domains")
    known_ids = {
        item.get("id")
        for item in domains
        if isinstance(domains, list) and isinstance(item, dict)
    } if isinstance(domains, list) else set()
    if pack_id not in known_ids:
        errors.append(f"selected pack is not in domain catalog: {pack_id}")
        return
    pack_root = root / "packs" / pack_id
    if not pack_root.is_dir():
        errors.append(f"selected pack is missing: {pack_id}")
        return
    validate_pack_manifest(pack_root, pack_id, errors)


def validate_repository(root: Path, selected_pack: str | None = None) -> List[str]:
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
    if selected_pack is not None:
        validate_selected_pack(root, selected_pack, errors)
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Repository root")
    parser.add_argument(
        "--pack",
        help="Also validate this pack even when its catalog status is planned",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    errors = validate_repository(root, args.pack)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("repository valid: 22 domains; P0=8, P1=8, P2=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
