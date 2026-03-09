"""
Master DT runner. Execute ALL destruct tests and report pass/fail.

Usage:
  python run_all_dts.py                  # run ALL DTs
  python run_all_dts.py --priority P0    # run only P0 DTs
  python run_all_dts.py --dt 1 5 15      # run specific DTs
"""
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

DT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = DT_DIR.parent / "results"

DT_PRIORITY = {
    1: "P0", 2: "P0", 3: "P0", 4: "P0", 5: "P0",
    6: "P0", 7: "P0", 8: "P1", 9: "P1", 10: "P1",
    11: "P1", 12: "P1", 13: "P1", 14: "P2",
    15: "P0", 16: "P0", 17: "P1",
}

DT_NAMES = {
    1: "Shape Destruction", 2: "Compression Regret", 3: "Determinism",
    4: "Noise Injection", 5: "Pathological", 6: "RAM Budget",
    7: "Latch Freedom", 8: "DC Torture", 9: "Power Regression",
    10: "Latency", 11: "Formal Spec", 12: "Monotonicity",
    13: "Cross-Platform", 14: "Side-Channel", 15: "Adaptive Threshold ECG",
    16: "PPG Codec", 17: "Packet Framing",
}


def find_dt_script(dt_num: int) -> Path:
    """Find the script for a given DT number."""
    prefix = f"dt{dt_num:02d}_"
    scripts = list(DT_DIR.glob(f"{prefix}*.py"))
    if not scripts:
        return None
    return scripts[0]


def run_dt(dt_num: int) -> dict:
    """Run a single DT and capture result."""
    script = find_dt_script(dt_num)
    if script is None or "placeholder" in script.name:
        return {
            "dt": dt_num,
            "name": DT_NAMES.get(dt_num, "Unknown"),
            "priority": DT_PRIORITY.get(dt_num, "?"),
            "status": "NOT_IMPLEMENTED",
            "output": "",
        }
    
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, timeout=900,
            cwd=str(DT_DIR.parent.parent),  # zpe-bio root
        )
        passed = result.returncode == 0
        return {
            "dt": dt_num,
            "name": DT_NAMES.get(dt_num, "Unknown"),
            "priority": DT_PRIORITY.get(dt_num, "?"),
            "status": "PASS" if passed else "FAIL",
            "output": (result.stdout + result.stderr)[-2000:],  # last 2000 chars
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "dt": dt_num,
            "name": DT_NAMES.get(dt_num, "Unknown"),
            "priority": DT_PRIORITY.get(dt_num, "?"),
            "status": "TIMEOUT",
            "output": "Exceeded 600s timeout",
        }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--priority", choices=["P0", "P1", "P2"], default=None)
    parser.add_argument("--dt", nargs="+", type=int, default=None)
    args = parser.parse_args()
    
    dts_to_run = list(range(1, 18))
    if args.dt:
        dts_to_run = args.dt
    elif args.priority:
        dts_to_run = [n for n in dts_to_run if DT_PRIORITY.get(n) == args.priority]
    
    results = []
    print(f"{'DT':>4}  {'Name':<25}  {'Pri':>3}  {'Status':<15}")
    print("-" * 55)
    
    for dt_num in dts_to_run:
        r = run_dt(dt_num)
        results.append(r)
        emoji = {"PASS": "✅", "FAIL": "❌", "NOT_IMPLEMENTED": "⬜", "TIMEOUT": "⏰"}.get(r["status"], "❓")
        print(f"  {r['dt']:2d}   {r['name']:<25}  {r['priority']:>3}  {r['status']:<11} {emoji}")
    
    print("-" * 55)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    not_impl = sum(1 for r in results if r["status"] == "NOT_IMPLEMENTED")
    print(f"Total: {passed} passed, {failed} failed, {not_impl} not implemented")
    
    # P0 gate
    p0_fails = [r for r in results if r["priority"] == "P0" and r["status"] == "FAIL"]
    if p0_fails:
        print("\n⚠️  P0 GATE FAILED. Do NOT proceed to next phase.")
        for r in p0_fails:
            print(f"   DT-{r['dt']} ({r['name']}): {r['status']}")
    else:
        p0_count = sum(1 for r in results if r["priority"] == "P0" and r["status"] == "PASS")
        if p0_count > 0:
            print(f"\n✅ P0 GATE PASSED ({p0_count} DTs)")
    
    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"dt_results_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    with open(out_path, "w") as f:
        json.dump({"timestamp": datetime.now(timezone.utc).isoformat(), "results": results}, f, indent=2)
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
