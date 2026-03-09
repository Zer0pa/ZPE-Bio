#!/usr/bin/env python3
"""Verify SHA-256 manifest for transplanted multimodal modules."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs" / "multimodal" / "MULTIMODAL_TRANSPLANT_MANIFEST.sha256"
DEFAULT_TARGET = ROOT / "python" / "zpe_bio" / "multimodal"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _load_manifest(manifest: Path) -> dict[str, str]:
    expected: dict[str, str] = {}
    for lineno, raw in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            raise SystemExit(f"invalid manifest line {lineno}: {raw!r}")
        digest, rel = parts[0], parts[1].strip()
        expected[rel] = digest
    return expected


def _iter_actual(target: Path) -> dict[str, str]:
    actual: dict[str, str] = {}
    for file_path in sorted(p for p in target.rglob("*.py") if "__pycache__" not in p.parts):
        rel = file_path.relative_to(ROOT).as_posix()
        actual[rel] = _sha256(file_path)
    return actual


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify multimodal SHA-256 manifest.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    manifest = args.manifest.resolve()
    target = args.target.resolve()
    if not manifest.exists():
        raise SystemExit(f"manifest not found: {manifest}")
    if not target.exists():
        raise SystemExit(f"target not found: {target}")

    expected = _load_manifest(manifest)
    actual = _iter_actual(target)

    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = sorted(path for path in set(expected) & set(actual) if expected[path] != actual[path])

    if missing or extra or changed:
        if missing:
            print("missing files:")
            for path in missing:
                print(f"  - {path}")
        if extra:
            print("untracked files:")
            for path in extra:
                print(f"  - {path}")
        if changed:
            print("digest mismatches:")
            for path in changed:
                print(f"  - {path}")
        raise SystemExit(1)

    print(f"manifest verified: {len(expected)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
