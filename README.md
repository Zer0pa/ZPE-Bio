# ZPE-Bio

Deterministic ECG codec — 100% integrity across four standard corpora (253 records), Python and Rust parity-gated in CI. ZPE-Bio is one of 17 independent encoding products in the Zer0pa portfolio, each developed for its own domain.

Scope discipline: ECG staged proof only. Not a generalized biosignal codec. Not a regulatory or wearable closure claim. Useful now, improving continuously.

## Commercial Readiness

| Field | Value |
| --- | --- |
| Verdict | STAGED |
| Domain | ECG — clinical and research corpora |
| Scope | ECG round-trip codec; Python + Rust; 4 standard corpora validated in CI |
| What is not claimed | Wearable closure, generalized biosignal, regulatory / FDA clearance |
| License | Zer0pa Source-Available License v7.0 (`LicenseRef-Zer0pa-SAL-7.0`) |

## Anchored Proof Surface

| Claim | Proof Artifact On Disk | CI Test Anchor |
| --- | --- | --- |
| MIT-BIH benchmark writer emits summary + aggregate artifacts | [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md), [`validation/results/mitdb_python_only/mitdb_aggregate.json`](validation/results/mitdb_python_only/mitdb_aggregate.json) | [`tests/test_benchmark_mitdb.py`](tests/test_benchmark_mitdb.py) |
| PTB-XL benchmark writer emits committed-style summary artifacts | [`validation/results/ptbxl/summary.json`](validation/results/ptbxl/summary.json) | [`tests/test_benchmark_physionet.py`](tests/test_benchmark_physionet.py) |
| Clinical ECG round-trip remains deterministic and high-fidelity in the Python codec | [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md) | [`tests/test_codec.py`](tests/test_codec.py), [`tests/test_deterministic_replay.py`](tests/test_deterministic_replay.py) |
| Python and Rust codec implementations remain parity-gated in CI | [`core/rust/`](core/rust), [`tests/test_parity.py`](tests/test_parity.py) | [`tests/test_parity.py`](tests/test_parity.py) |

## Not Claimed

- No generalized biosignal victory claim
- No Bio Wearable closure claim
- No regulatory or FDA claim

## Benchmark Results

Results below are from committed benchmark artifacts. All runs are CPU-only Python codec; no hardware path is implied.

### MIT-BIH Arrhythmia Database (48 records, full corpus)

| Metric | Value |
| --- | ---: |
| Records processed | 48/48 |
| Integrity pass rate | 48/48 (100%) |
| Mean compression ratio | 1.323 |
| Mean SNR | 43.3 dB |
| Mean RMSE | 3.24 uV |
| Mean PRD | 1.12% |
| Max PRD | 2.32% |

Source: [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md), [`validation/results/mitdb_python_only/mitdb_aggregate.json`](validation/results/mitdb_python_only/mitdb_aggregate.json) | CI: [`tests/test_benchmark_mitdb.py`](tests/test_benchmark_mitdb.py)

### MIT-BIH Noise Stress Test Database (nstdb, 15 entries)

| Metric | Value |
| --- | ---: |
| Records processed | 15/15 |
| Integrity pass rate | 15/15 (100%) |
| Mean compression ratio | 1.310 |
| Mean SNR | 60.5 dB |
| Max PRD | 1.96% |

Source: [`validation/results/nstdb/summary.json`](validation/results/nstdb/summary.json) | CI: [`tests/test_benchmark_physionet.py`](tests/test_benchmark_physionet.py)

### European ST-T Database (edb, 90 entries)

| Metric | Value |
| --- | ---: |
| Records processed | 90/90 |
| Integrity pass rate | 90/90 (100%) |
| Mean compression ratio | 1.376 |
| Mean SNR | 52.5 dB |
| Max PRD | 4.34% |

Source: [`validation/results/edb/summary.json`](validation/results/edb/summary.json) | CI: [`tests/test_benchmark_physionet.py`](tests/test_benchmark_physionet.py)

### PTB-XL ECG Database (100 records sample)

| Metric | Value |
| --- | ---: |
| Records processed | 100/100 |
| Integrity pass rate | 100/100 (100%) |
| Mean compression ratio | 1.576 |
| Mean SNR | 32.0 dB |
| Max PRD | 5.29% |

Source: [`validation/results/ptbxl/summary.json`](validation/results/ptbxl/summary.json) | CI: [`tests/test_benchmark_physionet.py`](tests/test_benchmark_physionet.py)

**Note on PTB-XL SNR/PRD:** PTB-XL records are 12-lead 500 Hz clinical studies; the lower SNR relative to MIT-BIH reflects higher signal diversity and more channels compressed per segment, not codec regression. Integrity passes 100/100.

## Local Validation

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,validation]"
pytest -q
python -m build
```

Quick ECG smoke check:

```bash
python -m zpe_bio roundtrip --mode clinical --samples 250
```

## Repository Map

- `python/zpe_bio/`: Python package and CLI
- `core/rust/`: Rust codec crate
- `embedded/`: embedded reference firmware tree
- `tests/`: repo-local pytest suite
- `scripts/`: benchmark and operator scripts
- `validation/results/`: committed benchmark outputs
- `validation/runbooks/`: execution and boundary runbooks
- `docs/`: repo documentation and regulatory/reference material

## Read Next

- [`validation/results/README.md`](validation/results/README.md)
- [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/LEGAL_BOUNDARIES.md`](docs/LEGAL_BOUNDARIES.md)
