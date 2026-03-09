"""
MIT-BIH Arrhythmia Database validation runner.
PRD Reference: §2.1 Golden Benchmark
DTs exercised: DT-1 (Shape Destruction), DT-2 (Compression Regret)

Runs the codec on all 48 MIT-BIH records and reports aggregate metrics.
"""
import json
import wfdb
import numpy as np
from pathlib import Path
from datetime import datetime, timezone

from zpe_bio.codec import encode, decode, compute_prd, compute_rmse, CodecMode

MIT_BIH_DIR = Path(__file__).resolve().parents[1] / "datasets" / "mitdb"
RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"

# All 48 MIT-BIH records
MIT_BIH_RECORDS = [
    "100", "101", "102", "103", "104", "105", "106", "107",
    "108", "109", "111", "112", "113", "114", "115", "116",
    "117", "118", "119", "121", "122", "123", "124",
    "200", "201", "202", "203", "205", "207", "208",
    "209", "210", "212", "213", "214", "215", "217",
    "219", "220", "221", "222", "223", "228", "230",
    "231", "232", "233", "234",
]


def run_single_record(record_id: str, mode: CodecMode = CodecMode.CLINICAL, thr_mode: str = "fixed") -> dict:
    """Encode and decode a single MIT-BIH record using ratified Mode Split."""
    record_path = str(MIT_BIH_DIR / record_id)
    record = wfdb.rdrecord(record_path)
    
    # Use first channel (MLII lead)
    signal = record.p_signal[:, 0]
    fs = record.fs
    
    # Encode with specified mode presets
    encoded = encode(signal, mode=mode, thr_mode=thr_mode, signal_type="ecg")
    
    # Decode
    reconstructed = decode(encoded)
    
    # Compute metrics
    min_len = min(len(signal), len(reconstructed))
    sig = signal[:min_len]
    rec = reconstructed[:min_len]
    
    prd = compute_prd(sig, rec)
    rmse = compute_rmse(sig, rec)
    cr = encoded.compression_ratio
    
    return {
        "record_id": record_id,
        "mode": mode.value,
        "num_samples": len(signal),
        "num_tokens": encoded.num_tokens,
        "compression_ratio": round(cr, 3),
        "prd_percent": round(prd, 3),
        "rmse_normalised": round(rmse, 6),
        "threshold": encoded.threshold,
        "thr_mode": thr_mode,
        "sample_rate_original": fs,
    }


def run_all(mode: CodecMode = CodecMode.CLINICAL, thr_mode: str = "fixed") -> dict:
    """Run golden benchmark on all 48 records for a specific mode."""
    results = []
    errors = []
    
    print(f"Running MIT-BIH Golden Benchmark (Mode: {mode.value}, {thr_mode} threshold)...")
    print(f"Dataset: {MIT_BIH_DIR}")
    print(f"Records: {len(MIT_BIH_RECORDS)}")
    print("-" * 60)
    
    for i, rec_id in enumerate(MIT_BIH_RECORDS):
        try:
            result = run_single_record(rec_id, mode=mode, thr_mode=thr_mode)
            results.append(result)
            # Use canonical mode-relative passing criteria.
            if mode == CodecMode.CLINICAL:
                # Fidelity Gate (Clinical): PRD < 5%
                passed = result["prd_percent"] < 5.0
            else:
                # Transport Gate
                passed = result["compression_ratio"] >= 5.0
                
            status = "PASS" if passed else "FAIL"
            print(f"  [{i+1:2d}/48] {rec_id}: CR={result['compression_ratio']:.2f}×  PRD={result['prd_percent']:.1f}%  [{status}]")
        except Exception as e:
            errors.append({"record_id": rec_id, "error": str(e)})
            print(f"  [{i+1:2d}/48] {rec_id}: ERROR — {e}")
    
    # Aggregate
    if results:
        crs = [r["compression_ratio"] for r in results]
        prds = [r["prd_percent"] for r in results]
        
        aggregate = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": mode.value,
            "thr_mode": thr_mode,
            "records_processed": len(results),
            "records_failed": len(errors),
            "cr_mean": round(float(np.mean(crs)), 3),
            "cr_min": round(float(np.min(crs)), 3),
            "cr_max": round(float(np.max(crs)), 3),
            "prd_mean": round(float(np.mean(prds)), 3),
            "prd_max": round(float(np.max(prds)), 3),
            "dt1_pass": all(p < 5.0 for p in prds) if mode == CodecMode.CLINICAL else False,
            "dt2_cr_pass": float(np.mean(crs)) >= 5.0 if mode == CodecMode.TRANSPORT else False,
            "results": results,
            "errors": errors,
        }
    else:
        aggregate = {"error": "No records processed", "errors": errors}
    
    print("-" * 60)
    print(f"Mode: {mode.value.upper()}")
    print(f"CR: {aggregate.get('cr_mean', 'N/A')}× (min={aggregate.get('cr_min', 'N/A')}, max={aggregate.get('cr_max', 'N/A')})")
    print(f"PRD: {aggregate.get('prd_mean', 'N/A')}% (max={aggregate.get('prd_max', 'N/A')})")
    
    return aggregate


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MIT-BIH validation runner")
    parser.add_argument("--mode", default="clinical", choices=["clinical", "transport"], help="Codec mode")
    parser.add_argument("--thr-mode", default="fixed")
    parser.add_argument("--output", default=None, help="JSON output path")
    args = parser.parse_args()
    
    mode_obj = CodecMode(args.mode)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results = run_all(mode=mode_obj, thr_mode=args.thr_mode)
    
    output_path = args.output or str(RESULTS_DIR / f"mit_bih_{args.mode}_{datetime.now().strftime('%Y%mT%H%M%S')}.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")
