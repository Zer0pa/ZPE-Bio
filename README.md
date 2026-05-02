# ZPE-Bio

ECG codec, beta. Clinical-mode fidelity-bounded-lossy ECG archival format covering the deterministic PRD <= 2.32% reconstruction contract that lossless byte compressors structurally cannot offer. Shipped as a Python CLI, a Rust core crate, and committed validation artifacts. This README is intentionally limited to claims that are backed by proof artifacts already on disk and by tests that run in CI. ZPE-Bio is one of 17 independent encoding products in the Zer0pa portfolio, each developed for its own domain.

This repo's claimed surface is the clinical-mode ECG fidelity contract only. It does not use the wearable runbooks as release evidence, and it does not make a generalized biosignal or regulatory claim. Scope is bounded to CPU-only Python codec; no hardware acceleration path is implied.

Headline metric: MIT-BIH 48/48 integrity, mean PRD 1.12%, mean SNR 43.3 dB. Backed by proof artifact at [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md) and [`validation/results/mitdb_python_only/mitdb_aggregate.json`](validation/results/mitdb_python_only/mitdb_aggregate.json).

Honest blocker: PTB-XL max PRD reaches 5.29% (100-record sample) — above the clinical 2.32% contract threshold. This is an open boundary; PTB-XL is logged but not claimed under the clinical fidelity contract.

| Field | Value |
| --- | --- |
| Architecture | BIO_STREAM |
| Encoding | BIO_DELTA_V1 |

## What This Is

Fidelity-bounded ECG archival codec. Deterministic PRD <=2.32% contract, Python CLI, Rust core, and MIT-BIH/PTB-XL validation. Install from PyPI: `pip install zpe-bio`

This repo's claimed surface is the clinical-mode ECG fidelity contract only. It does not use the wearable runbooks as release evidence, and it does not make a generalized biosignal or regulatory claim. ZPE-Bio is one of 17 independent encoding products in the Zer0pa portfolio, each developed for its own domain.

## Codec Mechanics

<p>
  <img src=".github/assets/readme/lane-mechanics/BIO.gif" alt="ZPE-Bio Codec Mechanics animation" width="100%">
</p>

| Field | Value |
| ------- | ------- |
| Architecture | BIO_STREAM |
| Encoding | BIO_DELTA_V1 |
| Mechanics Asset | `.github/assets/readme/lane-mechanics/BIO.gif` |

## Key Metrics

| Metric | Value | Baseline |
| -------- | ------- | ---------- |
| MIT-BIH Arrhythmia (mitdb) | 48/48 (100%) | Mean PRD 1.12%, Mean SNR 43.3 dB |
| MIT-BIH Noise Stress (nstdb) | 15/15 (100%) | Mean SNR 60.5 dB |
| European ST-T (edb) | 90/90 (100%) | Mean SNR 52.5 dB |
| PTB-XL (sample) | 100/100 (100%) | Max PRD 5.29% — open boundary |

> Source: `validation/results/BENCHMARK_SUMMARY.md`

## Repo Identity

| Field | Value |
| ------- | ------- |
| Identifier | ZPE-Bio |
| Repository | https://github.com/Zer0pa/ZPE-Bio |
| Section | encoding |
| Visibility | PUBLIC |
| Architecture | BIO_STREAM |
| Encoding | BIO_DELTA_V1 |
| Commit SHA | b57bd19f1609 |
| License | SAL-7.0 |
| Authority Source | validation/results/BENCHMARK_SUMMARY.md |

## Readiness

| Field | Value |
| ------- | ------- |
| Verdict | STAGED |
| Checks | 4/4 |
| Anchors | 4 display anchors |
| Confidence | MEDIUM — clinical-mode MIT-BIH contract met; PTB-XL max PRD exceeds 2.32% threshold (open boundary); regulatory alignment deferred |
| Authority | validation/results/BENCHMARK_SUMMARY.md |

### Honest Blocker

PTB-XL max PRD reaches 5.29% (100-record sample) — above the clinical 2.32% contract threshold. This is an open boundary; PTB-XL is logged but not claimed under the clinical fidelity contract.

