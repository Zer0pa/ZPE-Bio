"""Phase-4 tests for unified ECG+EEG multimodal stream command."""

from __future__ import annotations

import json

from zpe_bio.cli import main


def test_multimodal_stream_synthetic_eeg_json(capsys) -> None:
    code = main(
        [
            "multimodal-stream",
            "--record-id",
            "100",
            "--ecg-samples",
            "512",
            "--synthetic-eeg",
            "--eeg-channels",
            "2",
            "--eeg-samples",
            "256",
            "--json",
        ]
    )
    assert code == 0

    payload = json.loads(capsys.readouterr().out)
    result = payload["result"]
    assert payload["ok"] is True
    assert payload["command"] == "multimodal-stream"
    assert result["lane_count"] == 2
    assert result["replay_hash_stable"] is True
    assert result["eeg_lane"]["mode"] == "synthetic"
    assert result["eeg_lane"]["all_channels_direction_match"] is True

