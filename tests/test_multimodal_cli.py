"""CLI smoke tests for multimodal entrypoints."""

from __future__ import annotations

import json

from zpe_bio.cli import main


def test_cli_multimodal_json_output(capsys) -> None:
    code = main(["multimodal", "--json"])
    assert code == 0

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["smell_roundtrip_ok"]
    assert payload["taste_roundtrip_ok"]
    assert payload["taste_zlayer_has_flavor_link"]
    assert payload["touch_roundtrip_ok"]
    assert payload["touch_timed_cooccurrence_ok"]
    assert payload["mental_rle_roundtrip_ok"]
    assert payload["mental_raw_roundtrip_ok"]
    assert payload["mental_profile_roundtrip_ok"]
