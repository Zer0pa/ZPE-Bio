"""Archive helpers for safe extraction."""

from __future__ import annotations

import stat
import shutil
import zipfile
from pathlib import Path, PurePosixPath


def _validated_zip_target(destination: Path, member_name: str) -> Path:
    member = PurePosixPath(member_name)
    if member.is_absolute() or any(part == ".." for part in member.parts):
        raise ValueError(f"zip member escapes extraction root: {member_name}")

    parts = [part for part in member.parts if part not in ("", ".")]
    target = destination.joinpath(*parts).resolve()
    target.relative_to(destination.resolve())
    return target


def safe_extract_zip(zip_file: zipfile.ZipFile, destination: Path) -> list[Path]:
    """Extract a zip archive while preventing path traversal."""
    destination.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []

    for member in zip_file.infolist():
        target = _validated_zip_target(destination, member.filename)
        mode = member.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise ValueError(f"zip member is a symlink: {member.filename}")

        if member.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        with zip_file.open(member, "r") as source, target.open("wb") as handle:
            shutil.copyfileobj(source, handle)
        extracted.append(target)

    return extracted
