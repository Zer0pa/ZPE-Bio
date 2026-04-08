"""Compress a staged MIT-BIH record and report round-trip metrics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from zpe_bio.bio_wave2 import ecg_roundtrip_metrics, load_mitbih_record
from zpe_bio.codec import CodecMode
from zpe_bio.wearable_wave import snr_db


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compress a MIT-BIH record with ZPE-Bio.")
    parser.add_argument("--record-id", default="100", help="MIT-BIH record id.")
    parser.add_argument(
        "--dataset-dir",
        default=str(REPO_ROOT / "validation" / "datasets" / "mitdb"),
        help="Directory containing MIT-BIH files.",
    )
    parser.add_argument("--lead-index", type=int, default=0, help="Lead index to encode.")
    parser.add_argument("--samples", type=int, default=1024, help="Maximum samples to load.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    loaded = load_mitbih_record(
        record_id=args.record_id,
        lead_index=args.lead_index,
        max_samples=args.samples,
        dataset_dir=Path(args.dataset_dir),
    )
    _encoded, reconstructed, metrics = ecg_roundtrip_metrics(
        loaded["signal"],
        mode=CodecMode.CLINICAL,
        thr_mode="adaptive_rms",
    )
    payload = {
        "record_id": args.record_id,
        "dataset_dir": str(Path(args.dataset_dir)),
        "sample_rate_hz": loaded["sample_rate_hz"],
        "lead_index": args.lead_index,
        "samples": int(metrics["samples"]),
        "compression_ratio": float(metrics["compression_ratio"]),
        "prd_percent": float(metrics["prd_percent"]),
        "snr_db": round(float(snr_db(loaded["signal"], reconstructed)), 6),
        "raw_bytes": int(metrics["raw_bytes"]),
        "zpe_bytes_est": int(metrics["zpe_bytes_est"]),
        "gzip_bytes": int(metrics["gzip_bytes"]),
        "stream_hash": metrics["stream_hash"],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"MIT-BIH {args.record_id}: CR={payload['compression_ratio']:.6f} PRD={payload['prd_percent']:.6f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
