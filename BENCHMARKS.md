# Benchmarks

This file tracks the committed public-dataset benchmark surface for ZPE-Bio.
Raw result payloads live under `validation/results/`.

## Dataset Sources

- MIT-BIH Arrhythmia: <https://physionet.org/content/mitdb/1.0.0/>
- PTB-XL: <https://physionet.org/content/ptb-xl/1.0.3/>
- NSTDB: <https://physionet.org/content/nstdb/1.0.0/>
- European ST-T Database: <https://physionet.org/content/edb/1.0.0/>
- Sleep-EDF Expanded: <https://physionet.org/content/sleep-edfx/1.0.0/>

## Methodology

MIT-BIH local mirror, 48 committed records:

```bash
python -m pip install -e ".[dev,validation]"
python scripts/benchmark_mitdb.py \
  --samples 10000 \
  --out-dir validation/results/mitdb_python_only \
  --summary-md validation/results/BENCHMARK_SUMMARY.md \
  --aggregate-json validation/results/mitdb_python_only/mitdb_aggregate.json \
  --summary-csv validation/results/mitdb_python_only/mitdb_summary.csv
```

PhysioNet ECG refresh, Runpod workspace with reused local mirrors:

```bash
python -m pip install -e ".[dev,validation,bioeeg]"
python scripts/benchmark_physionet.py \
  --dataset ptb-xl \
  --dataset nstdb \
  --dataset edb \
  --download-root validation/datasets \
  --results-root validation/results \
  --skip-download \
  --json
```

Sleep-EDF reproduction, direct EDF download:

```bash
python scripts/benchmark_physionet.py \
  --dataset sleep-edfx \
  --download-root validation/datasets \
  --results-root validation/results \
  --record-limit 1 \
  --json
```

Baseline math uses committed gzip byte counts. `ZPE / gzip > 1.0` means the
estimated ZPE stream is smaller than gzip for that dataset slice.

## Dataset Metrics

| Dataset | Records / files | Sampling rate (Hz) | Channels | ZPE ratio | PRD (%) | SNR (dB) | Artifact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| MIT-BIH Arrhythmia | 48 | 360 | 1 | 1.323216 | 1.115854 | 43.294294 | `validation/results/mitdb_python_only/mitdb_aggregate.json` |
| PTB-XL | 100 | 500 | 12 | 1.576202 | 5.285148 | 31.987826 | `validation/results/ptbxl/summary.json` |
| NSTDB | 15 | 360 | 2 | 1.310067 | 1.960166 | 60.493187 | `validation/results/nstdb/summary.json` |
| European ST-T Database | 90 | 250 | 2 | 1.376457 | 4.336930 | 52.468288 | `validation/results/edb/summary.json` |
| Sleep-EDF | 1 | 100 | 2 | 1.812389 | n/a | n/a | `validation/results/sleep-edfx/summary.json` |

Sleep-EDF uses mean channel RMSE instead of PRD/SNR. The committed single-file
run produced `0.207799` mean channel RMSE.

## Baseline Comparison

| Dataset | Baseline (gzip) | ZPE | Ratio (ZPE / gzip) | Improvement | Artifact |
| --- | ---: | ---: | ---: | ---: | --- |
| MIT-BIH Arrhythmia | 1.752258 | 1.323179 | 0.755128 | -24.49% | `validation/results/mitdb_python_only/mitdb_aggregate.json` |
| PTB-XL | 1.404367 | 1.576202 | 1.122358 | +12.24% | `validation/results/ptbxl/summary.json` |
| NSTDB | 1.493227 | 1.310067 | 0.877339 | -12.27% | `validation/results/nstdb/summary.json` |
| European ST-T Database | 2.018847 | 1.376457 | 0.681804 | -31.82% | `validation/results/edb/summary.json` |
| Sleep-EDF | 0.939450 | 1.812389 | 1.929202 | +92.92% | `validation/results/sleep-edfx/summary.json` |

## Notes

- MIT-BIH runs against the committed local mirror in `validation/datasets/mitdb/`.
- MIT-BIH baseline math uses per-record `gzip_cr` and `zpe_cr_est` fields from
  `validation/results/mitdb_python_only/mitdb_aggregate.json`.
- PTB-XL, NSTDB, EDB, and Sleep-EDF baseline math uses the committed
  `mean_gzip_compression_ratio` and `mean_compression_ratio` fields from each
  dataset summary.
- The `Ratio (ZPE / gzip)` column is computed directly from the displayed row
  means in this table.
- Gzip remains the stronger compression baseline on MIT-BIH, NSTDB, and EDB.
- ZPE leads gzip on the committed PTB-XL slice and the reproduced Sleep-EDF file.
