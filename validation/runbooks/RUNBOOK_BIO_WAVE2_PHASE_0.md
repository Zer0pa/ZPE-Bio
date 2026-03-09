# RUNBOOK: BIO WAVE-2 PHASE 0 (Preflight + Baseline)

## Commands
1. `.venv/bin/python -m pip install -e '.[validation]'`
2. `.venv/bin/python -m pip install mne pyedflib`
3. `mkdir -p validation/datasets/eeg`
4. `curl -fL -o validation/datasets/eeg/SC4001E0-PSG.edf https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/SC4001E0-PSG.edf`
5. `curl -fL -o validation/datasets/eeg/chb01_01.edf https://physionet.org/files/chbmit/1.0.0/chb01/chb01_01.edf`
6. `.venv/bin/python -m pytest -q`

## Outputs
- `validation/results/bio_wave2_phase0_inventory.txt`
- `validation/results/bio_wave2_phase0_baseline.txt`
- `validation/results/bio_wave2_resource_manifest.json`
- `validation/results/bio_wave2_preflight_blockers.json`

## Gate
- Install/download attempts recorded with provenance.
- Baseline test pass status captured.

## Rollback
- If dependency/download fails, retry and emit blocker code with evidence.
