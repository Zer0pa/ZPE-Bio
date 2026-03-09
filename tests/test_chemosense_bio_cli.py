"""Phase-5 tests for chemosense-bio CLI command."""

from __future__ import annotations

import json

from zpe_bio.cli import main


def test_chemosense_bio_json_shape_and_claim_guard(capsys) -> None:
    code = main(["chemosense-bio", "--json"])
    assert code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "chemosense-bio"
    assert payload["result"]["mode"] == "chemosense-bio"
    assert payload["result"]["smell"]["word_count"] > 0
    assert payload["result"]["taste"]["word_count"] > 0
    assert payload["result"]["taste"]["claim_status"] == "runtime_measured_no_clinical_claim"
