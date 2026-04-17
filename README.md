# ZPE-Bio

---

## What This Is

Deterministic biosignal encoding for workflows where reproducibility is mandatory. Current governing evidence is ECG round-trip fidelity across MIT-BIH, PTB-XL, EDB, and NSTDB, with dual Rust and Python codec surfaces plus embedded reference builds.

For medical-device firmware teams and clinical-data infrastructure engineers: ZPE-Bio is an independent biosignal encoding product with auditable ECG proof lineage. EEG commands and multimodal helpers remain auxiliary surfaces, not current headline authority. **Bio Wearable is NO_GO** and retained only for traceability, not product authority.

Commercial posture: always in beta. Installable now, improving continuously. Historical validation artifacts may preserve host-specific paths; treat them as provenance, not current operator instructions.

Cross-repo coordination with [ZPE-IMC](https://github.com/zer0-point-energy/ZPE-IMC) is documented under `docs/family/`. ZPE-Bio stands on its own product surface; shared coordination does not make this repo a common platform dependency.

| Field | Value |
|-------|-------|
| Architecture | BIO_WAVEFORM |
| Encoding | ECG_DELTA_V1 |

## Key Metrics

| Metric | Value | Baseline |
|--------|-------|----------|
| MIT-BIH | 48/48 | integrity passes |
| PTB-XL | 1.576202× | 100/100 entries |
| EDB_SNR | 52.468288 dB | 90/90 entries |
| NSTDB_SNR | 60.493187 dB | 15/15 entries |

> Source: [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md) | [`validation/results/ptbxl/summary.json`](validation/results/ptbxl/summary.json) | [`validation/results/edb/summary.json`](validation/results/edb/summary.json) | [`validation/results/nstdb/summary.json`](validation/results/nstdb/summary.json)

## What We Prove

> Auditable guarantees backed by committed proof artifacts. Start at `validation/results/BENCHMARK_SUMMARY.md`.

- Deterministic ECG round-trip fidelity verified across the MIT-BIH 48-record corpus
- External ECG benchmark summaries retained for PTB-XL, EDB, and NSTDB
- Dual implementation surface: Rust core crate and Python package
- Cross-repo coordination with ZPE-IMC is documented at artifact level only

## What We Don't Claim

- No claim that EEG helpers carry the same benchmark authority as the ECG path
- No claim of Bio Wearable validation
- No claim of regulatory or FDA compliance
- No claim of NaN-safe input handling; callers must sanitize NaN inputs before encode/decode

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | ACTIVE_BETA |
| Release posture | Useful now, improving continuously |
| Authority scope | ECG-backed proof surface |
| Confidence | 100% (MIT-BIH integrity passes) |
| Source | validation/results/BENCHMARK_SUMMARY.md |

> **Evaluators:** `pip install zpe-bio` (available on PyPI) closes the public package import surface. Repo-local `pytest` that exercises ECG ingest currently needs validation extras as well: `python -m pip install -e ".[dev,validation]"`. Contact hello@zer0pa.com for integration guidance.

## Tests and Verification

| Code | Check | Verdict |
|------|-------|---------|
| V_01 | MIT-BIH integrity passes (48/48) | PASS |
| V_02 | PTB-XL benchmark summary committed | PASS |
| V_03 | NSTDB benchmark summary committed | PASS |
| V_04 | EDB benchmark summary committed | PASS |
| V_05 | Sleep-EDF single-file benchmark committed | PASS |
| V_06 | Bio Wearable gate | FAIL |

## Proof Anchors

| Path | State |
|------|-------|
| validation/results/BENCHMARK_SUMMARY.md | VERIFIED |
| validation/results/ptbxl/summary.json | VERIFIED |
| validation/results/nstdb/summary.json | VERIFIED |
| validation/results/edb/summary.json | VERIFIED |
| validation/results/sleep-edfx/summary.json | VERIFIED |
| docs/family/BIO_IMC_ALIGNMENT_REPORT.md | VERIFIED |

## Repo Shape

| Field | Value |
|-------|-------|
| Proof Anchors | 6 |
| Modality Lanes | 2 |
| Authority Source | validation/results/BENCHMARK_SUMMARY.md |

---

ZPE-Bio is an independent biosignal encoding product in the Zer0pa portfolio. It packages an ECG-backed deterministic codec surface, a Rust core crate, and retained validation artifacts for continued verification and improvement.

This repository is an active beta surface. It installs now, it improves continuously, and its current governing authority is the retained ECG benchmark set under `validation/results/`.

## Quick Start

```bash
# Install from PyPI
pip install zpe-bio
python -c "import zpe_bio; print(zpe_bio.__file__)"
```

Or install from source (development):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m zpe_bio --help
python -m zpe_bio roundtrip --mode clinical --samples 250
```

Repo-local pytest and ECG validation commands require validation extras:

```bash
python -m pip install -e ".[dev,validation]"
pytest
python -m zpe_bio encode-ecg --record-id 100 --samples 1000 --json
```

Optional EEG support requires extra packages and local dataset acquisition:

```bash
python -m pip install -e ".[validation,bioeeg]"
```

## Ecosystem

- Cross-repo coordination surface: [ZPE-IMC](https://github.com/zer0-point-energy/ZPE-IMC)
- Organization surface: [Zer0pa](https://github.com/zer0-point-energy)
- Coordination artifacts in this repo: `docs/family/BIO_IMC_ALIGNMENT_REPORT.md`

## Who This Is For

| | |
|---|---|
| **Ideal first buyer** | Medical-device firmware team or clinical-data infrastructure team evaluating deterministic biosignal encoding |
| **Pain statement** | Biosignal pipelines require reproducibility and auditability — generic compressors are non-deterministic or domain-agnostic |
| **Deployment model** | Python package + Rust crate, always-in-beta |
| **Portfolio position** | Independent biosignal product with retained cross-repo coordination artifacts under `docs/family/` |

## Current Reality

- Runtime/package surface exists under `python/zpe_bio/`.
- Native codec surface exists under `core/rust/`.
- Embedded references exist under `embedded/`.
- Proof and readiness artifacts exist under `validation/results/` and `validation/runbooks/`.
- Cross-repo coordination artifacts exist under `docs/family/`.
- The source tree contains runnable Python and Rust codec surfaces.
- The source tree contains committed Wave-1 and Wave-2 readiness artifacts.
- The source tree contains ZPE-IMC coordination artifacts for artifact-level compatibility.

## Current Status Snapshot

- Wave-1 and Wave-2 artifacts are retained and auditable.
- Bio Wearable remains `NO_GO`; its closure bundles are retained for traceability, not product authority.
- EEG and multimodal helpers exist in the codebase but are not current headline proof surfaces.
- Historical validation artifacts may preserve host-specific paths and should be read as provenance rather than operator instructions.

## Repository Map

- `python/zpe_bio/`: Python package and CLI
- `core/rust/`: Rust codec crate
- `embedded/`: embedded reference builds
- `tests/`: repo-local pytest suite; ECG ingest checks require validation extras
- `scripts/`: operator scripts and generators
- `validation/results/`: committed proof and readiness artifacts
- `validation/runbooks/`: execution runbooks
- `docs/`: repo docs, coordination notes, and regulatory material

## Audit And Boundaries

- Proof index: `validation/results/README.md`
- Short audit path: `validation/results/BENCHMARK_SUMMARY.md`
- Public/operator limits: `docs/LEGAL_BOUNDARIES.md`
- Docs landing: `docs/ARCHITECTURE.md`
- Legal boundary summary: `docs/LEGAL_BOUNDARIES.md`

## Open Contradictions

- Some historical docs still describe broader biosignal scope than the current ECG-backed authority surface.
- `ruff` and multimodal manifest verification were not re-cleared in this phase.
- Regulatory closeout still depends on parked external artifacts and owner-held decisions.

Read this repo as an active biosignal beta with ECG authority today and explicit open limits, not as a finished regulatory release.
