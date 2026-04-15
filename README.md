# ZPE-Bio

---

## What This Is

Deterministic biosignal compression where reproducibility is mandatory. ECG round-trip fidelity validated against MIT-BIH, PTB-XL, EDB, and NSTDB records — dual Rust and Python codec with embedded reference builds.

For medical-device firmware teams and clinical-data infrastructure engineers: this is the only lane in the family with both a Rust crate and Python package targeting the same signal domain, plus an embedded reference path. The proof lineage is auditable but the release surface is not green. **Bio Wearable is NO_GO** — its closure bundles are retained for traceability, not treated as release proof.

**Readiness: private-stage (2026-03-09).** Not a public release packet. Not a clean green-verification snapshot. Historical validation artifacts preserve host-specific paths (lineage, not path authority).

Part of the [Zer0pa](https://github.com/zer0-point-energy) family. Platform layer: [ZPE-IMC](https://github.com/zer0-point-energy/ZPE-IMC).

| Field | Value |
|-------|-------|
| Architecture | BIO_WAVEFORM |
| Encoding | ECG_DELTA_V1 |

## Key Metrics

| Metric | Value | Baseline |
|--------|-------|----------|
| DETERMINISM | 3/3 | strict encode-decode replay |
| MIT-BIH | 48/48 | — |
| PTB-XL | 1.58× | 100/100 entries |
| NSTDB_SNR | 60.49 | dB |

> Source: [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md) | [`validation/results/ptbxl/summary.json`](validation/results/ptbxl/summary.json) | [`validation/results/edb/summary.json`](validation/results/edb/summary.json) | [`validation/results/nstdb/summary.json`](validation/results/nstdb/summary.json)

## Competitive Benchmarks

| Tool | MIT-BIH CR | Notes |
|------|-----------|-------|
| **ZPE-Bio** | **1.32×** | Deterministic, bit-identical domain-aware replay |
| gzip | 2.13× | Higher CR but no deterministic integrity guarantee |

ZPE-Bio targets deterministic integrity, not compression ratio. Gzip achieves higher compression (2.13× vs 1.32×) on MIT-BIH data but does not guarantee bit-identical domain-aware replay. The commercial wedge is determinism + integrity, not raw ratio.

## What We Prove

> Auditable guarantees backed by committed proof artifacts. Start at `AUDITOR_PLAYBOOK.md`.

- Deterministic round-trip fidelity on ECG waveforms
- Dual implementation: Rust core crate and Python package
- Wave-1 and Wave-2 readiness artifacts committed
- IMC contract-consumption alignment verified

## What We Don't Claim

- No claim of fresh green release commit
- No claim of public release readiness
- No claim of Bio Wearable validation (NO_GO)
- No claim of regulatory or FDA compliance
- No claim of NaN-safe input handling — NaN inputs produce silently incorrect reconstruction (PRD=0.0 reported). This is a known limitation with implications for clinical/regulated deployment. Input validation is the caller's responsibility.

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | PRIVATE_STAGE |
| Commit SHA | 83dc91685284 |
| Confidence | 100% (MIT-BIH integrity passes) |
| Source | validation/results/BENCHMARK_SUMMARY.md |

> **Evaluators:** `pip install zpe-bio` (available on PyPI), then run `pytest`. Contact hello@zer0pa.com for integration guidance.

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

ZPE-Bio is the biosignal sector repository for Zero-Point Encoding. It packages a deterministic 8-primitive biosignal codec, a Rust-backed core codec crate, and Bio-specific validation artifacts for Wave-1 and Wave-2 execution.

This repository is a private staging surface as of 2026-03-09. It is not a public release packet and it is not a clean green-verification snapshot.

## Quick Start

```bash
# Install from PyPI
pip install zpe-bio
```

Or install from source (development):

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

## Who This Is For

| | |
|---|---|
| **Ideal first buyer** | Medical-device firmware team or clinical-data infrastructure team evaluating deterministic biosignal encoding |
| **Pain statement** | Biosignal pipelines require reproducibility and auditability — generic compressors are non-deterministic or domain-agnostic |
| **Deployment model** | Python package + Rust crate, private staged |
| **Family position** | Staged validation lane — proves the architecture extends to regulated biosignal domains |

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
- Regulatory and startup documents contained historical absolute-path references (scrubbed 2026-04-14; now repo-relative).

Read this repo as a private staged baseline for Phase 4.5 and Phase 5, not as a release verdict.
