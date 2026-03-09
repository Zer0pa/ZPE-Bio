# Bio Wave-2 External Resource Lock (2026-02-20)

## Purpose
Pin the external resources required to close the EEG/ECG gap for Bio Wave-2 with executable, license-aware sources.

## Verified Reachable Sources (2026-02-20)

### 1) EEG: Sleep-EDF sample (PhysioNet)
- Dataset page: https://physionet.org/content/sleep-edfx/
- Sample file URL:
  - https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/SC4001E0-PSG.edf
- HTTP status: 200
- Content-Length (HEAD): 48,338,048 bytes
- License page indicator on dataset page: Open Data Commons Attribution License v1.0

### 2) EEG: CHB-MIT sample (PhysioNet)
- Dataset page: https://physionet.org/content/chbmit/
- Sample file URL:
  - https://physionet.org/files/chbmit/1.0.0/chb01/chb01_01.edf
- HTTP status: 200
- Content-Length (HEAD): 42,399,744 bytes
- License page indicator on dataset page: Open Data Commons Attribution License v1.0

### 3) ECG: MIT-BIH (PhysioNet)
- Dataset page: https://physionet.org/content/mitdb/
- Local copy already present in repo:
  - `validation/datasets/mitdb`
- License page indicator on dataset page: Open Data Commons Attribution License v1.0

### 4) Optional EEG alternate (PhysioNet EEGMMI)
- Dataset page: https://physionet.org/content/eegmmidb/
- License page indicator: Open Data Commons Attribution License v1.0

## Tooling Availability
- `wfdb` package versions are available via pip (checked).
- `mne` package versions are available via pip (checked).
- `pyedflib` package versions are available via pip (checked).

## Required Acquisition Commands
Run from repo root:

```bash
python -m pip install -e '.[validation]'
python -m pip install mne pyedflib
mkdir -p validation/datasets/eeg
curl -fL -o validation/datasets/eeg/SC4001E0-PSG.edf \
  https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/SC4001E0-PSG.edf
curl -fL -o validation/datasets/eeg/chb01_01.edf \
  https://physionet.org/files/chbmit/1.0.0/chb01/chb01_01.edf
```

## Hard Rule
If acquisition fails, execution must return a concrete blocker code with evidence, not a generic “gap” statement.
