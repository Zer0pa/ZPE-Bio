from __future__ import annotations

import stat
import zipfile
from pathlib import Path

import pytest

from zpe_bio.archive_utils import safe_extract_zip


def test_safe_extract_zip_extracts_nested_files(tmp_path: Path) -> None:
    archive_path = tmp_path / "nested.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("SisFall_dataset/file.txt", "ok")

    destination = tmp_path / "extract"
    with zipfile.ZipFile(archive_path, "r") as archive:
        extracted = safe_extract_zip(archive, destination)

    assert extracted == [destination / "SisFall_dataset" / "file.txt"]
    assert (destination / "SisFall_dataset" / "file.txt").read_text(encoding="utf-8") == "ok"


def test_safe_extract_zip_rejects_traversal_entries(tmp_path: Path) -> None:
    archive_path = tmp_path / "traversal.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../escape.txt", "bad")

    destination = tmp_path / "extract"
    with zipfile.ZipFile(archive_path, "r") as archive:
        with pytest.raises(ValueError, match="escapes extraction root"):
            safe_extract_zip(archive, destination)

    assert not (tmp_path / "escape.txt").exists()


def test_safe_extract_zip_rejects_symlink_entries(tmp_path: Path) -> None:
    archive_path = tmp_path / "symlink.zip"
    destination = tmp_path / "extract"

    symlink = zipfile.ZipInfo("shortcut")
    symlink.create_system = 3
    symlink.external_attr = (stat.S_IFLNK | 0o777) << 16

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(symlink, "../escape.txt")

    with zipfile.ZipFile(archive_path, "r") as archive:
        with pytest.raises(ValueError, match="symlink"):
            safe_extract_zip(archive, destination)

    assert not any(destination.rglob("*"))
