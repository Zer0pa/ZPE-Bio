#!/usr/bin/env python3
"""Run Bio Wave-2 phase-6 falsification checks and emit JSON artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = ROOT / "validation" / "results"


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _base_env() -> dict[str, str]:
    env = os.environ.copy()
    pythonpath = str(ROOT / "python")
    if env.get("PYTHONPATH"):
        env["PYTHONPATH"] = f"{pythonpath}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = pythonpath
    return env


def _run_cli(args: list[str]) -> dict[str, Any]:
    cmd = [str(ROOT / ".venv" / "bin" / "python"), "-m", "zpe_bio", *args]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        env=_base_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    payload: dict[str, Any] | None = None
    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else None
    except json.JSONDecodeError:
        payload = None
    return {
        "cmd": " ".join(cmd),
        "args": args,
        "return_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "json": payload,
    }


def _is_uncaught_crash(run: dict[str, Any]) -> bool:
    if run["return_code"] not in (0, 1, 2):
        return True
    stderr = run["stderr"] or ""
    stdout = run["stdout"] or ""
    return "Traceback (most recent call last)" in stderr or "Traceback (most recent call last)" in stdout


def _dirty_campaign() -> dict[str, Any]:
    cases = [
        {
            "name": "encode_ecg_invalid_record",
            "args": ["encode-ecg", "--record-id", "999", "--json"],
            "expect_codes": [1],
        },
        {
            "name": "encode_ecg_invalid_lead",
            "args": ["encode-ecg", "--record-id", "100", "--lead-index", "-1", "--json"],
            "expect_codes": [1],
        },
        {
            "name": "encode_ecg_invalid_samples",
            "args": ["encode-ecg", "--record-id", "100", "--samples", "16", "--json"],
            "expect_codes": [1],
        },
        {
            "name": "encode_eeg_missing_file",
            "args": ["encode-eeg", "--edf", "validation/datasets/eeg/missing.edf", "--json"],
            "expect_codes": [1],
        },
        {
            "name": "benchmark_ecg_missing_ids",
            "args": ["benchmark", "--lane", "ecg", "--record-ids", ",,,", "--json"],
            "expect_codes": [1],
        },
        {
            "name": "benchmark_eeg_missing_file",
            "args": ["benchmark", "--lane", "eeg", "--edf", "validation/datasets/eeg/missing.edf", "--json"],
            "expect_codes": [1],
        },
        {
            "name": "multimodal_stream_missing_record",
            "args": ["multimodal-stream", "--record-id", "999", "--synthetic-eeg", "--json"],
            "expect_codes": [1],
        },
        {
            "name": "chemosense_argparse_error",
            "args": ["chemosense-bio", "--bogus-flag"],
            "expect_codes": [2],
        },
    ]

    rows: list[dict[str, Any]] = []
    uncaught = 0
    mismatched = 0
    for case in cases:
        run = _run_cli(case["args"])
        uncaught_crash = _is_uncaught_crash(run)
        if uncaught_crash:
            uncaught += 1
        expected = run["return_code"] in case["expect_codes"]
        if not expected:
            mismatched += 1
        error_code = None
        if isinstance(run["json"], dict):
            error = run["json"].get("error")
            if isinstance(error, dict):
                error_code = error.get("code")
        rows.append(
            {
                "name": case["name"],
                "args": case["args"],
                "expected_return_codes": case["expect_codes"],
                "return_code": run["return_code"],
                "expected_return_code_met": expected,
                "uncaught_crash": uncaught_crash,
                "error_code": error_code,
                "stdout_preview": (run["stdout"] or "").strip()[:400],
                "stderr_preview": (run["stderr"] or "").strip()[:400],
            }
        )

    return {
        "phase": 6,
        "kind": "dirty_campaign",
        "timestamp_utc": _utc_now(),
        "cases": rows,
        "summary": {
            "total_cases": len(rows),
            "uncaught_crashes": uncaught,
            "return_code_mismatches": mismatched,
            "overall_pass": uncaught == 0 and mismatched == 0,
        },
    }


def _extract_determinism_key(case_name: str, payload: dict[str, Any]) -> str:
    if case_name == "encode_ecg":
        return str(payload["metrics"]["stream_hash"])
    if case_name == "encode_eeg_synth":
        return str(payload["metrics"]["stream_hash"])
    if case_name == "benchmark_ecg":
        hashes = [row["stream_hash"] for row in payload["result"]["records"]]
        return json.dumps(hashes, separators=(",", ":"), sort_keys=False)
    if case_name == "benchmark_eeg_synth":
        return str(payload["result"]["stream_hash"])
    if case_name == "multimodal_stream_synth":
        return str(payload["result"]["stream_hash"])
    if case_name == "chemosense_bio":
        return str(payload["result"]["stream_hash"])
    raise KeyError(f"unknown case: {case_name}")


def _determinism_campaign(repeats: int) -> dict[str, Any]:
    cases = [
        {
            "name": "encode_ecg",
            "args": ["encode-ecg", "--record-id", "100", "--samples", "512", "--json"],
        },
        {
            "name": "encode_eeg_synth",
            "args": ["encode-eeg", "--synthetic-eeg", "--channels", "2", "--samples", "512", "--json"],
        },
        {
            "name": "benchmark_ecg",
            "args": ["benchmark", "--lane", "ecg", "--record-ids", "100,103", "--samples", "512", "--json"],
        },
        {
            "name": "benchmark_eeg_synth",
            "args": ["benchmark", "--lane", "eeg", "--synthetic-eeg", "--channels", "2", "--samples", "512", "--json"],
        },
        {
            "name": "multimodal_stream_synth",
            "args": [
                "multimodal-stream",
                "--record-id",
                "100",
                "--ecg-samples",
                "512",
                "--synthetic-eeg",
                "--eeg-channels",
                "2",
                "--eeg-samples",
                "512",
                "--json",
            ],
        },
        {
            "name": "chemosense_bio",
            "args": ["chemosense-bio", "--json"],
        },
    ]

    rows: list[dict[str, Any]] = []
    pass_count = 0
    for case in cases:
        keys: list[str] = []
        return_codes: list[int] = []
        failures: list[str] = []
        for idx in range(repeats):
            run = _run_cli(case["args"])
            return_codes.append(run["return_code"])
            if run["return_code"] != 0:
                failures.append(f"run[{idx}] return_code={run['return_code']}")
                continue
            if not isinstance(run["json"], dict):
                failures.append(f"run[{idx}] non-json stdout")
                continue
            try:
                keys.append(_extract_determinism_key(case["name"], run["json"]))
            except Exception as exc:  # pragma: no cover - defensive
                failures.append(f"run[{idx}] key extraction failed: {exc}")

        unique = sorted(set(keys))
        case_pass = (len(failures) == 0) and (len(unique) == 1) and (len(keys) == repeats)
        if case_pass:
            pass_count += 1
        rows.append(
            {
                "name": case["name"],
                "args": case["args"],
                "repeats": repeats,
                "return_codes": return_codes,
                "sample_count": len(keys),
                "unique_key_count": len(unique),
                "deterministic": case_pass,
                "determinism_key": unique[0] if unique else None,
                "failures": failures,
            }
        )

    return {
        "phase": 6,
        "kind": "determinism_campaign",
        "timestamp_utc": _utc_now(),
        "repeats_per_case": repeats,
        "cases": rows,
        "summary": {
            "total_cases": len(rows),
            "pass_cases": pass_count,
            "overall_pass": pass_count == len(rows),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Bio Wave-2 phase6 falsification checks.")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--dirty-json", type=Path, default=None)
    parser.add_argument("--determinism-json", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.repeats < 5:
        raise SystemExit("repeats must be >= 5")

    results_dir = args.results_dir.resolve()
    results_dir.mkdir(parents=True, exist_ok=True)
    dirty_path = (args.dirty_json or (results_dir / "bio_wave2_phase6_dirty_campaign.json")).resolve()
    determinism_path = (
        args.determinism_json or (results_dir / "bio_wave2_phase6_determinism.json")
    ).resolve()

    dirty = _dirty_campaign()
    determinism = _determinism_campaign(repeats=args.repeats)

    dirty_path.write_text(json.dumps(dirty, indent=2) + "\n", encoding="utf-8")
    determinism_path.write_text(json.dumps(determinism, indent=2) + "\n", encoding="utf-8")

    summary = {
        "dirty_overall_pass": dirty["summary"]["overall_pass"],
        "determinism_overall_pass": determinism["summary"]["overall_pass"],
        "dirty_sha256": _sha256(dirty_path),
        "determinism_sha256": _sha256(determinism_path),
    }
    print(json.dumps(summary, indent=2))

    return 0 if summary["dirty_overall_pass"] and summary["determinism_overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
