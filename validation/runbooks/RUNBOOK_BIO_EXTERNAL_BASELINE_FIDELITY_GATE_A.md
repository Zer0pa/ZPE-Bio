# RUNBOOK: GATE A (Baseline Replay Lock)

## Commands
1. Replay baseline ECG benchmark:
   - `PYTHONPATH=python .venv/bin/python -m zpe_bio benchmark --lane ecg --record-ids 100,103,114,200,223 --samples 3600 --json`
2. Capture baseline chemosense payload:
   - `PYTHONPATH=python .venv/bin/python -m zpe_bio chemosense-bio --json`
3. Execute reproducibility/destruct baseline:
   - `scripts/run_repro_falsification.sh`

## Gate Criteria
1. Baseline benchmark lock includes prior max-PRD context.
2. Repro falsification overall GO is true.

## Rollback
1. If baseline replay fails, fix command/runtime issues and rerun Gate A only.
