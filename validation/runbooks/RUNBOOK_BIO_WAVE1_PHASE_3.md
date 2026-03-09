# RUNBOOK: BIO WAVE-1 PHASE 3 (Parity + Golden Compatibility)

## Commands
1. Python/Rust parity:
   - `cd core/rust && cargo build --release && cargo build --release --target x86_64-apple-darwin`
   - `.venv/bin/python -m pytest -q tests/test_parity.py`
2. Golden packet compatibility:
   - `.venv/bin/python -m pytest -q tests/test_multimodal_fusion.py`
   - `.venv/bin/python -m pytest -q tests/test_packet_compatibility.py`
3. Deterministic replay:
   - `.venv/bin/python -m pytest -q tests/test_deterministic_replay.py`

## Outputs
1. `validation/results/bio_wave1_phase3_parity.txt`
2. `validation/results/bio_wave1_phase3_golden_packets.txt`

## Gate
1. Parity tests pass without skip.
2. Golden packet fixtures pass.
3. Deterministic replay pass.

## Rollback
1. Patch parity/fixture logic and rerun full Phase 3 commands.
