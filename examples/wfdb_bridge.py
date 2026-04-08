"""Load a WFDB record and pass it through the ZPE-Bio ECG round-trip path."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import numpy as np

from zpe_bio.codec import CodecMode
from zpe_bio.wearable_wave import roundtrip_metrics


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bridge a WFDB record into ZPE-Bio.")
    parser.add_argument("--record-id", default="100", help="WFDB record id.")
    parser.add_argument(
        "--dataset-dir",
        default=str(REPO_ROOT / "validation" / "datasets" / "mitdb"),
        help="Directory containing WFDB record files.",
    )
    parser.add_argument("--channel-index", type=int, default=0, help="Channel index to encode.")
    parser.add_argument("--samples", type=int, default=1024, help="Maximum samples to load.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    return parser.parse_args(argv)


def _signal_integrity(original: np.ndarray, reconstructed: np.ndarray) -> dict[str, object]:
    compared = min(original.shape[0], reconstructed.shape[0])
    delta = original[:compared] - reconstructed[:compared]
    return {
        "status": "pass" if compared > 0 and np.isfinite(delta).all() else "fail",
        "compared_samples": int(compared),
        "max_abs_error": round(float(np.max(np.abs(delta))) if compared else 0.0, 9),
    }


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        import wfdb
    except ImportError as exc:  # pragma: no cover - runtime dependency
        raise SystemExit(
            "WFDB is required for this example. Install with `python -m pip install -e \".[validation]\"`."
        ) from exc

    record_path = Path(args.dataset_dir) / args.record_id
    record = wfdb.rdrecord(str(record_path), sampto=args.samples)
    signal = record.p_signal[:, args.channel_index].astype(np.float64)
    _encoded, reconstructed, metrics = roundtrip_metrics(
        signal,
        signal_type="ecg",
        mode=CodecMode.CLINICAL,
        thr_mode="adaptive_rms",
    )
    payload = {
        "record_id": args.record_id,
        "dataset_dir": str(Path(args.dataset_dir)),
        "channel_index": args.channel_index,
        "sample_rate_hz": float(record.fs),
        "channels": list(record.sig_name),
        "samples": int(metrics["samples"]),
        "compression_ratio": float(metrics["compression_ratio"]),
        "prd_percent": float(metrics["prd_percent"]),
        "snr_db": float(metrics["snr_db"]),
        "signal_integrity": _signal_integrity(signal, reconstructed),
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"WFDB bridge {args.record_id}: CR={payload['compression_ratio']:.6f} "
            f"PRD={payload['prd_percent']:.6f}% integrity={payload['signal_integrity']['status']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
