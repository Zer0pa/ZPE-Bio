"""Generate per-record MIT-BIH benchmark artifacts and an aggregate summary."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

import numpy as np

from zpe_bio.bio_wave2 import ecg_roundtrip_metrics, load_mitbih_record
from zpe_bio.codec import CodecMode
from zpe_bio.wearable_wave import snr_db

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_RESULTS_DIR = REPO_ROOT / "validation" / "results"
DEFAULT_RECORDS_DIR = DEFAULT_RESULTS_DIR / "mitdb_python_only"
DEFAULT_SUMMARY_MD = DEFAULT_RESULTS_DIR / "BENCHMARK_SUMMARY.md"
DEFAULT_AGGREGATE_JSON = DEFAULT_RECORDS_DIR / "mitdb_aggregate.json"
DEFAULT_SUMMARY_CSV = DEFAULT_RECORDS_DIR / "mitdb_summary.csv"

ARRHYTHMIA_KEYWORDS = (
    "atrial fibrillation",
    "atrial flutter",
    "bigeminy",
    "block",
    "bradycardia",
    "bundle branch",
    "ectopic",
    "flutter",
    "idioventricular",
    "junctional",
    "paced",
    "pacemaker",
    "pvc",
    "tachycardia",
    "trigeminy",
    "ventricular",
)

NORMAL_SINUS_HINTS = (
    "normal sinus rhythm",
    "sinus rhythm",
)


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run CPU-only MIT-BIH benchmarks and write per-record + summary artifacts."
    )
    parser.add_argument(
        "--dataset-dir",
        default=str(REPO_ROOT / "validation" / "datasets" / "mitdb"),
        help="Directory containing MIT-BIH record files.",
    )
    parser.add_argument(
        "--record-ids",
        default="all",
        help="Comma-separated MIT-BIH ids to benchmark, or 'all'.",
    )
    parser.add_argument("--lead-index", type=int, default=0, help="Lead index to encode.")
    parser.add_argument("--samples", type=int, default=10000, help="Maximum samples per record.")
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in CodecMode],
        default=CodecMode.CLINICAL.value,
        help="Codec mode to benchmark.",
    )
    parser.add_argument(
        "--thr-mode",
        choices=["fixed", "adaptive_rms"],
        default="adaptive_rms",
        help="Thresholding mode.",
    )
    parser.add_argument("--threshold", type=float, default=None, help="Explicit threshold override.")
    parser.add_argument("--step", type=float, default=None, help="Explicit quantisation step override.")
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_RECORDS_DIR),
        help="Directory for per-record JSON outputs and aggregate JSON/CSV.",
    )
    parser.add_argument(
        "--summary-md",
        default=str(DEFAULT_SUMMARY_MD),
        help="Markdown summary report path.",
    )
    parser.add_argument(
        "--aggregate-json",
        default=str(DEFAULT_AGGREGATE_JSON),
        help="Aggregate JSON output path.",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(DEFAULT_SUMMARY_CSV),
        help="CSV rollup path.",
    )
    return parser.parse_args(argv)


def _available_record_ids(dataset_dir: Path) -> list[str]:
    return sorted(path.stem for path in dataset_dir.glob("*.hea"))


def _requested_record_ids(raw_value: str, dataset_dir: Path) -> list[str]:
    available = _available_record_ids(dataset_dir)
    if raw_value.strip().lower() == "all":
        return available

    requested = [item.strip() for item in raw_value.split(",") if item.strip()]
    missing = sorted(set(requested) - set(available))
    if missing:
        missing_text = ", ".join(missing)
        raise SystemExit(f"Unknown MIT-BIH record id(s): {missing_text}")
    return requested


def _read_header_lines(dataset_dir: Path, record_id: str) -> list[str]:
    header_path = dataset_dir / f"{record_id}.hea"
    return header_path.read_text(encoding="utf-8").splitlines()


def _demographics_from_header(lines: list[str]) -> dict[str, Any]:
    for line in lines:
        if not line.startswith("# "):
            continue
        tokens = line[2:].split()
        if len(tokens) < 2:
            continue
        if not tokens[0].isdigit():
            continue
        return {"age_years": int(tokens[0]), "sex": tokens[1]}
    return {"age_years": None, "sex": None}


def _record_comment_lines(lines: list[str]) -> list[str]:
    comments: list[str] = []
    for index, line in enumerate(lines):
        if not line.startswith("# "):
            continue
        content = line[2:].strip()
        if index == 3 and content:
            parts = content.split()
            if len(parts) >= 2 and parts[0].isdigit():
                continue
        comments.append(content)
    return comments


def _diagnosis_bucket(comment_text: str) -> str:
    text = comment_text.lower()
    if any(hint in text for hint in NORMAL_SINUS_HINTS) and not any(
        keyword in text for keyword in ARRHYTHMIA_KEYWORDS
    ):
        return "normal_sinus_rhythm"
    if any(keyword in text for keyword in ARRHYTHMIA_KEYWORDS):
        return "arrhythmia_or_conduction_disorder"
    return "normal_or_unannotated"


def _signal_integrity(original: np.ndarray, reconstructed: np.ndarray) -> dict[str, Any]:
    original_finite = bool(np.isfinite(original).all())
    reconstructed_finite = bool(np.isfinite(reconstructed).all())
    compared_samples = min(len(original), len(reconstructed))
    compared_original = original[:compared_samples]
    compared_reconstructed = reconstructed[:compared_samples]
    delta = compared_original - compared_reconstructed
    max_abs_error_uv = float(np.max(np.abs(delta)) * 1000.0) if compared_samples else 0.0
    return {
        "status": "pass" if original_finite and reconstructed_finite and compared_samples > 0 else "fail",
        "original_finite": original_finite,
        "reconstructed_finite": reconstructed_finite,
        "compared_samples": compared_samples,
        "length_match": len(original) == len(reconstructed),
        "max_abs_error_uv": round(max_abs_error_uv, 6),
    }


def _rmse_uv(original: np.ndarray, reconstructed: np.ndarray) -> float:
    compared_samples = min(len(original), len(reconstructed))
    if compared_samples == 0:
        return 0.0
    err_millivolts = math.sqrt(
        float(np.mean((original[:compared_samples] - reconstructed[:compared_samples]) ** 2))
    )
    return err_millivolts * 1000.0


def _record_payload(
    record_id: str,
    dataset_dir: Path,
    lead_index: int,
    samples: int,
    mode: CodecMode,
    thr_mode: str,
    threshold: float | None,
    step: float | None,
) -> dict[str, Any]:
    header_lines = _read_header_lines(dataset_dir, record_id)
    loaded = load_mitbih_record(
        record_id=record_id,
        lead_index=lead_index,
        max_samples=samples,
        dataset_dir=dataset_dir,
    )
    encoded, reconstructed, metrics = ecg_roundtrip_metrics(
        loaded["signal"],
        mode=mode,
        thr_mode=thr_mode,
        threshold=threshold,
        step=step,
    )
    comments = _record_comment_lines(header_lines)
    comment_text = " ".join(comments)
    integrity = _signal_integrity(loaded["signal"], reconstructed)

    return {
        "ok": True,
        "record_id": record_id,
        "lead_index": lead_index,
        "sample_rate_hz": loaded["sample_rate_hz"],
        "mode": encoded.mode.value,
        "thr_mode": encoded.thr_mode,
        "threshold": float(encoded.threshold),
        "step": float(encoded.step),
        "metrics": {
            **metrics,
            "encode_time_us": round(metrics["encode_ms"] * 1000.0, 3),
            "decode_time_us": round(metrics["decode_ms"] * 1000.0, 3),
            "snr_db": round(float(snr_db(loaded["signal"], reconstructed)), 6),
            "rmse_uv": round(_rmse_uv(loaded["signal"], reconstructed), 6),
        },
        "signal_integrity": integrity,
        "header_metadata": {
            **_demographics_from_header(header_lines),
            "comment_lines": comments,
            "comment_text": comment_text,
            "diagnosis_bucket": _diagnosis_bucket(comment_text),
        },
    }


def _aggregate_payload(records: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    compression_ratios = [record["metrics"]["compression_ratio"] for record in records]
    snr_values = [record["metrics"]["snr_db"] for record in records]
    rmse_values = [record["metrics"]["rmse_uv"] for record in records]
    encode_us = [record["metrics"]["encode_time_us"] for record in records]
    decode_us = [record["metrics"]["decode_time_us"] for record in records]
    prd_values = [record["metrics"]["prd_percent"] for record in records]

    diagnosis_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        diagnosis_groups[record["header_metadata"]["diagnosis_bucket"]].append(record)

    by_diagnosis = []
    for diagnosis, grouped_records in sorted(diagnosis_groups.items()):
        grouped_cr = [record["metrics"]["compression_ratio"] for record in grouped_records]
        grouped_snr = [record["metrics"]["snr_db"] for record in grouped_records]
        grouped_rmse = [record["metrics"]["rmse_uv"] for record in grouped_records]
        by_diagnosis.append(
            {
                "diagnosis_bucket": diagnosis,
                "records": len(grouped_records),
                "mean_compression_ratio": round(mean(grouped_cr), 6),
                "median_compression_ratio": round(median(grouped_cr), 6),
                "mean_snr_db": round(mean(grouped_snr), 6),
                "mean_rmse_uv": round(mean(grouped_rmse), 6),
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_dir": _display_path(Path(args.dataset_dir)),
        "mode": args.mode,
        "thr_mode": args.thr_mode,
        "threshold": args.threshold,
        "step": args.step,
        "lead_index": args.lead_index,
        "samples": args.samples,
        "records_processed": len(records),
        "summary": {
            "compression_ratio_mean": round(mean(compression_ratios), 6),
            "compression_ratio_median": round(median(compression_ratios), 6),
            "compression_ratio_min": round(min(compression_ratios), 6),
            "compression_ratio_max": round(max(compression_ratios), 6),
            "snr_db_mean": round(mean(snr_values), 6),
            "snr_db_min": round(min(snr_values), 6),
            "snr_db_max": round(max(snr_values), 6),
            "rmse_uv_mean": round(mean(rmse_values), 6),
            "rmse_uv_min": round(min(rmse_values), 6),
            "rmse_uv_max": round(max(rmse_values), 6),
            "encode_time_us_mean": round(mean(encode_us), 3),
            "decode_time_us_mean": round(mean(decode_us), 3),
            "prd_percent_mean": round(mean(prd_values), 6),
            "prd_percent_max": round(max(prd_values), 6),
            "integrity_pass_count": sum(
                1 for record in records if record["signal_integrity"]["status"] == "pass"
            ),
        },
        "by_diagnosis_bucket": by_diagnosis,
        "records": records,
    }


def _write_record_jsons(records: list[dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for record in records:
        output_path = out_dir / f"mitdb_{record['record_id']}.json"
        output_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def _write_summary_csv(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "record_id",
        "diagnosis_bucket",
        "compression_ratio",
        "snr_db",
        "rmse_uv",
        "prd_percent",
        "encode_time_us",
        "decode_time_us",
        "integrity_status",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "record_id": record["record_id"],
                    "diagnosis_bucket": record["header_metadata"]["diagnosis_bucket"],
                    "compression_ratio": record["metrics"]["compression_ratio"],
                    "snr_db": record["metrics"]["snr_db"],
                    "rmse_uv": record["metrics"]["rmse_uv"],
                    "prd_percent": record["metrics"]["prd_percent"],
                    "encode_time_us": record["metrics"]["encode_time_us"],
                    "decode_time_us": record["metrics"]["decode_time_us"],
                    "integrity_status": record["signal_integrity"]["status"],
                }
            )


def _write_summary_markdown(
    aggregate: dict[str, Any],
    output_path: Path,
    records_dir: Path,
    aggregate_json_path: Path,
    summary_csv_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = aggregate["summary"]
    lines = [
        "# MIT-BIH Python-Only Benchmark Summary",
        "",
        f"Generated: `{aggregate['generated_at']}`",
        f"Dataset: `{aggregate['dataset_dir']}`",
        f"Records processed: `{aggregate['records_processed']}`",
        f"Mode: `{aggregate['mode']}` | Threshold mode: `{aggregate['thr_mode']}`",
        "",
        "## Aggregate",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Mean compression ratio | {summary['compression_ratio_mean']:.6f} |",
        f"| Median compression ratio | {summary['compression_ratio_median']:.6f} |",
        f"| Min compression ratio | {summary['compression_ratio_min']:.6f} |",
        f"| Max compression ratio | {summary['compression_ratio_max']:.6f} |",
        f"| Mean SNR (dB) | {summary['snr_db_mean']:.6f} |",
        f"| Mean RMSE (uV) | {summary['rmse_uv_mean']:.6f} |",
        f"| Mean encode time (us) | {summary['encode_time_us_mean']:.3f} |",
        f"| Mean decode time (us) | {summary['decode_time_us_mean']:.3f} |",
        f"| Mean PRD (%) | {summary['prd_percent_mean']:.6f} |",
        f"| Max PRD (%) | {summary['prd_percent_max']:.6f} |",
        f"| Integrity passes | {summary['integrity_pass_count']}/{aggregate['records_processed']} |",
        "",
        "## By Diagnosis Bucket",
        "",
        (
            "Diagnosis grouping is derived from MIT-BIH header comment text. "
            "Records without explicit normal-sinus phrasing remain in "
            "`normal_or_unannotated` rather than being relabeled."
        ),
        "",
        "| Diagnosis bucket | Records | Mean CR | Median CR | Mean SNR (dB) | Mean RMSE (uV) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in aggregate["by_diagnosis_bucket"]:
        lines.append(
            f"| {row['diagnosis_bucket']} | {row['records']} | "
            f"{row['mean_compression_ratio']:.6f} | {row['median_compression_ratio']:.6f} | "
            f"{row['mean_snr_db']:.6f} | {row['mean_rmse_uv']:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Per-Record Table",
            "",
            "| Record | Diagnosis bucket | CR | SNR (dB) | RMSE (uV) | Encode (us) | Decode (us) | Integrity |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )

    for record in aggregate["records"]:
        metrics = record["metrics"]
        lines.append(
            f"| {record['record_id']} | {record['header_metadata']['diagnosis_bucket']} | "
            f"{metrics['compression_ratio']:.6f} | {metrics['snr_db']:.6f} | {metrics['rmse_uv']:.6f} | "
            f"{metrics['encode_time_us']:.3f} | {metrics['decode_time_us']:.3f} | "
            f"{record['signal_integrity']['status']} |"
        )

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Per-record JSON: `{_display_path(records_dir)}`",
            f"- Aggregate JSON: `{_display_path(aggregate_json_path)}`",
            f"- Summary CSV: `{_display_path(summary_csv_path)}`",
            "",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    dataset_dir = Path(args.dataset_dir)
    if not dataset_dir.exists():
        raise SystemExit(f"Dataset directory not found: {dataset_dir}")

    out_dir = Path(args.out_dir)
    aggregate_json_path = Path(args.aggregate_json)
    summary_md_path = Path(args.summary_md)
    summary_csv_path = Path(args.summary_csv)

    record_ids = _requested_record_ids(args.record_ids, dataset_dir)
    mode = CodecMode(args.mode)

    records = [
        _record_payload(
            record_id=record_id,
            dataset_dir=dataset_dir,
            lead_index=args.lead_index,
            samples=args.samples,
            mode=mode,
            thr_mode=args.thr_mode,
            threshold=args.threshold,
            step=args.step,
        )
        for record_id in record_ids
    ]

    aggregate = _aggregate_payload(records, args)
    _write_record_jsons(records, out_dir)
    summary_csv_path.parent.mkdir(parents=True, exist_ok=True)
    aggregate_json_path.parent.mkdir(parents=True, exist_ok=True)
    aggregate_json_path.write_text(json.dumps(aggregate, indent=2) + "\n", encoding="utf-8")
    _write_summary_csv(records, summary_csv_path)
    _write_summary_markdown(
        aggregate=aggregate,
        output_path=summary_md_path,
        records_dir=out_dir,
        aggregate_json_path=aggregate_json_path,
        summary_csv_path=summary_csv_path,
    )

    print(
        json.dumps(
            {
                "ok": True,
                "records_processed": len(records),
                "out_dir": str(out_dir),
                "aggregate_json": str(aggregate_json_path),
                "summary_md": str(summary_md_path),
                "summary_csv": str(summary_csv_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
