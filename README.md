# ZPE-Bio

48 MIT-BIH records. 1.32x mean compression. 1.12% mean PRD.
Research use only. Not FDA-cleared. Do not use for clinical diagnosis.

---

## What This Is

Deterministic 8-primitive biosignal codec. ECG + EEG. Rust core. Python package. Embedded reference path.

Medical device audit trails need deterministic replay, stable thresholds, and reproducible byte streams. ZPE-Bio keeps round-trip metrics tied to the same record, same mode, and same CLI path so firmware teams, clinical data engineers, and reviewers can re-run evidence without transport ambiguity.

Validated on: MIT-BIH Arrhythmia ✅ | PTB-XL ✅ | NSTDB ✅ | Sleep-EDF single-file ✅

Wave-1 and Wave-2 readiness artifacts are committed under `validation/results/` and `validation/runbooks/`. ECG validation runs deterministic round-trip fidelity checks against real MIT-BIH records: `python -m zpe_bio encode-ecg --record-id 100 --samples 1000 --json`. IMC contract-consumption artifacts confirm family alignment.

PhysioNet lanes tracked here: MIT-BIH local mirror committed. PTB-XL, NSTDB, EDB, and a single-file Sleep-EDF summary committed.

Ecosystem neighbors: [WFDB-Python](https://github.com/MIT-LCP/wfdb-python), [NeuroKit2](https://github.com/neuropsychology/NeuroKit), [HeartPy](https://github.com/paulvangentcom/heartrate_analysis_python), [BioSPPy](https://github.com/PIA-Group/BioSPPy).

Alternative tooling focuses on loading, filtering, and downstream analysis. ZPE-Bio focuses on deterministic compression, replay, and audit-ready transport.

Baseline context: gzip leads on MIT-BIH, NSTDB, and EDB. ZPE leads on PTB-XL and the reproduced Sleep-EDF file.

| Proof anchor | Location |
|---|---|
| MIT-BIH golden benchmark | `docs/specs/ZPE_BIOSIGNAL_CODEC_PRD_v1.0.md` |
| ECG validation | `python -m zpe_bio encode-ecg --record-id 100 --samples 1000 --json` |
| Validation results | `validation/results/`, `validation/runbooks/` |
| Family alignment | `docs/family/` |

Part of the [Zer0pa](https://github.com/Zer0pa) family. Platform layer: [ZPE-IMC](https://github.com/Zer0pa/ZPE-IMC).

---

ZPE-Bio is the biosignal sector repository for Zero-Point Encoding. It packages a deterministic 8-primitive biosignal codec, a Rust-backed core codec crate, and Bio-specific validation artifacts for Wave-1 and Wave-2 execution.

## Install

Editable source install:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,validation]"
```

Wheel build:

```bash
python -m pip install build
python -m build
python -m pip install dist/*.whl
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,validation]"
python -m zpe_bio encode-ecg --record-id 100 --samples 1000 --json
```

Examples: `examples/README.md`
Benchmarks: `BENCHMARKS.md`

## Current Reality

- Runtime/package surface exists under `python/zpe_bio/`.
- Native codec surface exists under `core/rust/`.
- Embedded references exist under `embedded/`.
- Proof and readiness artifacts exist under `validation/results/` and `validation/runbooks/`.
- Family alignment artifacts exist under `docs/family/`.

## Current Status Snapshot

- Wave-1 repo substance is real.
- Wave-2 execution artifacts are present but mixed.
- Bio Wearable remains `NO_GO`; its closure bundles are retained for traceability, not treated as release proof.
- Historical validation artifacts preserve host-specific paths and should be read as lineage, not as current path authority.

## What This Repo Proves Today

- The source tree contains runnable Python and Rust codec surfaces.
- The source tree contains committed Wave-1 and Wave-2 readiness artifacts.
- The source tree contains IMC contract-consumption artifacts for family alignment.

## What It Does Not Prove Today

- It does not prove a fresh green release commit.
- It does not prove public-release readiness.
- It does not prove Bio Wearable closure.
- It does not prove that every historical validation artifact path has been normalized.

## Repository Map

- `python/zpe_bio/`: Python package and CLI
- `core/rust/`: Rust codec crate
- `embedded/`: embedded reference builds
- `tests/`: maintained pytest suite
- `scripts/`: operator scripts and generators
- `validation/results/`: committed benchmark outputs and summaries
- `validation/benchmarks/`: benchmark runners and validation entrypoints
- `validation/runbooks/`: execution runbooks
- `docs/`: repo docs, family alignment, and regulatory material

## Audit And Boundaries

- Proof index: `PROOF_INDEX.md`
- Short audit path: `AUDITOR_PLAYBOOK.md`
- Public/operator limits: `PUBLIC_AUDIT_LIMITS.md`
- Docs landing: `docs/README.md`
- Legal boundary summary: `docs/LEGAL_BOUNDARIES.md`

## Open Contradictions

- Historical GO prose exists, but this staged repo still carries unresolved correctness work.
- `ruff` and multimodal manifest verification were not re-cleared in this phase.
- Regulatory and startup documents still contain historical absolute-path references outside the active front door.

Read this repo as the current biosignal proof surface and operator baseline.

## Ecosystem Cross-Links

- Platform-layer contract surface: [ZPE-IMC](https://github.com/Zer0pa/ZPE-IMC)
- Organization surface: [Zer0pa](https://github.com/Zer0pa)
- Bio-family alignment artifacts in this repo: `docs/family/BIO_IMC_ALIGNMENT_REPORT.md`
