# PRD: Bio Wave-2 Biosignal Multimodal Execution

Date: 2026-02-20
Owner: Product/Engineering
Repo root: repository root (`.`)
Priority: P0
Mode: Code-first execution (documentation polish is out of scope for this wave)

## 1) Mission
Close the Bio product gap by shipping executable biosignal features (not narrative):
1. `encode-ecg` CLI command (WFDB/MIT-BIH ingest -> ZPE stream -> roundtrip metrics).
2. `encode-eeg` CLI command (EDF/BIDS-friendly ingest path -> mental-lane stream -> roundtrip metrics).
3. `benchmark` CLI command (raw vs gzip vs ZPE, PRD and latency outputs).
4. `multimodal-stream` CLI command (ECG + EEG encoded/decoded in one unified stream contract).
5. `chemosense-bio` CLI command (smell+taste combined lane demo suitable for diagnostics framing).

## 2) Scientific Positioning (Code Scope)
This wave does **not** claim a novel disease model. It operationalizes one substrate claim in code:
- eight-primitive geometry can encode heterogeneous biosignals in one stream contract.

Modality mapping to implement/test in code:
1. mental lane -> EEG trajectories
2. rhythm/temporal lane -> ECG heartbeat dynamics
3. smell+taste lanes -> chemosensory signals

## 3) Current Baseline (Observed)
Already present:
1. `zpe-bio` package and CLI (`roundtrip`, `version`, `multimodal`).
2. Core ECG codec in `python/zpe_bio/codec.py`.
3. MIT-BIH local dataset under `validation/datasets/mitdb`.
4. WFDB-based benchmark runner at `validation/benchmarks/mit_bih_runner.py`.
5. Multimodal smell/taste/touch/mental packs and tests.

Missing productized surface:
1. No first-class CLI commands for ECG/EEG ingest and benchmark.
2. No EEG ingest pipeline bound to mental lane from real files.
3. No unified ECG+EEG CLI stream demo.
4. No explicit falsification bundle for these new commands.

## 4) Scope
In scope:
1. Python code and tests under this repo only.
2. CLI command expansion and robust error handling.
3. Deterministic benchmark/falsification outputs.
4. Optional dependency wiring for EEG stacks.

Out of scope:
1. Regulatory documentation authoring.
2. README/LICENSE writing.
3. IMC repo changes.
4. New clinical efficacy claims.

## 5) Data + Tooling Contract
### 5.1 Local-first mandatory assets
1. MIT-BIH from `validation/datasets/mitdb` (already present).
2. Existing multimodal smell/taste fixtures and code.

### 5.2 Optional external assets (if available)
1. EEG via EDF/BDF/BIDS using `mne` and/or `pyedflib`.
2. Extra PhysioNet/OpenNeuro files only if license/provenance is logged.

### 5.3 Dependency policy
1. Keep base install lean.
2. Add EEG libs under extras (`validation` or new `bioeeg` extra).
3. Commands must fail gracefully with actionable errors if optional deps are missing.

### 5.4 Mandatory gap-closure preflight (no ambiguity)
Before any phase execution, the agent must attempt to close external gaps using these exact steps:
1. Dependency install attempt:
   - `python -m pip install -e '.[validation]'`
   - `python -m pip install mne pyedflib`
2. EEG sample acquisition attempt (commercial-safe PhysioNet ODC-By datasets):
   - `mkdir -p validation/datasets/eeg`
   - `curl -fL -o validation/datasets/eeg/SC4001E0-PSG.edf https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/SC4001E0-PSG.edf`
   - `curl -fL -o validation/datasets/eeg/chb01_01.edf https://physionet.org/files/chbmit/1.0.0/chb01/chb01_01.edf`
3. Provenance recording:
   - create `validation/results/bio_wave2_resource_manifest.json` with:
     - source URL
     - dataset name/version
     - acquired UTC
     - license URL
     - file size and sha256
     - status (`PASS`/`FAIL`)

If any of the above fails, the agent must not hand-wave. It must emit a concrete blocker code with evidence:
1. `BLOCKER_ENV_NETWORK`
2. `BLOCKER_DEP_INSTALL`
3. `BLOCKER_SOURCE_UNAVAILABLE`
4. `BLOCKER_IO_PERMISSION`

A blocker is valid only with:
1. command attempted
2. stderr/stdout evidence
3. retry count
4. minimum remediation command

## 6) Runbook-First Protocol (Mandatory)
Before code edits, create:
1. `validation/runbooks/RUNBOOK_BIO_WAVE2_MASTER.md`
2. `validation/runbooks/RUNBOOK_BIO_WAVE2_PHASE_<N>.md`

Each phase must include:
1. exact command list
2. expected outputs
3. gate criteria
4. rollback notes

## 7) Phase Plan
### Phase 0: Baseline Freeze
Tasks:
1. Capture current CLI surface, tests, and benchmark scripts.
2. Run baseline tests and store logs.
3. Execute mandatory gap-closure preflight and record results.

Outputs:
1. `validation/results/bio_wave2_phase0_inventory.txt`
2. `validation/results/bio_wave2_phase0_baseline.txt`
3. `validation/results/bio_wave2_resource_manifest.json`
4. `validation/results/bio_wave2_preflight_blockers.json` (empty array when none)

Gate:
1. Baseline green before changes.

### Phase 1: CLI Surface Expansion
Tasks:
1. Extend `python/zpe_bio/cli.py` with new commands:
   - `encode-ecg`
   - `encode-eeg`
   - `benchmark`
   - `multimodal-stream`
   - `chemosense-bio`
2. Add shared JSON result schema helpers.
3. Add strict argument validation and structured error outputs.

