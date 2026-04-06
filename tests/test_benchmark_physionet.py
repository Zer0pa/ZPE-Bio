from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import benchmark_physionet as benchmark_physionet


def test_benchmark_physionet_routes_ecg_and_eeg(tmp_path, monkeypatch, capsys) -> None:
    ecg_calls: list[tuple[Path, int, int]] = []
    eeg_calls: list[tuple[Path, int, int, bool]] = []
    download_calls: list[tuple[str, str, list[str] | None]] = []

    class FakeWFDB:
        def dl_database(self, db_name: str, download_dir: str, records: list[str] | None = None) -> None:
            download_calls.append((db_name, download_dir, records))

        def get_record_list(self, db_name: str) -> list[str]:
            assert db_name == "ptb-xl/1.0.3"
            return [
                "records500/00000/00001_hr",
                "records500/00000/00002_hr",
            ]

    def fake_wfdb_module():
        return FakeWFDB()

    def fake_discover_wfdb_records(dataset_dir: Path, dataset: str) -> list[Path]:
        assert dataset == "ptb-xl"
        return [dataset_dir / "records500" / "00000" / "00001_hr"]

    def fake_load_local_wfdb_record(
        record_path: Path,
        channel_index: int,
        max_samples: int,
    ) -> dict[str, object]:
        ecg_calls.append((record_path, channel_index, max_samples))
        signal = np.array([0.0, 1.0, 0.5, 1.5], dtype=np.float64)
        return {
            "sample_rate_hz": 360.0,
            "signal": signal,
            "channels": ["MLII", "V5"],
        }

    def fake_roundtrip_metrics(
        signal: np.ndarray,
        signal_type: str,
        mode,
        thr_mode: str,
        threshold,
        step,
    ):
        assert signal_type == "ecg"
        reconstructed = signal + 0.001
        metrics = {
            "samples": int(signal.shape[0]),
            "raw_bytes": int(signal.shape[0] * 2),
            "zpe_bytes_est": 4,
            "compression_ratio": 2.0,
            "prd_percent": 1.25,
            "snr_db": 41.0,
        }
        return SimpleNamespace(compression_ratio=2.0), reconstructed, metrics

    def fake_encode_eeg_to_mental(
        edf_path: Path,
        max_channels: int = 2,
        max_samples: int = 2048,
        synthetic: bool = False,
    ) -> dict[str, object]:
        eeg_calls.append((edf_path, max_channels, max_samples, synthetic))
        return {
            "mode": "real_file",
            "backend": "mne",
            "source_path": str(edf_path),
            "channel_count": max_channels,
            "sample_rate_hz": 256.0,
            "total_words": 12,
            "total_strokes": 4,
            "raw_bytes": 512,
            "zpe_bytes_est": 128,
            "total_runtime_ms": 9.5,
            "channels": [
                {"signal_rmse": 0.1},
                {"signal_rmse": 0.2},
            ],
            "stream_hash": "abc123",
        }

    monkeypatch.setattr(benchmark_physionet, "_wfdb_module", fake_wfdb_module)
    monkeypatch.setattr(benchmark_physionet, "_discover_wfdb_records", fake_discover_wfdb_records)
    monkeypatch.setattr(benchmark_physionet, "_load_local_wfdb_record", fake_load_local_wfdb_record)
    monkeypatch.setattr(benchmark_physionet, "roundtrip_metrics", fake_roundtrip_metrics)
    monkeypatch.setattr(benchmark_physionet, "encode_eeg_to_mental", fake_encode_eeg_to_mental)

    download_root = tmp_path / "datasets"
    results_root = tmp_path / "results"
    sleep_edf = download_root / "sleep-edfx" / "sleep-cassette" / "SC4001E0-PSG.edf"
    sleep_edf.parent.mkdir(parents=True, exist_ok=True)
    sleep_edf.touch()

    code = benchmark_physionet.main(
        [
            "--dataset",
            "ptb-xl",
            "--dataset",
            "sleep-edfx",
            "--download-root",
            str(download_root),
            "--results-root",
            str(results_root),
            "--record-limit",
            "1",
            "--signal-samples",
            "128",
            "--eeg-samples",
            "64",
            "--eeg-channels",
            "2",
            "--json",
        ]
    )
    assert code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["comparison"]["ecg"]["entries"] == 1
    assert payload["comparison"]["eeg"]["entries"] == 1
    assert payload["comparison"]["delta_mean_compression_ratio"] == -2.0

    datasets = {item["dataset"]: item for item in payload["datasets"]}
    ptbxl = datasets["ptb-xl"]
    sleep = datasets["sleep-edfx"]

    assert ptbxl["download"]["status"] == "downloaded"
    assert ptbxl["aggregate"]["entries_ok"] == 1
    assert ptbxl["entries"][0]["status"] == "ok"
    assert ptbxl["entries"][0]["compression_ratio"] == 2.0
    assert ptbxl["entries"][0]["signal_integrity"]["status"] == "pass"
    assert (results_root / "ptbxl" / "BENCHMARK_SUMMARY.md").exists()
    assert (results_root / "ptbxl" / "summary.json").exists()
    assert (results_root / "ptbxl" / "entries" / "records500__00000__00001_hr.json").exists()

    assert sleep["download"]["status"] == "downloaded"
    assert sleep["aggregate"]["entries_ok"] == 1
    assert sleep["entries"][0]["status"] == "ok"
    assert sleep["entries"][0]["compression_ratio"] == 4.0
    assert sleep["entries"][0]["mean_channel_rmse"] == 0.15
    assert (results_root / "sleep-edfx" / "BENCHMARK_SUMMARY.md").exists()
    assert (results_root / "sleep-edfx" / "summary.json").exists()
    assert (results_root / "sleep-edfx" / "entries" / "sleep-cassette__SC4001E0-PSG.edf.json").exists()

    assert download_calls == [
        ("ptb-xl", str(download_root / "ptbxl"), ["records500/00000/00001_hr"]),
        ("sleep-edfx", str(download_root / "sleep-edfx"), None),
    ]
    assert ecg_calls == [(download_root / "ptbxl" / "records500" / "00000" / "00001_hr", 0, 128)]
    assert eeg_calls == [(sleep_edf, 2, 64, False)]