## What We Prove

- MIT-BIH 48/48 records processed with 100% integrity pass rate, mean PRD 1.12%, mean SNR 43.3 dB, max PRD 2.32% — within clinical contract.
- MIT-BIH Noise Stress 15/15 records, 100% integrity, mean SNR 60.5 dB, max PRD 1.96%.
- European ST-T 90/90 records, 100% integrity, mean SNR 52.5 dB.
- PTB-XL 100/100 records (sample), 100% integrity.
- Python and Rust codec implementations are parity-gated in CI.
- Deterministic round-trip replay is CI-anchored.

## What We Don't Claim

- No public release-readiness verdict
- No generalized biosignal victory claim
- No Bio Wearable closure claim
- No regulatory or FDA claim

## Verification Status

| Code | Check | Verdict |
| ------ | ------- | --------- |
| V_01 | MIT-BIH benchmark writer emits summary + aggregate artifacts | PASS |
| V_02 | PTB-XL benchmark writer emits committed-style summary artifacts | PASS |
| V_03 | Clinical ECG round-trip remains deterministic and high-fidelity in the Python codec | PASS |
| V_04 | Python and Rust codec implementations remain parity-gated in CI | PASS |

## Proof Anchors

| Path | State |
| ------ | ------- |
| `validation/results/BENCHMARK_SUMMARY.md` | VERIFIED |
| `validation/results/mitdb_python_only/mitdb_aggregate.json` | VERIFIED |
| `validation/results/ptbxl/summary.json` | VERIFIED |
| `tests/test_parity.py` | VERIFIED |

## Repo Shape

| Field | Value |
| ------- | ------- |
| Proof Anchors | 4 display anchors |
| Modality Lanes | 2 |
| Architecture | BIO_STREAM |
| Encoding | BIO_DELTA_V1 |
| Verification | 4/4 checks |
| Authority Source | validation/results/BENCHMARK_SUMMARY.md |

- `python/zpe_bio/`: Python package and CLI
- `core/rust/`: Rust codec crate
- `embedded/`: embedded reference firmware tree
- `tests/`: repo-local pytest suite
- `scripts/`: benchmark and operator scripts
- `validation/results/`: committed benchmark outputs
- `validation/runbooks/`: execution and boundary runbooks
- `docs/`: repo documentation and regulatory/reference material

## Extended Metrics

Rows retained from the previous expanded `## Key Metrics` table. The public product page uses the first four rows only.

| Database | Records | Integrity | Mean PRD | Mean SNR |
| --- | ---: | ---: | ---: | ---: |
| PTB-XL (100-record sample) | 100/100 | 100% | — | 32.0 dB |

## Competitive Benchmarks

ZPE-Bio is a fidelity-bounded-lossy ECG codec (clinical mode, mean PRD ~1.12%, max PRD <= 2.32% on MIT-BIH). gzip, zlib, and zstd are general-purpose lossless byte compressors. Direct compression-ratio comparison is not apples-to-apples: ZPE-Bio's CR is intrinsically bounded by its clinical fidelity contract, while lossless compressors achieve whatever CR the byte distribution permits at zero error. The honest comparison reports both CRs and the fidelity contract, not a single "winner".

| Codec | Mean CR | Median CR | Fidelity |
| --- | ---: | ---: | --- |
| ZPE-Bio | 1.323 | 1.316 | bounded-lossy, PRD <= 2.32% (mean ~1.12%) |
| gzip (level 6) | 1.429 | 1.408 | lossless |
| zlib (level 6) | 1.429 | 1.408 | lossless |
| zstd (level 3) | 1.412 | 1.394 | lossless |

On raw compression ratio alone, ZPE-Bio (mean CR 1.323) loses to gzip, zlib, zstd (gzip 1.429, zlib 1.429, zstd 1.412). This is expected and does not invalidate the lane: ZPE-Bio is a fidelity-bounded-lossy clinical ECG codec (mean PRD ~1.12%, max PRD <= 2.32% on MIT-BIH); gzip/zlib/zstd are lossless general-purpose compressors. The two are not commensurable as a single CR number. ZPE-Bio's value proposition is deterministic, bounded-error reconstruction with a clinical fidelity contract, not raw CR supremacy over lossless byte compressors.

