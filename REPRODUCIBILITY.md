# Reproducibility

## Canonical Inputs

- `validation/datasets/mitdb/`: staged ECG corpus used for cold-clone verification and the committed MIT-BIH benchmark summaries
- `validation/results/mitdb_python_only/mitdb_aggregate.json`: aggregate ECG proof artifact for the staged MIT-BIH replay path
- `validation/results/ptbxl/summary.json`
- `validation/results/edb/summary.json`
- `validation/results/nstdb/summary.json`
- `validation/results/sleep-edfx/summary.json`

The committed public proof surface is ECG-focused. Historical summaries for
other corpora remain committed as artifacts; they are not a claim that every
upstream corpus is staged in this cold-clone repo.

## Golden-Bundle Hash

This field will be populated by the `receipt-bundle.yml` workflow in Wave 3.

## Verification Command

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m zpe_bio --help
python -m zpe_bio roundtrip --mode clinical --samples 250
```

Repo-local pytest and ECG validation commands require:

```bash
python -m pip install -e ".[dev,validation]"
pytest
python -m zpe_bio encode-ecg --record-id 100 --samples 1000 --json
```

## Supported Runtimes

- Python CLI/package via `python/zpe_bio/`
- Rust codec crate via `core/rust/`
- Embedded reference target via `embedded/nrf5340/`

The public proof surface remains staged ECG proof. Bio Wearable remains `NO_GO`
unless separately re-proven.
