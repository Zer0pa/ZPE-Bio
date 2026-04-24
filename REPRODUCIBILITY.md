# Reproducibility

## Canonical Inputs

- `tests/fixtures/wave1_golden_packets.json`
- `validation/datasets/mitdb/100.atr`
- `validation/datasets/mitdb/100.dat`
- `validation/datasets/mitdb/100.hea`
- `validation/datasets/mitdb/` — staged MIT-BIH ECG corpus used by the committed benchmark path

Additional EEG, SisFall, and wearable dataset mirrors are intentionally not staged in this clone for this phase.

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

Additional repo-local validation commands from the README Quick Start:

```bash
python -m pip install -e ".[dev,validation]"
pytest
python -m zpe_bio encode-ecg --record-id 100 --samples 1000 --json
```

## Supported Runtimes

- Python CLI/package via `python/zpe_bio/`
- Rust codec crate via `core/rust/`
- Embedded reference target via `embedded/nrf5340/`
