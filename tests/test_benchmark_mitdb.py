from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_benchmark_mitdb_script_writes_expected_artifacts(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "benchmark_mitdb.py"
    out_dir = tmp_path / "mitdb_python_only"
    summary_md = tmp_path / "BENCHMARK_SUMMARY.md"
    aggregate_json = out_dir / "mitdb_aggregate.json"
    summary_csv = out_dir / "mitdb_summary.csv"

    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--record-ids",
            "100",
            "--samples",
            "512",
            "--out-dir",
            str(out_dir),
            "--summary-md",
            str(summary_md),
            "--aggregate-json",
            str(aggregate_json),
            "--summary-csv",
            str(summary_csv),
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["records_processed"] == 1
    assert Path(payload["out_dir"]) == out_dir
    assert Path(payload["aggregate_json"]) == aggregate_json
    assert Path(payload["summary_md"]) == summary_md
    assert Path(payload["summary_csv"]) == summary_csv

    record_payload = json.loads((out_dir / "mitdb_100.json").read_text(encoding="utf-8"))
    assert record_payload["ok"] is True
    assert record_payload["record_id"] == "100"
    assert record_payload["metrics"]["compression_ratio"] > 0
    assert record_payload["metrics"]["snr_db"] >= 0
    assert record_payload["metrics"]["rmse_uv"] >= 0
    assert record_payload["signal_integrity"]["status"] == "pass"

    aggregate_payload = json.loads(aggregate_json.read_text(encoding="utf-8"))
    assert aggregate_payload["records_processed"] == 1
    assert aggregate_payload["summary"]["integrity_pass_count"] == 1

    summary_text = summary_md.read_text(encoding="utf-8")
    assert "MIT-BIH Python-Only Benchmark Summary" in summary_text
    assert "100" in summary_text

    csv_text = summary_csv.read_text(encoding="utf-8")
    assert "record_id,diagnosis_bucket" in csv_text
    assert "100" in csv_text
