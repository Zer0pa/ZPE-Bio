"""
Generate a consolidated Phase 3 host-side evidence report.

Runs/collects:
- Embedded thumb compile
- DT-6, DT-9, DT-10, DT-13, DT-17
- Stack proxy unit test

Writes JSON to validation/results/phase3_hostok_<timestamp>.json
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "validation" / "results"


def run(cmd: list[str], cwd: Path | None = None) -> dict:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "cwd": str(cwd) if cwd else str(REPO_ROOT),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def parse_float(pattern: str, text: str) -> float | None:
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def parse_int(pattern: str, text: str) -> int | None:
    m = re.search(pattern, text)
    return int(m.group(1)) if m else None


def main() -> None:
    commands = {}

    commands["compile_thumb"] = run(
        ["cargo", "build", "--release", "--target", "thumbv8m.main-none-eabi"],
        cwd=REPO_ROOT / "embedded" / "nrf5340",
    )

    python_exe = str(REPO_ROOT / ".venv" / "bin" / "python")
    commands["dt06"] = run([python_exe, "validation/destruct_tests/dt06_ram_budget.py"], cwd=REPO_ROOT)
    commands["dt09"] = run([python_exe, "validation/destruct_tests/dt09_power_regression.py"], cwd=REPO_ROOT)
    commands["dt10"] = run([python_exe, "validation/destruct_tests/dt10_latency.py"], cwd=REPO_ROOT)
    commands["dt13"] = run([python_exe, "validation/destruct_tests/dt13_cross_platform.py"], cwd=REPO_ROOT)
    commands["dt17"] = run([python_exe, "validation/destruct_tests/dt17_packet_framing.py"], cwd=REPO_ROOT)

    commands["stack_proxy"] = run(
        ["cargo", "test", "embedded_stack_proxy_within_budget", "--", "--nocapture"],
        cwd=REPO_ROOT / "core" / "rust",
    )

    dt06_out = commands["dt06"]["stdout"]
    dt09_out = commands["dt09"]["stdout"]
    dt10_out = commands["dt10"]["stdout"]
    dt17_out = commands["dt17"]["stdout"]
    stack_out = commands["stack_proxy"]["stdout"]

    metrics = {
        "dt06_data_bytes": parse_int(r"\.data:\s+([0-9]+)", dt06_out),
        "dt06_bss_bytes": parse_int(r"\.bss:\s+([0-9]+)", dt06_out),
        "dt06_uninit_bytes": parse_int(r"\.uninit:\s+([0-9]+)", dt06_out),
        "dt06_static_ram_bytes": parse_int(r"Static RAM total:\s+([0-9]+)", dt06_out),
        "dt09_mean_tx_reduction_x": parse_float(r"Mean estimated reduction:\s+([0-9.]+)x", dt09_out),
        "dt09_min_tx_reduction_x": parse_float(r"Min estimated reduction:\s+([0-9.]+)x", dt09_out),
        "dt10_mean_latency_ms": parse_float(r"Mean latency:\s+([0-9.]+) ms", dt10_out),
        "dt10_p99_latency_ms": parse_float(r"P99 latency:\s+([0-9.]+) ms", dt10_out),
        "dt17_detection_percent": parse_float(r"Detection rate:\s+([0-9.]+)%", dt17_out),
        "stack_proxy_bytes": parse_int(r"embedded_stack_proxy_bytes=([0-9]+)", stack_out),
    }

    statuses = {
        name: (entry["returncode"] == 0)
        for name, entry in commands.items()
    }

    overall_pass = all(statuses.values())

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "Phase 3 Embedded (Host-OK)",
        "overall_pass": overall_pass,
        "statuses": statuses,
        "metrics": metrics,
        "commands": {
            k: {
                "cmd": v["cmd"],
                "cwd": v["cwd"],
                "returncode": v["returncode"],
                "stdout_tail": v["stdout"][-2000:],
                "stderr_tail": v["stderr"][-2000:],
            }
            for k, v in commands.items()
        },
        "notes": [
            "DT-9 and DT-10 are host-side proxies pending hardware timer/PPK2 confirmation.",
            "DT-13 includes ARM compile audit plus host byte-parity check.",
        ],
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"phase3_hostok_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    out_path.write_text(json.dumps(report, indent=2))

    print(f"overall_pass={overall_pass}")
    print(f"out_path={out_path}")

    if overall_pass:
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
