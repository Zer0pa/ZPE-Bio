"""
Compute the CR/PRD Pareto frontier on MIT-BIH for fixed thresholds.

This script is the canonical Phase 1 rescue artifact when PT-1 and PT-2
fire together. It produces a JSON file consumable by RUNBOOK_01 Step 2.5.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import wfdb

from zpe_bio.codec import encode, decode, compute_prd

MIT_BIH_RECORDS = [
    "100",
    "101",
    "102",
    "103",
    "104",
    "105",
    "106",
    "107",
    "108",
    "109",
    "111",
    "112",
    "113",
    "114",
    "115",
    "116",
    "117",
    "118",
    "119",
    "121",
    "122",
    "123",
    "124",
    "200",
    "201",
    "202",
    "203",
    "205",
    "207",
    "208",
    "209",
    "210",
    "212",
    "213",
    "214",
    "215",
    "217",
    "219",
    "220",
    "221",
    "222",
    "223",
    "228",
    "230",
    "231",
    "232",
    "233",
    "234",
]

DEFAULT_THRESHOLDS = [0.005, 0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.15, 0.2]


@dataclass
class FrontierPoint:
    threshold: float
    cr_mean: float
    cr_min: float
    cr_max: float
    prd_mean: float
    prd_max: float
    dt1_pass: bool
    dt2_pass: bool
    records_prd_lt_5: int


def evaluate_threshold(dataset_dir: Path, threshold: float) -> FrontierPoint:
    crs: list[float] = []
    prds: list[float] = []

    for rec_id in MIT_BIH_RECORDS:
        signal = wfdb.rdrecord(str(dataset_dir / rec_id)).p_signal[:, 0]
        encoded = encode(
            signal,
            threshold=threshold,
            step=threshold,
            thr_mode="fixed",
            signal_type="ecg",
        )
        reconstructed = decode(encoded)
        length = min(len(signal), len(reconstructed))
        prd = compute_prd(signal[:length], reconstructed[:length])
        crs.append(float(encoded.compression_ratio))
        prds.append(float(prd))

    cr_array = np.array(crs, dtype=np.float64)
    prd_array = np.array(prds, dtype=np.float64)
    return FrontierPoint(
        threshold=threshold,
        cr_mean=float(np.mean(cr_array)),
        cr_min=float(np.min(cr_array)),
        cr_max=float(np.max(cr_array)),
        prd_mean=float(np.mean(prd_array)),
        prd_max=float(np.max(prd_array)),
        dt1_pass=bool(np.all(prd_array < 5.0)),
        dt2_pass=bool(np.mean(cr_array) >= 5.0),
        records_prd_lt_5=int(np.sum(prd_array < 5.0)),
    )


def classify(points: list[FrontierPoint]) -> str:
    if any(p.dt1_pass and p.dt2_pass for p in points):
        return "TUNE_POSSIBLE"

    has_fidelity_zone = any(p.prd_mean < 8.0 for p in points)
    has_compression_zone = any(p.cr_mean >= 5.0 for p in points)

    if has_fidelity_zone and has_compression_zone:
        return "MODE_SPLIT_REQUIRED"
    return "ARCHITECTURE_BREAK"


def main() -> None:
    parser = argparse.ArgumentParser(description="MIT-BIH CR/PRD Pareto frontier")
    parser.add_argument(
        "--dataset-dir",
        default="validation/datasets/mitdb",
        help="Directory containing MIT-BIH records",
    )
    parser.add_argument(
        "--thresholds",
        nargs="*",
        type=float,
        default=DEFAULT_THRESHOLDS,
        help="Thresholds to evaluate",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path (default under validation/results)",
    )
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    points = [evaluate_threshold(dataset_dir, thr) for thr in args.thresholds]
    decision = classify(points)

    results_dir = Path("validation/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc)
    output_path = (
        Path(args.output)
        if args.output
        else results_dir / f"pareto_frontier_{timestamp.strftime('%Y%m%dT%H%M%SZ')}.json"
    )

    payload = {
        "timestamp": timestamp.isoformat(),
        "dataset_dir": str(dataset_dir),
        "records": len(MIT_BIH_RECORDS),
        "thresholds": args.thresholds,
        "decision": decision,
        "points": [asdict(p) for p in points],
    }
    output_path.write_text(json.dumps(payload, indent=2))

    print(f"Decision: {decision}")
    print("thr\tcr_mean\tprd_mean\tdt1\tdt2")
    for point in points:
        print(
            f"{point.threshold:.4f}\t{point.cr_mean:.3f}\t{point.prd_mean:.3f}\t"
            f"{point.dt1_pass}\t{point.dt2_pass}"
        )
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
