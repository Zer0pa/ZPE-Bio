"""Tests for EEG ingest and deterministic mental-lane mapping."""

from __future__ import annotations

from pathlib import Path

import pytest

from zpe_bio.bio_wave2 import DependencyError, SourceError, encode_eeg_to_mental


def test_synthetic_eeg_mapping_deterministic() -> None:
    first = encode_eeg_to_mental(edf_path=None, max_channels=2, max_samples=256, synthetic=True)
    second = encode_eeg_to_mental(edf_path=None, max_channels=2, max_samples=256, synthetic=True)

    assert first["mode"] == "synthetic"
    assert second["mode"] == "synthetic"
    assert first["stream_hash"] == second["stream_hash"]
    assert all(channel["quantized_direction_match"] for channel in first["channels"])


def test_missing_real_eeg_file_raises_source_error() -> None:
    with pytest.raises(SourceError):
        encode_eeg_to_mental(
            edf_path=Path("validation/datasets/eeg/not_present.edf"),
            max_channels=1,
            max_samples=128,
            synthetic=False,
        )


def test_missing_eeg_backends_raise_dependency_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from zpe_bio import bio_wave2

    def _raise_import_error(*_args, **_kwargs):
        raise ImportError("simulated missing backend")

    monkeypatch.setattr(bio_wave2, "_read_edf_with_pyedflib", _raise_import_error)
    monkeypatch.setattr(bio_wave2, "_read_edf_with_mne", _raise_import_error)
    dummy_edf = tmp_path / "missing-backend.edf"
    dummy_edf.touch()

    with pytest.raises(DependencyError):
        encode_eeg_to_mental(
            edf_path=dummy_edf,
            max_channels=1,
            max_samples=128,
            synthetic=False,
        )
