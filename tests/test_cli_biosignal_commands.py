"""CLI contract tests for Bio Wave-2 command surface."""

from __future__ import annotations

import json

from zpe_bio.cli import main


def test_cli_help_lists_wave2_commands(capsys) -> None:
    code = main(["--help"])
    assert code == 0
    out = capsys.readouterr().out
    assert "encode-ecg" in out
    assert "encode-eeg" in out
    assert "benchmark" in out
    assert "multimodal-stream" in out
    assert "chemosense-bio" in out


def test_encode_ecg_json(capsys) -> None:
    code = main(["encode-ecg", "--record-id", "100", "--samples", "512", "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "encode-ecg"
    assert payload["metrics"]["samples"] == 512
    assert payload["metrics"]["compression_ratio"] > 0
    assert payload["metrics"]["raw_bytes"] > 0
    assert payload["metrics"]["gzip_bytes"] > 0
    assert payload["metrics"]["zpe_bytes_est"] > 0
    assert payload["metrics"]["encode_ms"] >= 0
    assert payload["metrics"]["decode_ms"] >= 0


def test_encode_eeg_synthetic_json(capsys) -> None:
    code = main(["encode-eeg", "--synthetic-eeg", "--channels", "2", "--samples", "256", "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["metrics"]["mode"] == "synthetic"
    assert payload["metrics"]["channel_count"] == 2
    assert payload["metrics"]["raw_bytes"] > 0
    assert payload["metrics"]["gzip_bytes"] > 0
    assert payload["metrics"]["zpe_bytes_est"] > 0
    assert payload["metrics"]["encode_ms"] >= 0
    assert payload["metrics"]["decode_ms"] >= 0


def test_benchmark_ecg_json(capsys) -> None:
    code = main(
        [
            "benchmark",
            "--lane",
            "ecg",
            "--record-ids",
            "100,103",
            "--samples",
            "512",
            "--json",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["result"]["aggregate"]["records_processed"] == 2


def test_multimodal_stream_and_chemosense_json(capsys) -> None:
    code_stream = main(
        [
            "multimodal-stream",
            "--record-id",
            "100",
            "--ecg-samples",
            "512",
            "--synthetic-eeg",
            "--eeg-samples",
            "256",
            "--json",
        ]
    )
    assert code_stream == 0
    stream_payload = json.loads(capsys.readouterr().out)
    assert stream_payload["ok"] is True
    assert stream_payload["result"]["lane_count"] == 2
    assert stream_payload["result"]["replay_hash_stable"] is True

    code_chemo = main(["chemosense-bio", "--json"])
    assert code_chemo == 0
    chemo_payload = json.loads(capsys.readouterr().out)
    assert chemo_payload["ok"] is True
    assert chemo_payload["result"]["taste"]["claim_status"] == "runtime_measured_no_clinical_claim"