Note on input scope: lossless comparator CRs above are computed over the full raw int16 `.dat` byte stream of each MIT-BIH record; ZPE-Bio CRs are taken from the lane's existing aggregate, computed over a 10000-sample clinical-mode window per record. Both surfaces are recorded in the proof artifact below.

Proof: [proofs/artifacts/comp_benchmarks/mitbih_codec_comparison.json](proofs/artifacts/comp_benchmarks/mitbih_codec_comparison.json)

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,validation]"
python -m zpe_bio roundtrip --mode clinical --samples 250
```

Further reading:

- [`validation/results/README.md`](validation/results/README.md)
- [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/LEGAL_BOUNDARIES.md`](docs/LEGAL_BOUNDARIES.md)

---

### MIT-BIH Arrhythmia Database (48 records, full corpus)

| Metric | Value |
| --- | ---: |
| Records processed | 48/48 |
| Integrity pass rate | 48/48 (100%) |
| Mean compression ratio | 1.323 |
| Mean SNR | 43.3 dB |
| Mean RMSE | 3.24 uV |
| Mean PRD | 1.12% |
| Max PRD | 2.32% |

Source: [`validation/results/BENCHMARK_SUMMARY.md`](validation/results/BENCHMARK_SUMMARY.md), [`validation/results/mitdb_python_only/mitdb_aggregate.json`](validation/results/mitdb_python_only/mitdb_aggregate.json) | CI: [`tests/test_benchmark_mitdb.py`](tests/test_benchmark_mitdb.py)

### MIT-BIH Noise Stress Test Database (nstdb, 15 entries)

| Metric | Value |
| --- | ---: |
| Records processed | 15/15 |
| Integrity pass rate | 15/15 (100%) |
| Mean compression ratio | 1.310 |
| Mean SNR | 60.5 dB |
| Max PRD | 1.96% |

Source: [`validation/results/nstdb/summary.json`](validation/results/nstdb/summary.json) | CI: [`tests/test_benchmark_physionet.py`](tests/test_benchmark_physionet.py)

### European ST-T Database (edb, 90 entries)

| Metric | Value |
| --- | ---: |
| Records processed | 90/90 |
| Integrity pass rate | 90/90 (100%) |
| Mean compression ratio | 1.376 |
| Mean SNR | 52.5 dB |
| Max PRD | 4.34% |

Source: [`validation/results/edb/summary.json`](validation/results/edb/summary.json) | CI: [`tests/test_benchmark_physionet.py`](tests/test_benchmark_physionet.py)

### PTB-XL ECG Database (100 records sample)

| Metric | Value |
| --- | ---: |
| Records processed | 100/100 |
| Integrity pass rate | 100/100 (100%) |
| Mean compression ratio | 1.576 |
| Mean SNR | 32.0 dB |
| Max PRD | 5.29% |

Source: [`validation/results/ptbxl/summary.json`](validation/results/ptbxl/summary.json) | CI: [`tests/test_benchmark_physionet.py`](tests/test_benchmark_physionet.py)

**Note on PTB-XL SNR/PRD:** PTB-XL records are 12-lead 500 Hz clinical studies; the lower SNR relative to MIT-BIH reflects higher signal diversity and more channels compressed per segment, not codec regression. Integrity passes 100/100.

## Upcoming Workstreams

This section captures the active lane priorities — what the next agent or contributor picks up, and what investors should expect. Cadence is continuous, not milestoned.

- **Rust embedded encode/decode path** — Active Engineering. Wearable-cardiac-monitor wedge requires sub-ms latency and constrained-resource execution; foundation primitives are mature.
- **Regulatory alignment scoping (IEC 60601 / FDA)** — Research-Deferred — Investigation Underway. The PRD-bounded fidelity contract is a regulatory moat that lossless coders cannot match; alignment work scopes the path to clinical submission.
