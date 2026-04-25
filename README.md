# ZPE-Bio

Deterministic ECG codec repository with a Python CLI, a Rust core crate, and committed validation artifacts. This README is intentionally limited to claims that are backed by proof artifacts already on disk and by tests that run in CI. ZPE-Bio is one of 17 independent encoding products in the Zer0pa portfolio, each developed for its own domain.

This repo's claimed surface is ECG staged proof only. It does not use the wearable runbooks as release evidence, and it does not make a generalized biosignal or regulatory claim.

## Anchored Proof Surface

| Claim | Proof Artifact On Disk | CI Test Anchor |
| --- | --- | --- |
| MIT-BIH benchmark writer emits summary + aggregate artifacts | [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md), [`validation/results/mitdb_python_only/mitdb_aggregate.json`](validation/results/mitdb_python_only/mitdb_aggregate.json) | [`tests/test_benchmark_mitdb.py`](tests/test_benchmark_mitdb.py) |
| PTB-XL benchmark writer emits committed-style summary artifacts | [`validation/results/ptbxl/summary.json`](validation/results/ptbxl/summary.json) | [`tests/test_benchmark_physionet.py`](tests/test_benchmark_physionet.py) |
| Clinical ECG round-trip remains deterministic and high-fidelity in the Python codec | [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md) | [`tests/test_codec.py`](tests/test_codec.py), [`tests/test_deterministic_replay.py`](tests/test_deterministic_replay.py) |
| Python and Rust codec implementations remain parity-gated in CI | [`core/rust/`](core/rust), [`tests/test_parity.py`](tests/test_parity.py) | [`tests/test_parity.py`](tests/test_parity.py) |

## Not Claimed

- No public release-readiness verdict
- No generalized biosignal victory claim
- No Bio Wearable closure claim
- No regulatory or FDA claim

## Benchmark Results (committed artifacts, beta)

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

## Comp Benchmarks

ZPE-Bio is a fidelity-bounded-lossy ECG codec (clinical mode, mean PRD ~1.12%, max PRD <= 2.32% on MIT-BIH). gzip, zlib, and zstd are general-purpose lossless byte compressors. Direct compression-ratio comparison is not apples-to-apples: ZPE-Bio's CR is intrinsically bounded by its clinical fidelity contract, while lossless compressors achieve whatever CR the byte distribution permits at zero error. The honest comparison reports both CRs and the fidelity contract, not a single "winner".

| Codec | Mean CR | Median CR | Fidelity |
| --- | ---: | ---: | --- |
| ZPE-Bio | 1.323 | 1.316 | bounded-lossy, PRD <= 2.32% (mean ~1.12%) |
| gzip (level 6) | 1.429 | 1.408 | lossless |
| zlib (level 6) | 1.429 | 1.408 | lossless |
| zstd (level 3) | 1.412 | 1.394 | lossless |

On raw compression ratio alone, ZPE-Bio (mean CR 1.323) loses to gzip, zlib, zstd (gzip 1.429, zlib 1.429, zstd 1.412). This is expected and does not invalidate the lane: ZPE-Bio is a fidelity-bounded-lossy clinical ECG codec (mean PRD ~1.12%, max PRD <= 2.32% on MIT-BIH); gzip/zlib/zstd are lossless general-purpose compressors. The two are not commensurable as a single CR number. ZPE-Bio's value proposition is deterministic, bounded-error reconstruction with a clinical fidelity contract, not raw CR supremacy over lossless byte compressors.

Note on input scope: lossless comparator CRs above are computed over the full raw int16 `.dat` byte stream of each MIT-BIH record; ZPE-Bio CRs are taken from the lane's existing aggregate, computed over a 10000-sample clinical-mode window per record. Both surfaces are recorded in the proof artifact below.

Proof: [proofs/artifacts/comp_benchmarks/mitbih_codec_comparison.json](proofs/artifacts/comp_benchmarks/mitbih_codec_comparison.json)

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