Outputs:
1. `validation/results/bio_wave2_phase1_cli_contract.txt`
2. `tests/test_cli_biosignal_commands.py`

Gate:
1. `zpe-bio --help` lists all new commands.
2. New CLI tests pass.

### Phase 2: ECG Productization (`encode-ecg` + benchmark lane)
Tasks:
1. Implement ECG record ingestion from MIT-BIH via WFDB path.
2. Add `encode-ecg` command supporting record id, lead index, window length.
3. Add benchmark metrics:
   - raw bytes
   - gzip bytes
   - zpe bytes estimate
   - compression ratios
   - PRD
   - encode/decode latency
4. Reuse/adapt logic from `validation/benchmarks/mit_bih_runner.py`.

Outputs:
1. `validation/results/bio_wave2_phase2_ecg_smoke.txt`
2. `validation/results/bio_wave2_phase2_ecg_benchmark.json`

Gate:
1. At least 5 MIT-BIH records process end-to-end with no uncaught crash.
2. PRD and CR are emitted for each record.

### Phase 3: EEG Ingest + Mental-Lane Mapping (`encode-eeg`)
Tasks:
1. Implement EEG ingest adapter:
   - local EDF path first
   - optional BIDS/OpenNeuro path if provided
2. Map EEG channel windows to mental-lane stroke sequences (deterministic mapping contract).
3. Add fallback mode (`--synthetic-eeg`) so command remains executable offline.
4. Ensure decoded output and per-channel metrics are reported.

Outputs:
1. `validation/results/bio_wave2_phase3_eeg_contract.txt`
2. `validation/results/bio_wave2_phase3_eeg_roundtrip.json`
3. `tests/test_eeg_mental_mapping.py`
4. `validation/results/bio_wave2_phase3_eeg_realfile_smoke.txt`

Gate:
1. Real-file path works when EEG dependency + file are available.
2. Synthetic fallback always works.
3. No hard crash on missing optional dependencies.

### Phase 4: Unified Stream Demo (`multimodal-stream`)
Tasks:
1. Implement unified stream container for at least:
   - one ECG lane
   - one EEG lane
2. Add decode/reconstruction per lane from same stream.
3. Emit per-lane and aggregate metrics.

Outputs:
1. `validation/results/bio_wave2_phase4_multimodal_stream.json`
2. `tests/test_multimodal_stream_ecg_eeg.py`

Gate:
1. Unified stream roundtrip succeeds and preserves lane counts.
2. Deterministic replay hash stable.

### Phase 5: Chemosense Demo Hardening (`chemosense-bio`)
Tasks:
1. Add CLI command combining smell+taste events into one run output.
2. Reuse existing multimodal smell/taste modules.
3. Emit parseable summary for downstream IMC/Bio integration.

Outputs:
1. `validation/results/bio_wave2_phase5_chemosense.json`
2. `tests/test_chemosense_bio_cli.py`

Gate:
1. Combined smell+taste command passes with deterministic output.

### Phase 6: Falsification + Hardening
Tasks:
1. Dirty input campaign for all new commands.
2. Determinism replay (>=5 identical hashes per command/case).
3. Optional-dependency absence tests (graceful failures).
4. Packaging/install smoke for new CLI surface.

Outputs:
1. `validation/results/bio_wave2_phase6_falsification.md`
2. `validation/results/bio_wave2_phase6_dirty_campaign.json`
3. `validation/results/bio_wave2_phase6_determinism.json`
4. `validation/results/bio_wave2_phase6_package_smoke.txt`
5. `validation/results/BIO_WAVE2_EXECUTION_READINESS_REPORT.md`

Gate:
1. Zero uncaught crashes in dirty campaign.
2. Determinism gate pass.
3. CLI install + invocation smoke pass.

## 8) Quantitative Acceptance Criteria
All required:
1. New command set implemented and tested.
2. ECG benchmark command emits PRD + compression metrics vs raw and gzip.
3. EEG command supports both real-file path and synthetic fallback.
4. Unified ECG+EEG stream demo succeeds end-to-end.
5. Chemosense command succeeds and is deterministic.
6. Falsification campaign records zero uncaught crashes.

## 9) Required Artifact Contract
Minimum required files at completion:
1. `validation/results/bio_wave2_phase0_inventory.txt`
2. `validation/results/bio_wave2_phase0_baseline.txt`
3. `validation/results/bio_wave2_phase1_cli_contract.txt`
4. `validation/results/bio_wave2_phase2_ecg_benchmark.json`
5. `validation/results/bio_wave2_phase3_eeg_roundtrip.json`
6. `validation/results/bio_wave2_phase3_eeg_realfile_smoke.txt`
7. `validation/results/bio_wave2_phase4_multimodal_stream.json`
8. `validation/results/bio_wave2_phase5_chemosense.json`
9. `validation/results/bio_wave2_phase6_falsification.md`
10. `validation/results/bio_wave2_phase6_dirty_campaign.json`
11. `validation/results/bio_wave2_phase6_determinism.json`
12. `validation/results/BIO_WAVE2_EXECUTION_READINESS_REPORT.md`
13. `validation/results/BIO_WAVE2_HANDOFF_MANIFEST.json` (`required_files_complete=true`)

## 10) Risks and Blockers
Primary blockers to handle in code:
1. EEG dependency not installed (`mne`, `pyedflib`) -> must auto-attempt install first; if failed, emit blocker code.
2. No local EEG file -> must auto-attempt download first; if failed, emit blocker code.
3. Runtime variance on large records -> enforce bounded window mode and deterministic seed controls.

## 11) Done Definition
Done only when:
1. All phase gates pass.
2. Required artifact contract is complete.
3. Claims are bound to generated evidence files.
4. No unresolved P0 issues remain without owner + exact next command.
