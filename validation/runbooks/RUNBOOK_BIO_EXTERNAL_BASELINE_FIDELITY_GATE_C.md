# RUNBOOK: GATE C (Fidelity Sweep)

## Commands
1. Run reproducible ECG parameter sweep across benchmark records with fixed seed.
2. Record before/after aggregate metrics and best-achieved Pareto point.

## Gate Criteria
1. `fidelity_sweep_results.json` contains full sweep rows.
2. `before_after_metrics.json` contains baseline and best-achieved metrics.
3. Stretch target status (`max_prd <= 1.0`) explicitly marked PASS/OPEN.

## Rollback
1. If sweep fails, patch sweep runner/metric collection and rerun Gate C.
