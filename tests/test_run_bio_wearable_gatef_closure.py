from __future__ import annotations

import importlib.util
import io
import sys
import types
import zipfile
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_bio_wearable_gatef_closure.py"


def _load_closure_script(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    def _unused(*_args, **_kwargs):
        raise AssertionError("unexpected test call")

    monkeypatch.setitem(sys.modules, "wfdb", types.ModuleType("wfdb"))

    sklearn = types.ModuleType("sklearn")
    ensemble = types.ModuleType("sklearn.ensemble")
    ensemble.RandomForestClassifier = type("RandomForestClassifier", (), {})
    metrics = types.ModuleType("sklearn.metrics")
    metrics.confusion_matrix = _unused
    metrics.precision_score = _unused
    metrics.recall_score = _unused
    model_selection = types.ModuleType("sklearn.model_selection")
    model_selection.train_test_split = _unused

    monkeypatch.setitem(sys.modules, "sklearn", sklearn)
    monkeypatch.setitem(sys.modules, "sklearn.ensemble", ensemble)
    monkeypatch.setitem(sys.modules, "sklearn.metrics", metrics)
    monkeypatch.setitem(sys.modules, "sklearn.model_selection", model_selection)

    module_name = "test_run_bio_wearable_gatef_closure_module"
    spec = importlib.util.spec_from_file_location(module_name, SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def closure_script(monkeypatch: pytest.MonkeyPatch):
    return _load_closure_script(monkeypatch)


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    return buffer.getvalue()


def _write_outer_sisfall_zip(sisfall_dir: Path, inner_members: dict[str, bytes]) -> None:
    outer_zip = sisfall_dir / "SisFall.zip"
    sisfall_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(outer_zip, "w") as archive:
        archive.writestr("SisFall_dataset.zip", _zip_bytes(inner_members))


def _unexpected_download(*_args: object, **_kwargs: object) -> None:
    raise AssertionError("unexpected download")


def test_ensure_sisfall_extracts_valid_nested_archive(
    closure_script: types.ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dataset_root = tmp_path / "datasets"
    sisfall_dir = dataset_root / "sisfall"
    _write_outer_sisfall_zip(
        sisfall_dir,
        {
            "SisFall_dataset/SA01/F001.txt": b"1,2,3;\n",
            "SisFall_dataset/SA01/D001.txt": b"4,5,6;\n",
        },
    )
    monkeypatch.setattr(closure_script, "urlretrieve", _unexpected_download)

    extract_dir, metadata = closure_script._ensure_sisfall(dataset_root, [])

    assert extract_dir == sisfall_dir / "extracted" / "SisFall_dataset"
    assert (extract_dir / "SA01" / "F001.txt").read_text(encoding="latin-1") == "1,2,3;\n"
    assert (extract_dir / "SA01" / "D001.txt").read_text(encoding="latin-1") == "4,5,6;\n"
    assert metadata["files_count"] == 2


def test_ensure_sisfall_rejects_nested_archive_traversal(
    closure_script: types.ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dataset_root = tmp_path / "datasets"
    sisfall_dir = dataset_root / "sisfall"
    _write_outer_sisfall_zip(sisfall_dir, {"../escape.txt": b"bad"})
    monkeypatch.setattr(closure_script, "urlretrieve", _unexpected_download)

    with pytest.raises(ValueError, match="escapes extraction root"):
        closure_script._ensure_sisfall(dataset_root, [])

    assert not (sisfall_dir / "escape.txt").exists()
