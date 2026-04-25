"""Benchmark downloaded PhysioNet datasets with the local ZPE-Bio codec."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any

import numpy as np

from zpe_bio.bio_wave2 import encode_eeg_to_mental
from zpe_bio.codec import CodecMode
from zpe_bio.wearable_wave import roundtrip_metrics

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DatasetConfig:
    dataset: str
    signal_type: str
    download_name: str
    list_name: str | None
    download_subdir: str
    results_subdir: str
    default_limit: int | None


DATASETS: dict[str, DatasetConfig] = {
    "ptb-xl": DatasetConfig(
        dataset="ptb-xl",
        signal_type="ecg",
        download_name="ptb-xl",
        list_name="ptb-xl/1.0.3",
        download_subdir="ptbxl",
        results_subdir="ptbxl",
        default_limit=100,
    ),
    "ptbdb": DatasetConfig(
        dataset="ptbdb",
        signal_type="ecg",
        download_name="ptbdb",
        list_name="ptbdb",
        download_subdir="ptbdb",
        results_subdir="ptbdb",
        default_limit=None,
    ),
    "nstdb": DatasetConfig(
        dataset="nstdb",
        signal_type="ecg",
        download_name="nstdb",
        list_name="nstdb",
        download_subdir="nstdb",
        results_subdir="nstdb",
        default_limit=None,
    ),
    "edb": DatasetConfig(
        dataset="edb",
        signal_type="ecg",
        download_name="edb",
        list_name="edb",
        download_subdir="edb",
        results_subdir="edb",
        default_limit=None,
    ),
    "mimic3wdb-matched": DatasetConfig(
        dataset="mimic3wdb-matched",
        signal_type="ecg",
        download_name="mimic3wdb-matched",
        list_name="mimic3wdb-matched",
        download_subdir="mimic3wdb-matched",
        results_subdir="mimic3wdb-matched",
        default_limit=25,
    ),
    "sleep-edfx": DatasetConfig(
        dataset="sleep-edfx",
        signal_type="eeg",
        download_name="sleep-edfx",
        list_name=None,
        download_subdir="sleep-edfx",
        results_subdir="sleep-edfx",
        default_limit=25,
    ),
}


def _wfdb_module() -> Any:
    try:
        return __import__("wfdb")
    except ImportError as exc:  # pragma: no cover - runtime dependency
        raise SystemExit(
            "WFDB is required for PhysioNet benchmarking. Install with `python -m pip install -e \".[validation]\"`."
        ) from exc


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark downloaded PhysioNet ECG and EEG datasets with ZPE-Bio."
    )
    parser.add_argument(
        "--dataset",
        action="append",
        choices=sorted(DATASETS.keys()),
        required=True,
        help="Dataset to download and benchmark. Repeat for multiple datasets.",
    )
    parser.add_argument(
        "--download-root",
        default=str(REPO_ROOT / "validation" / "datasets"),
        help="Root directory used for wfdb.dl_database downloads.",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Reuse an existing local dataset mirror instead of calling wfdb.dl_database again.",
    )
    parser.add_argument(
        "--results-root",
        default=str(REPO_ROOT / "validation" / "results"),
        help="Root directory for benchmark outputs.",
    )
    parser.add_argument(
        "--record-limit",
        type=int,
        default=None,
        help="Optional cap applied to each dataset after discovery.",
    )
    parser.add_argument(
        "--signal-samples",
        type=int,
        default=5000,
        help="Maximum ECG samples loaded per record.",
    )
    parser.add_argument(
        "--eeg-samples",
        type=int,
        default=4096,
        help="Maximum EEG samples loaded per EDF file.",
    )
    parser.add_argument(
        "--eeg-channels",
        type=int,
        default=2,
        help="Maximum EEG channels processed per EDF file.",
    )
    parser.add_argument(
        "--lead-index",
        type=int,
        default=0,
        help="ECG channel index for WFDB datasets.",
    )
    parser.add_argument("--json", action="store_true", help="Emit the aggregate payload as JSON.")
    return parser.parse_args(argv)


def _repo_relative_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def _dataset_download_dir(download_root: Path, config: DatasetConfig) -> Path:
    return download_root / config.download_subdir


def _dataset_results_dir(results_root: Path, config: DatasetConfig) -> Path:
    return results_root / config.results_subdir


def _safe_slug(relative_path: Path) -> str:
    return relative_path.as_posix().replace("/", "__")


def _signal_integrity(original: np.ndarray, reconstructed: np.ndarray) -> dict[str, Any]:
    compared_samples = min(original.shape[0], reconstructed.shape[0])
    if compared_samples == 0:
        return {"status": "fail", "compared_samples": 0, "max_abs_error": None}
    delta = original[:compared_samples] - reconstructed[:compared_samples]
    return {
        "status": "pass" if np.isfinite(delta).all() else "fail",
        "compared_samples": int(compared_samples),
        "max_abs_error": round(float(np.max(np.abs(delta))), 9),
    }


def _load_local_wfdb_record(record_path: Path, channel_index: int, max_samples: int) -> dict[str, Any]:
    wfdb = _wfdb_module()
    record = wfdb.rdrecord(str(record_path), sampto=max_samples)
    if channel_index < 0 or channel_index >= record.p_signal.shape[1]:
        raise ValueError(
            f"channel_index {channel_index} out of range for {record_path} with {record.p_signal.shape[1]} channels"
        )
    signal = record.p_signal[:, channel_index].astype(np.float64)
    return {
        "sample_rate_hz": float(record.fs),
        "channels": list(record.sig_name),
        "signal": signal,
    }


def _discover_ptbxl_records(dataset_dir: Path) -> list[Path]:
    records = sorted(dataset_dir.glob("records500/**/*_hr.hea"))
    if records:
        return [path.with_suffix("") for path in records]
    return [path.with_suffix("") for path in sorted(dataset_dir.rglob("*.hea"))]


def _discover_wfdb_records(dataset_dir: Path, dataset: str) -> list[Path]:
    if dataset == "ptb-xl":
        return _discover_ptbxl_records(dataset_dir)
    return [path.with_suffix("") for path in sorted(dataset_dir.rglob("*.hea"))]


def _discover_sleep_edf_files(dataset_dir: Path) -> list[Path]:
    return sorted(
        path
        for pattern in ("*.edf", "*.EDF")
        for path in dataset_dir.rglob(pattern)
    )


def _limit_entries(items: list[Path], limit: int | None) -> list[Path]:
    if limit is None:
        return items
    return items[:limit]


def _ecg_entry(record_path: Path, dataset_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    relative_path = record_path.relative_to(dataset_dir)
    start = time.perf_counter()
    loaded = _load_local_wfdb_record(
        record_path=record_path,
        channel_index=args.lead_index,
        max_samples=args.signal_samples,
    )
    _encoded, reconstructed, metrics = roundtrip_metrics(
        loaded["signal"],
        signal_type="ecg",
        mode=CodecMode.CLINICAL,
        thr_mode="adaptive_rms",
        threshold=None,
        step=None,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return {
        "status": "ok",
        "dataset_entry": relative_path.as_posix(),
        "record_name": relative_path.stem,
        "sample_rate_hz": loaded["sample_rate_hz"],
        "channels": loaded["channels"],
        "samples": int(metrics["samples"]),
        "compression_ratio": float(metrics["compression_ratio"]),
        "snr_db": float(metrics["snr_db"]),
        "prd_percent": float(metrics["prd_percent"]),
        "roundtrip_time_ms": round(elapsed_ms, 6),
        "signal_integrity": _signal_integrity(loaded["signal"], reconstructed),
    }


def _eeg_entry(edf_path: Path, dataset_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    relative_path = edf_path.relative_to(dataset_dir)
    result = encode_eeg_to_mental(
        edf_path=edf_path,
        max_channels=args.eeg_channels,
        max_samples=args.eeg_samples,
        synthetic=False,
    )
    channel_rmses = [float(channel["signal_rmse"]) for channel in result["channels"]]
    zpe_bytes = int(result["zpe_bytes_est"])
    raw_bytes = int(result["raw_bytes"])
    compression_ratio = float(raw_bytes / zpe_bytes) if zpe_bytes > 0 else 0.0
    return {
        "status": "ok",
        "dataset_entry": relative_path.as_posix(),
        "record_name": relative_path.name,
        "sample_rate_hz": float(result["sample_rate_hz"]),
        "channel_count": int(result["channel_count"]),
        "raw_bytes": raw_bytes,
        "zpe_bytes_est": zpe_bytes,
        "compression_ratio": round(compression_ratio, 6),
        "total_runtime_ms": float(result["total_runtime_ms"]),
        "mean_channel_rmse": round(mean(channel_rmses), 6) if channel_rmses else 0.0,
        "max_channel_rmse": round(max(channel_rmses), 6) if channel_rmses else 0.0,
        "stream_hash": result["stream_hash"],
        "signal_integrity": {
            "status": "pass" if channel_rmses else "fail",
            "channels": len(channel_rmses),
        },
    }


def _error_entry(item_path: Path, dataset_dir: Path, exc: Exception) -> dict[str, Any]:
    relative_path = item_path.relative_to(dataset_dir)
    return {
        "status": "error",
        "dataset_entry": relative_path.as_posix(),
        "record_name": relative_path.name,
        "error": str(exc),
    }


def _write_entry_payloads(entries_dir: Path, entries: list[dict[str, Any]]) -> None:
    entries_dir.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        entry_id = _safe_slug(Path(entry["dataset_entry"]))
        (entries_dir / f"{entry_id}.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")


def _aggregate_dataset(config: DatasetConfig, entries: list[dict[str, Any]]) -> dict[str, Any]:
    ok_entries = [entry for entry in entries if entry["status"] == "ok"]
    compression_values = [float(entry["compression_ratio"]) for entry in ok_entries]
    aggregate = {
        "signal_type": config.signal_type,
        "entries_total": len(entries),
        "entries_ok": len(ok_entries),
        "entries_failed": len(entries) - len(ok_entries),
    }
    if compression_values:
        aggregate.update(
            {
                "mean_compression_ratio": round(mean(compression_values), 6),
                "median_compression_ratio": round(median(compression_values), 6),
                "min_compression_ratio": round(min(compression_values), 6),
                "max_compression_ratio": round(max(compression_values), 6),
            }
        )
    if config.signal_type == "ecg" and ok_entries:
        aggregate["mean_snr_db"] = round(mean(float(entry["snr_db"]) for entry in ok_entries), 6)
        aggregate["max_prd_percent"] = round(max(float(entry["prd_percent"]) for entry in ok_entries), 6)
    if config.signal_type == "eeg" and ok_entries:
        aggregate["mean_channel_rmse"] = round(mean(float(entry["mean_channel_rmse"]) for entry in ok_entries), 6)
        aggregate["mean_runtime_ms"] = round(mean(float(entry["total_runtime_ms"]) for entry in ok_entries), 6)
    return aggregate


def _write_summary_markdown(
    config: DatasetConfig,
    output_path: Path,
    dataset_dir: Path,
    entries: list[dict[str, Any]],
    aggregate: dict[str, Any],
    download_status: dict[str, Any],
) -> None:
    ok_entries = [entry for entry in entries if entry["status"] == "ok"]
    lines = [
        f"# {config.dataset} benchmark summary",
        "",
        f"Dataset path: `{_repo_relative_path(dataset_dir)}`",
        f"Signal type: `{config.signal_type}`",
        f"Download status: `{download_status['status']}`",
        "",
        "## Aggregate",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key in (
        "entries_total",
        "entries_ok",
        "entries_failed",
        "mean_compression_ratio",
        "median_compression_ratio",
        "min_compression_ratio",
        "max_compression_ratio",
        "mean_snr_db",
        "max_prd_percent",
        "mean_channel_rmse",
        "mean_runtime_ms",
    ):
        if key in aggregate:
            lines.append(f"| {key} | {aggregate[key]} |")

    lines.extend(
        [
            "",
            "## Entries",
            "",
        ]
    )

    if config.signal_type == "ecg":
        lines.extend(
            [
                "| Entry | CR | SNR (dB) | PRD (%) | Runtime (ms) | Integrity |",
                "| --- | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for entry in ok_entries:
            lines.append(
                f"| {entry['dataset_entry']} | {entry['compression_ratio']:.6f} | "
                f"{entry['snr_db']:.6f} | {entry['prd_percent']:.6f} | "
                f"{entry['roundtrip_time_ms']:.6f} | {entry['signal_integrity']['status']} |"
            )
    else:
        lines.extend(
            [
                "| Entry | CR | Mean channel RMSE | Runtime (ms) | Integrity |",
                "| --- | ---: | ---: | ---: | --- |",
            ]
        )
        for entry in ok_entries:
            lines.append(
                f"| {entry['dataset_entry']} | {entry['compression_ratio']:.6f} | "
                f"{entry['mean_channel_rmse']:.6f} | {entry['total_runtime_ms']:.6f} | "
                f"{entry['signal_integrity']['status']} |"
            )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_dataset_outputs(
    config: DatasetConfig,
    dataset_dir: Path,
    results_dir: Path,
    entries: list[dict[str, Any]],
    download_status: dict[str, Any],
) -> dict[str, Any]:
    results_dir.mkdir(parents=True, exist_ok=True)
    entries_dir = results_dir / "entries"
    _write_entry_payloads(entries_dir, entries)
    aggregate = _aggregate_dataset(config, entries)
    summary_payload = {
        "dataset": config.dataset,
        "signal_type": config.signal_type,
        "dataset_dir": _repo_relative_path(dataset_dir),
        "download": download_status,
        "aggregate": aggregate,
        "entries": entries,
    }
    (results_dir / "summary.json").write_text(json.dumps(summary_payload, indent=2) + "\n", encoding="utf-8")
    _write_summary_markdown(
        config=config,
        output_path=results_dir / "BENCHMARK_SUMMARY.md",
        dataset_dir=dataset_dir,
        entries=entries,
        aggregate=aggregate,
        download_status=download_status,
    )
    return summary_payload


def _records_requested(config: DatasetConfig, args: argparse.Namespace) -> int | str:
    limit = _dataset_limit(config, args)
    return limit if limit is not None else "all"


def _download_record_subset(wfdb: Any, config: DatasetConfig, args: argparse.Namespace) -> list[str] | None:
    limit = _dataset_limit(config, args)
    if config.list_name is None or limit is None:
        return None

    record_list = list(wfdb.get_record_list(config.list_name))
    return record_list[:limit]


def _download_dataset(
    config: DatasetConfig,
    download_root: Path,
    skip_download: bool,
    args: argparse.Namespace,
) -> tuple[Path, dict[str, Any]]:
    dataset_dir = _dataset_download_dir(download_root, config)
    if skip_download:
        if not dataset_dir.exists():
            raise FileNotFoundError(f"dataset directory not found for --skip-download: {dataset_dir}")
        return dataset_dir, {
            "status": "reused_local",
            "target_dir": str(dataset_dir),
            "records_requested": _records_requested(config, args),
        }

    wfdb = _wfdb_module()
    dataset_dir.parent.mkdir(parents=True, exist_ok=True)
    selected_records = _download_record_subset(wfdb, config, args)
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
        if selected_records is None:
            wfdb.dl_database(config.download_name, str(dataset_dir))
        else:
            wfdb.dl_database(config.download_name, str(dataset_dir), records=selected_records)
    return dataset_dir, {
        "status": "downloaded",
        "target_dir": str(dataset_dir),
        "records_requested": _records_requested(config, args),
    }


def _dataset_limit(config: DatasetConfig, args: argparse.Namespace) -> int | None:
    if args.record_limit is not None:
        return args.record_limit
    return config.default_limit


def _benchmark_ecg_dataset(config: DatasetConfig, dataset_dir: Path, args: argparse.Namespace) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    record_paths = _limit_entries(_discover_wfdb_records(dataset_dir, config.dataset), _dataset_limit(config, args))
    for record_path in record_paths:
        try:
            entries.append(_ecg_entry(record_path, dataset_dir, args))
        except Exception as exc:  # pragma: no cover - exercised on real datasets
            entries.append(_error_entry(record_path, dataset_dir, exc))
    return entries


def _benchmark_eeg_dataset(config: DatasetConfig, dataset_dir: Path, args: argparse.Namespace) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    edf_paths = _limit_entries(_discover_sleep_edf_files(dataset_dir), _dataset_limit(config, args))
    for edf_path in edf_paths:
        try:
            entries.append(_eeg_entry(edf_path, dataset_dir, args))
        except Exception as exc:  # pragma: no cover - exercised on real datasets
            entries.append(_error_entry(edf_path, dataset_dir, exc))
    return entries


def _comparison_payload(dataset_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    ok_by_type: dict[str, list[dict[str, Any]]] = {"ecg": [], "eeg": []}
    for dataset in dataset_payloads:
        signal_type = dataset["signal_type"]
        ok_by_type[signal_type].extend(
            entry for entry in dataset["entries"] if entry["status"] == "ok"
        )

    comparison: dict[str, Any] = {}
    for signal_type in ("ecg", "eeg"):
        entries = ok_by_type[signal_type]
        ratios = [float(entry["compression_ratio"]) for entry in entries]
        comparison[signal_type] = {
            "entries": len(entries),
            "mean_compression_ratio": round(mean(ratios), 6) if ratios else None,
        }

    ecg_mean = comparison["ecg"]["mean_compression_ratio"]
    eeg_mean = comparison["eeg"]["mean_compression_ratio"]
    comparison["delta_mean_compression_ratio"] = (
        round(ecg_mean - eeg_mean, 6)
        if ecg_mean is not None and eeg_mean is not None
        else None
    )
    return comparison


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    download_root = Path(args.download_root)
    results_root = Path(args.results_root)
    dataset_payloads: list[dict[str, Any]] = []

    for dataset_name in args.dataset:
        config = DATASETS[dataset_name]
        results_dir = _dataset_results_dir(results_root, config)
        try:
            dataset_dir, download_status = _download_dataset(
                config,
                download_root,
                args.skip_download,
                args,
            )
            entries = (
                _benchmark_ecg_dataset(config, dataset_dir, args)
                if config.signal_type == "ecg"
                else _benchmark_eeg_dataset(config, dataset_dir, args)
            )
            dataset_payloads.append(
                _write_dataset_outputs(
                    config=config,
                    dataset_dir=dataset_dir,
                    results_dir=results_dir,
                    entries=entries,
                    download_status=download_status,
                )
            )
        except Exception as exc:  # pragma: no cover - exercised on real downloads
            results_dir.mkdir(parents=True, exist_ok=True)
            payload = {
                "dataset": config.dataset,
                "signal_type": config.signal_type,
                "dataset_dir": _repo_relative_path(_dataset_download_dir(download_root, config)),
                "download": {"status": "failed", "error": str(exc)},
                "aggregate": {
                    "signal_type": config.signal_type,
                    "entries_total": 0,
                    "entries_ok": 0,
                    "entries_failed": 0,
                },
                "entries": [],
            }
            (results_dir / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            (results_dir / "BENCHMARK_SUMMARY.md").write_text(
                "\n".join(
                    [
                        f"# {config.dataset} benchmark summary",
                        "",
                        f"Download failed: `{exc}`",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            dataset_payloads.append(payload)

    payload = {
        "ok": True,
        "datasets": dataset_payloads,
        "comparison": _comparison_payload(dataset_payloads),
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Benchmarked {len(dataset_payloads)} dataset(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
