#!/usr/bin/env python3
"""Build deterministic unsigned catalog payloads from verified domain archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Tuple
from urllib.parse import urlparse


ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
PRIMARY_ORIGIN = "https://downloads.lawyeah.cn"
FALLBACK_ORIGIN = "https://github.com/Lawyeah-Tech/lawyeah/releases/download"


class BuildError(Exception):
    """Raised when unsigned release metadata cannot be built safely."""


class ReleaseOrigins:
    def __init__(self, primary: str = PRIMARY_ORIGIN, fallback: str = FALLBACK_ORIGIN):
        self.primary = primary.rstrip("/")
        self.fallback = fallback.rstrip("/")

    def validate(self) -> None:
        primary = urlparse(self.primary)
        fallback = urlparse(self.fallback)
        if (
            primary.scheme != "https"
            or primary.hostname != "downloads.lawyeah.cn"
            or primary.path not in ("", "/")
            or primary.query
            or primary.fragment
        ):
            raise BuildError("untrusted primary release origin")
        if (
            fallback.scheme != "https"
            or fallback.hostname != "github.com"
            or fallback.path != "/Lawyeah-Tech/lawyeah/releases/download"
            or fallback.query
            or fallback.fragment
        ):
            raise BuildError("untrusted fallback release origin")


def canonical_json(value: Dict[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def load_domain_catalog(root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    try:
        catalog = json.loads((root / "catalog" / "domains.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError(f"cannot load canonical domain catalog: {error}") from error
    domains = catalog.get("domains")
    if not isinstance(domains, list):
        raise BuildError("canonical domain catalog domains must be an array")
    active: List[Dict[str, Any]] = []
    by_id: Dict[str, Dict[str, Any]] = {}
    for domain in domains:
        if not isinstance(domain, dict):
            raise BuildError("canonical domain entry must be an object")
        domain_id = domain.get("id")
        name = domain.get("displayName")
        if not isinstance(domain_id, str) or not ID_PATTERN.fullmatch(domain_id):
            raise BuildError("canonical domain has invalid id")
        if domain_id in by_id:
            raise BuildError(f"duplicate canonical domain: {domain_id}")
        if not isinstance(name, str) or not name.strip():
            raise BuildError(f"canonical domain has invalid displayName: {domain_id}")
        by_id[domain_id] = domain
        if domain.get("status") == "active":
            active.append(domain)
    if not active:
        raise BuildError("at least one active domain is required")
    active.sort(key=lambda item: item["id"])
    return active, by_id


def inspect_artifact(path: Path) -> Tuple[str, str]:
    if not path.is_file() or path.is_symlink():
        raise BuildError(f"release archive is missing or unsafe: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            manifest_entries = []
            for info in archive.infolist():
                name = PurePosixPath(info.filename)
                if info.filename.startswith("/") or ".." in name.parts or "\\" in info.filename:
                    raise BuildError(f"unsafe path in release archive: {info.filename}")
                if len(name.parts) == 2 and name.name == "pack.json":
                    manifest_entries.append(info)
            if len(manifest_entries) != 1:
                raise BuildError("release archive must contain exactly one <domain>/pack.json")
            info = manifest_entries[0]
            if info.file_size > 1 << 20:
                raise BuildError("pack.json exceeds size limit")
            manifest = json.loads(archive.read(info))
    except (OSError, zipfile.BadZipFile, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BuildError(f"cannot inspect release archive {path}: {error}") from error
    domain_id = manifest.get("id") if isinstance(manifest, dict) else None
    version = manifest.get("version") if isinstance(manifest, dict) else None
    root_id = PurePosixPath(info.filename).parts[0]
    if not isinstance(domain_id, str) or not ID_PATTERN.fullmatch(domain_id) or domain_id != root_id:
        raise BuildError("archive root and pack id must match")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        raise BuildError(f"pack {domain_id} version must be stable semantic version")
    return domain_id, version


def write_payload(path: Path, payload: Dict[str, Any]) -> None:
    data = canonical_json(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.with_suffix(path.suffix + ".sha256").write_text(
        hashlib.sha256(data).hexdigest() + "\n",
        encoding="ascii",
    )


def build_payloads(
    root: Path,
    artifacts: Iterable[Path],
    output: Path,
    minimum_installer_version: str,
    origins: ReleaseOrigins | None = None,
) -> None:
    root = root.resolve()
    output = output.resolve()
    if not SEMVER_PATTERN.fullmatch(minimum_installer_version):
        raise BuildError("minimum installer version must be stable semantic version")
    origins = origins or ReleaseOrigins()
    origins.validate()
    active, canonical_by_id = load_domain_catalog(root)
    releases: Dict[str, Tuple[str, Path]] = {}
    for artifact_value in artifacts:
        artifact = Path(artifact_value).resolve()
        domain_id, version = inspect_artifact(artifact)
        if domain_id not in canonical_by_id or canonical_by_id[domain_id].get("status") != "active":
            raise BuildError(f"release archive is not an active canonical domain: {domain_id}")
        if domain_id in releases:
            raise BuildError(f"duplicate release archive: {domain_id}")
        releases[domain_id] = (version, artifact)
    if not releases:
        raise BuildError("at least one active release archive is required")

    catalog_domains = []
    for domain in active:
        domain_id = domain["id"]
        if domain_id in releases:
            version, artifact = releases[domain_id]
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            latest = {
                "schemaVersion": 1,
                "domainID": domain_id,
                "version": version,
                "packURL": f"{origins.primary}/domains/{domain_id}/{version}/pack.zip",
                "fallbackPackURL": f"{origins.fallback}/{domain_id}-v{version}/pack.zip",
                "sha256": digest,
                "size": artifact.stat().st_size,
            }
            write_payload(output / "domains" / domain_id / "latest.payload.json", latest)
        catalog_domains.append(
            {
                "id": domain_id,
                "name": domain["displayName"],
                "latestURL": f"{origins.primary}/domains/{domain_id}/latest.json",
                "fallbackLatestURL": f"{origins.fallback}/static-catalog/{domain_id}-latest.json",
            }
        )
    write_payload(
        output / "catalog.payload.json",
        {
            "schemaVersion": 1,
            "minimumInstallerVersion": minimum_installer_version,
            "domains": catalog_domains,
        },
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimum-installer-version", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        build_payloads(
            root=args.root,
            artifacts=args.artifact,
            output=args.output,
            minimum_installer_version=args.minimum_installer_version,
        )
    except BuildError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"built unsigned release metadata in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
