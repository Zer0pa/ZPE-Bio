# PRD: Bio External Baseline + Fidelity Closure

- Date: 2026-02-20
- Repo root: `/Users/prinivenpillay/ZPE Bio/zpe-bio`
- Priority: P0

## 1) Mission (Measurable)
Close the remaining scientific engineering gaps in Bio:
1. Produce external baseline evidence for ECG/EEG transport.
2. Improve ECG fidelity from current `max_prd=2.452904` toward <= `1.0` target.
3. Remove ambiguous chemosense taste claim tag (`placeholder_governed`) from runtime outputs/tests.

## 2) Baseline Evidence Anchors
1. `/Users/prinivenpillay/ZPE Bio/zpe-bio/validation/results/bio_wave2_phase2_ecg_benchmark.json`
2. `/Users/prinivenpillay/ZPE Bio/zpe-bio/python/zpe_bio/bio_wave2.py`
3. `/Users/prinivenpillay/ZPE Bio/zpe-bio/tests/test_chemosense_bio_cli.py`
4. `/Users/prinivenpillay/ZPE Multimodality/ZPE_IMC_TECHNICAL_DOSSIER.md`

## 3) In Scope / Out Of Scope
In scope:
1. Bio code/tests/benchmarks only.
2. ECG threshold/quantization tuning with reproducible evidence.
3. Chemosense claim-status normalization in code + tests.

Out of scope:
1. IMC/IoT code.
2. Pure documentation-only edits with no engineering change.

## 4) Comparator Contract
ECG and EEG comparator rows must include:
1. `raw_bytes`
2. `gzip_bytes`
3. `zpe_bytes_est`
4. `prd_percent` (for ECG where defined)
5. `encode_ms` and `decode_ms`

## 5) Execution Order With Hard Gates
1. Gate A: baseline replay and lock current benchmark artifacts.
2. Gate B: external baseline comparator generation.
3. Gate C: fidelity-optimization sweep (parameterized, reproducible).
4. Gate D: chemosense claim-status runtime/test alignment.
5. Gate E: full regression + deterministic replay + packaging.

## 6) Acceptance Criteria
Mandatory:
1. External baseline table generated for ECG and EEG commands.
2. No regression in existing DT suite.
3. `placeholder_governed` removed from runtime chemosense output and tests updated.

Stretch target:
1. ECG `max_prd <= 1.0` on the phase benchmark set.

If stretch target fails:
1. Emit best-achieved Pareto artifact and keep claim as open.
2. Do not mark closed.

## 7) Mandatory Artifacts
Output folder:
- `/Users/prinivenpillay/ZPE Bio/zpe-bio/validation/results/<DATE>_bio_external_baseline_fidelity/`

Required:
1. `handoff_manifest.json`
2. `before_after_metrics.json`
3. `bio_external_baseline_results.json`
4. `fidelity_sweep_results.json`
5. `falsification_results.md`
6. `claim_status_delta.md`
7. `command_log.txt`

## 8) Stop / Rollback
Stop if DT regressions appear or crash-safety degrades. Roll back to last green state.

## 9) No Hand-Wavy Claims
No “clinical-lossless” closure claim without measured artifact proving threshold compliance.
