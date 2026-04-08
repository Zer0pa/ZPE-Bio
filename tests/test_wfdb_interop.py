from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from zpe_bio.bio_wave2 import load_mitbih_record

wfdb = pytest.importorskip("wfdb")


def test_load_mitbih_record_matches_wfdb_direct_read() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    dataset_dir = repo_root / "validation" / "datasets" / "mitdb"

    loaded = load_mitbih_record("100", lead_index=0, max_samples=256, dataset_dir=dataset_dir)
    direct = wfdb.rdrecord(str(dataset_dir / "100"), sampto=256)

    assert loaded["sample_rate_hz"] == float(direct.fs)
    assert loaded["signal"].shape == (256,)
    np.testing.assert_allclose(loaded["signal"], direct.p_signal[:, 0].astype(np.float64))


def test_examples_emit_json_payloads() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    examples = repo_root / "examples"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "python")

    mitdb = subprocess.run(
        [
            sys.executable,
            str(examples / "mitdb_compress.py"),
            "--record-id",
            "100",
            "--samples",
            "256",
            "--json",
        ],
        cwd=repo_root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    mitdb_payload = json.loads(mitdb.stdout)
    assert mitdb_payload["record_id"] == "100"
    assert mitdb_payload["samples"] == 256
    assert mitdb_payload["compression_ratio"] > 0

    bridge = subprocess.run(
        [
            sys.executable,
            str(examples / "wfdb_bridge.py"),
            "--record-id",
            "100",
            "--samples",
            "256",
            "--json",
        ],
        cwd=repo_root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    bridge_payload = json.loads(bridge.stdout)
    assert bridge_payload["record_id"] == "100"
    assert bridge_payload["samples"] == 256
    assert bridge_payload["signal_integrity"]["status"] == "pass"
