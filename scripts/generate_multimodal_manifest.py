#!/usr/bin/env python3
"""Generate SHA-256 manifest for transplanted multimodal modules."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = ROOT / "python" / "zpe_bio" / "multimodal"
DEFAULT_OUTPUT = ROOT / "docs" / "multimodal" / "MULTIMODAL_TRANSPLANT_MANIFEST.sha256"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _iter_files(target: Path) -> list[Path]:
    files = [p for p in target.rglob("*.py") if "__pycache__" not in p.parts]
    return sorted(files)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate multimodal SHA-256 manifest.")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target = args.target.resolve()
    if not target.exists():
        raise SystemExit(f"target does not exist: {target}")

    lines: list[str] = []
    for file_path in _iter_files(target):
        rel = file_path.relative_to(ROOT)
        lines.append(f"{_sha256(file_path)}  {rel.as_posix()}")

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(lines)} entries to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
