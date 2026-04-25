# ZPE-Bio

Deterministic ECG codec repository with a Python CLI, a Rust core crate, and committed validation artifacts. This README is intentionally limited to claims that are backed by proof artifacts already on disk and by tests that run in CI.

This repo's claimed surface is ECG staged proof only. It does not use the wearable runbooks as release evidence, and it does not make a generalized biosignal or regulatory claim.

## Anchored Proof Surface

| Claim | Proof Artifact On Disk | CI Test Anchor |
| --- | --- | --- |
| MIT-BIH benchmark writer emits summary + aggregate artifacts | [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md), [`validation/results/mitdb_python_only/mitdb_aggregate.json`](validation/results/mitdb_python_only/mitdb_aggregate.json) | [`tests/test_benchmark_mitdb.py`](tests/test_benchmark_mitdb.py) |
| PTB-XL benchmark writer emits committed-style summary artifacts | [`validation/results/ptbxl/summary.json`](validation/results/ptbxl/summary.json) | [`tests/test_benchmark_physionet.py`](tests/test_benchmark_physionet.py) |
| Sleep-EDF benchmark writer emits committed-style summary artifacts | [`validation/results/sleep-edfx/summary.json`](validation/results/sleep-edfx/summary.json) | [`tests/test_benchmark_physionet.py`](tests/test_benchmark_physionet.py) |
| Clinical ECG round-trip remains deterministic and high-fidelity in the Python codec | [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md) | [`tests/test_codec.py`](tests/test_codec.py), [`tests/test_deterministic_replay.py`](tests/test_deterministic_replay.py) |
| Python and Rust codec implementations remain parity-gated in CI | [`core/rust/`](core/rust), [`tests/test_parity.py`](tests/test_parity.py) | [`tests/test_parity.py`](tests/test_parity.py) |

## Not Claimed

- No public release-readiness verdict
- No Bio Wearable closure claim
- No generalized biosignal victory claim
- No regulatory or FDA claim

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
