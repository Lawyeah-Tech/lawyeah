#!/usr/bin/env python3
"""Build a deterministic, allowlisted static archive for one active domain pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Tuple


PACK_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


class BuildError(Exception):
    """Raised when a release cannot be built safely."""


def load_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise BuildError(f"missing configuration: {path}") from error
    except json.JSONDecodeError as error:
        raise BuildError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise BuildError(f"expected JSON object in {path}")
    return value


def is_allowlisted(relative_path: str, patterns: Iterable[str]) -> bool:
    for pattern in patterns:
        if pattern.endswith("/**"):
            prefix = pattern[:-3].rstrip("/")
            if relative_path.startswith(prefix + "/"):
                return True
        elif relative_path == pattern:
            return True
    return False


def active_pack_ids(catalog: Dict[str, Any]) -> set[str]:
    domains = catalog.get("domains", [])
    if not isinstance(domains, list):
        raise BuildError("catalog domains must be an array")
    return {
        domain.get("id")
        for domain in domains
        if isinstance(domain, dict) and domain.get("status") == "active"
    }


def collect_files(pack_root: Path, include_patterns: List[str]) -> List[Path]:
    files: List[Path] = []
    for path in pack_root.rglob("*"):
        if path.is_symlink():
            raise BuildError(f"symbolic links are not allowed in releases: {path}")
        if not path.is_file():
            continue
        relative = PurePosixPath(path.relative_to(pack_root).as_posix()).as_posix()
        if is_allowlisted(relative, include_patterns):
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(pack_root).as_posix())


def write_archive(
    output: Path,
    pack_id: str,
    entries: List[Tuple[str, Path]],
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".zip", delete=False) as handle:
        temporary_path = Path(handle.name)
    try:
        with zipfile.ZipFile(
            temporary_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for relative, path in entries:
                info = zipfile.ZipInfo(f"{pack_id}/{relative}", ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
        os.replace(temporary_path, output)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def build_release(root: Path, pack_id: str, output: Path) -> str:
    if not PACK_ID_PATTERN.fullmatch(pack_id):
        raise BuildError(f"invalid pack id: {pack_id}")

    catalog = load_json(root / "catalog" / "domains.json")
    if pack_id not in active_pack_ids(catalog):
        raise BuildError(f"unknown or inactive pack: {pack_id}")

    release_manifest = load_json(root / "release-manifest.json")
    required = release_manifest.get("required")
    root_include = release_manifest.get("rootInclude")
    include = release_manifest.get("include")
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        raise BuildError("release manifest required must be an array of paths")
    if not isinstance(include, list) or not all(isinstance(item, str) for item in include):
        raise BuildError("release manifest include must be an array of paths")
    if not isinstance(root_include, list) or not all(
        isinstance(item, str) for item in root_include
    ):
        raise BuildError("release manifest rootInclude must be an array of paths")

    packs_root = (root / "packs").resolve()
    pack_root = (packs_root / pack_id).resolve()
    if pack_root.parent != packs_root or not pack_root.is_dir():
        raise BuildError(f"pack directory is missing: {pack_id}")

    for relative in required:
        required_path = pack_root / relative
        if not required_path.is_file() or required_path.is_symlink():
            raise BuildError(f"required release file is missing: {relative}")

    files = collect_files(pack_root, include)
    included_relatives = {path.relative_to(pack_root).as_posix() for path in files}
    missing_from_archive = [path for path in required if path not in included_relatives]
    if missing_from_archive:
        raise BuildError(
            "required files are not allowlisted: " + ", ".join(missing_from_archive)
        )

    entries = [(path.relative_to(pack_root).as_posix(), path) for path in files]
    for relative in root_include:
        source = root / relative
        if not source.is_file() or source.is_symlink():
            raise BuildError(f"required repository release file is missing: {relative}")
        entries.append((relative, source))
    entries.sort(key=lambda entry: entry[0])

    write_archive(output, pack_id, entries)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum_path = output.with_suffix(output.suffix + ".sha256")
    checksum_path.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return digest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Repository root")
    parser.add_argument("--pack", required=True, help="Active domain pack ID")
    parser.add_argument("--output", type=Path, required=True, help="Output ZIP path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        digest = build_release(args.root.resolve(), args.pack, args.output.resolve())
    except BuildError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"built {args.output} sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
