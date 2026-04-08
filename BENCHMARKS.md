# Benchmarks

This file tracks the reproducible benchmark surface for ZPE-Bio. Raw result
payloads live under `validation/results/`.

## Methodology

MIT-BIH local mirror:

```bash
python -m pip install -e ".[dev,validation]"
python scripts/benchmark_mitdb.py \
  --samples 10000 \
  --out-dir validation/results/mitdb_python_only \
  --summary-md validation/results/BENCHMARK_SUMMARY.md \
  --aggregate-json validation/results/mitdb_python_only/mitdb_aggregate.json \
  --summary-csv validation/results/mitdb_python_only/mitdb_summary.csv
```

PhysioNet remote datasets:

```bash
python -m pip install -e ".[dev,validation,bioeeg]"
python scripts/benchmark_physionet.py \
  --dataset ptb-xl \
  --dataset nstdb \
  --dataset edb \
  --dataset sleep-edfx \
  --results-root validation/results \
  --json
```

## Current Committed Results

| Dataset | Signal | Records / files | Metric | Value | Artifact |
| --- | --- | ---: | --- | ---: | --- |
| MIT-BIH Arrhythmia | ECG | 48 | Mean compression ratio | 1.323216 | `validation/results/mitdb_python_only/mitdb_aggregate.json` |
| MIT-BIH Arrhythmia | ECG | 48 | Mean PRD (%) | 1.115854 | `validation/results/mitdb_python_only/mitdb_aggregate.json` |
| MIT-BIH Arrhythmia | ECG | 48 | Mean SNR (dB) | 43.294294 | `validation/results/mitdb_python_only/mitdb_aggregate.json` |
| PTB-XL | ECG | 100 | Mean compression ratio | 1.576202 | `validation/results/ptbxl/summary.json` |
| PTB-XL | ECG | 100 | Mean SNR (dB) | 31.987826 | `validation/results/ptbxl/summary.json` |
| PTB-XL | ECG | 100 | Max PRD (%) | 5.285148 | `validation/results/ptbxl/summary.json` |
| NSTDB | ECG | 15 | Mean compression ratio | 1.310067 | `validation/results/nstdb/summary.json` |
| NSTDB | ECG | 15 | Mean SNR (dB) | 60.493187 | `validation/results/nstdb/summary.json` |
| NSTDB | ECG | 15 | Max PRD (%) | 1.960166 | `validation/results/nstdb/summary.json` |
| European ST-T Database | ECG | 90 | Mean compression ratio | 1.376457 | `validation/results/edb/summary.json` |
| European ST-T Database | ECG | 90 | Mean SNR (dB) | 52.468288 | `validation/results/edb/summary.json` |
| European ST-T Database | ECG | 90 | Max PRD (%) | 4.336930 | `validation/results/edb/summary.json` |
| Sleep-EDF | EEG | 0 | Download status | upstream 404 | `validation/results/sleep-edfx/summary.json` |

## Notes

- MIT-BIH runs against the committed local mirror in `validation/datasets/mitdb/`.
- PTB-XL, NSTDB, and EDB summaries were produced through `wfdb` acquisition and
  are preserved under `validation/results/`.
- Sleep-EDF remains blocked by the upstream `SC4001E0-PSG.edf.hea` 404 captured
  in `validation/results/sleep-edfx/summary.json`.
