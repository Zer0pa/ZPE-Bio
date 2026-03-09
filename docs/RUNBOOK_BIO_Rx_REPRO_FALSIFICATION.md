# RUNBOOK: Bio Rx Reproducible Falsification Rerun

## Scope
- Repository: `/Users/prinivenpillay/ZPE Bio/zpe-bio`
- Purpose: run full falsification in a pinned local environment (`.venv`) and emit machine-runnable evidence artifacts.
- This runbook does not use global Python.

## Environment Contract
- Python interpreter: `.venv/bin/python` (required)
- Required Python packages:
  - `numpy`
  - `wfdb`
  - `pytest`
  - `scipy`
  - `matplotlib`
  - `build`
  - `ruff`
- Required Rust tools:
  - `cargo`
  - `rustc`
  - `rustup`
- Required Rust targets:
  - `thumbv8m.main-none-eabi`
  - `x86_64-apple-darwin`

## One-Command Rerun
```bash
./scripts/run_repro_falsification.sh
```

## What the Entrypoint Executes
1. Verifies dependency contract inside `.venv`.
2. Captures `pip freeze --all` snapshot.
3. Verifies Rust toolchain and installed targets.
4. Builds Rust release artifacts required for DT parity/latency paths.
5. Runs full DT suite (`DT-1..DT-17`) via:
   - `.venv/bin/python validation/destruct_tests/run_all_dts.py`
6. Enforces DT stop policy:
   - Any DT `FAIL`, `TIMEOUT`, or `NOT_IMPLEMENTED` => immediate NO-GO stop.
7. If DT gate passes, runs:
   - `.venv/bin/python -m pytest -q`
   - `.venv/bin/python validation/benchmarks/phase3_hostok_report.py`
8. Writes reproducibility + summary artifacts in `validation/results/`.

## Output Artifacts
- `validation/results/dt_results_<timestamp>.json`
- `validation/results/phase3_hostok_<timestamp>.json`
- `validation/results/repro_manifest_<timestamp>.json`
- `validation/results/repro_hashes_<timestamp>.txt`
- `validation/results/falsification_results_<timestamp>.md`
- `validation/results/claim_status_delta_<timestamp>.md`
- `validation/results/command_log_<timestamp>.txt`
- `validation/results/pip_freeze_<timestamp>.txt`

## Acceptance Gates
- Full DT suite executed (`DT-1..DT-17`) with no `NOT_IMPLEMENTED`.
- `.venv` pytest suite passes.
- `phase3_hostok_report` has `overall_pass=true`.
- Reproducibility manifest complete with dependency/toolchain contract and artifact hashes.

## NO-GO Policy
- If any DT fails: stop immediately and report NO-GO with exact failing DT output tails.
- If pytest or phase3 host report fails: NO-GO.
