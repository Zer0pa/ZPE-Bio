# ZPE-Bio

---

## What This Is

**ZPE-Bio applies the ZPE deterministic 8-primitive encoding architecture to biosignal domains — ECG and EEG.**

The codec ships in both Rust (core/rust/) and Python (python/zpe_bio/), with embedded reference builds under embedded/.

Wave-1 and Wave-2 readiness artifacts are committed under validation/results/ and validation/runbooks/.

ECG validation runs deterministic round-trip fidelity checks against real records: python -m zpe_bio encode-ecg --record-id 100 --samples 1000 --json.

| Field | Value |
|-------|-------|
| Architecture | BIO_WAVEFORM |
| Encoding | ECG_DELTA_V1 |

## Key Metrics

| Metric | Value | Baseline |
|--------|-------|----------|
| ECG_SNR | 43.29 dB | — |
| RMSE | 3.24 μV | — |
| COMPRESSION | 1.32× | vs gzip ~2× (lossless) |
| INTEGRITY | 48/48 | pass |

## What We Prove

- 8-code delta quantization decomposes ECG signals into directional primitives
- Deterministic round-trip fidelity verified across MIT-BIH's full 48-record corpus
- Dual implementation surface: Rust core crate and Python package with parity checks
- Heterogeneous biosignal transport via shared primitive layer (ECG, EEG, wearable)
- IMC contract-consumption alignment verified on the staged pipeline

## What We Don't Claim

- No claim of fresh green release commit
- No claim of public release readiness
- No claim of Bio Wearable validation (NO_GO)
- No claim of regulatory or FDA compliance

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | STAGED |
| Commit SHA | 83DC916 |
| Confidence | 100% (MIT-BIH integrity passes) |
| Source | proofs/FINAL_STATUS.md |

## Tests and Verification

| Code | Check | Verdict |
|------|-------|---------|
| V_01 | MIT-BIH_INTEGRITY_PASSES_(48/48) | PASS |
| V_02 | PTB-XL_BENCHMARK_SUMMARY_COMMITTED | PASS |
| V_03 | NSTDB_BENCHMARK_SUMMARY_COMMITTED | PASS |
| V_04 | EDB_BENCHMARK_SUMMARY_COMMITTED | PASS |
| V_05 | SLEEP-EDF_SINGLE-FILE_BENCHMARK_... | PASS |
| V_06 | BIO_WEARABLE_GATE | FAIL |

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

ZPE-Bio is the biosignal sector repository for Zero-Point Encoding. It packages a deterministic 8-primitive biosignal codec, a Rust-backed core codec crate, and Bio-specific validation artifacts for Wave-1 and Wave-2 execution.

This repository is a private staging surface as of 2026-03-09. It is not a public release packet and it is not a clean green-verification snapshot.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m zpe_bio --help
python -m zpe_bio roundtrip --mode clinical --samples 250
```

For ECG validation commands:

```bash
python -m pip install -e ".[validation]"
python -m zpe_bio encode-ecg --record-id 100 --samples 1000 --json
```

Optional EEG support requires extra packages and local dataset acquisition:

```bash
python -m pip install -e ".[validation,bioeeg]"
```

## Ecosystem

- Platform-layer contract surface: [ZPE-IMC](https://github.com/zer0-point-energy/ZPE-IMC)
- Organization surface: [Zer0pa](https://github.com/zer0-point-energy)
- Bio-family alignment artifacts in this repo: `docs/family/BIO_IMC_ALIGNMENT_REPORT.md`

## Current Reality

- Runtime/package surface exists under `python/zpe_bio/`.
- Native codec surface exists under `core/rust/`.
- Embedded references exist under `embedded/`.
- Proof and readiness artifacts exist under `validation/results/` and `validation/runbooks/`.
- Family alignment artifacts exist under `docs/family/`.
- The source tree contains runnable Python and Rust codec surfaces.
- The source tree contains committed Wave-1 and Wave-2 readiness artifacts.
- The source tree contains IMC contract-consumption artifacts for family alignment.

## Current Status Snapshot

- Wave-1 repo substance is real.
- Wave-2 execution artifacts are present but mixed.
- Bio Wearable remains `NO_GO`; its closure bundles are retained for traceability, not treated as release proof.
- Historical validation artifacts preserve host-specific paths and should be read as lineage, not as current path authority.
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
- `validation/results/`: committed proof and readiness artifacts
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

Read this repo as a private staged baseline for Phase 4.5 and Phase 5, not as a release verdict.
