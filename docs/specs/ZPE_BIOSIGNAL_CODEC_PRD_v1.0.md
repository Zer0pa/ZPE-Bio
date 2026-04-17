# ZPE-Bio: 8-Primitive Biosignal Encoding Product
## Historical Product Requirements Document & Execution Runbook v1.3

**Codename:** Heartbeat  
**Classification:** Historical internal spec retained in the repo and aligned to Zer0pa SAL v6.2 posture
**Date:** 2026-02-11  
**Revision:** v1.3 — Bionic Log-Magnitude Ratified, Host Parity Secured  
**Status:** Historical runbook retained for provenance. Current public authority is the ECG-backed benchmark surface under `validation/results/`; external clinical/legal closure items remain parked by owner directive.

This document is kept as a historical specification and execution runbook. It is not the governing public authority surface. Current public claims should be cross-checked against the retained benchmark summaries under `validation/results/`.

---

## 1. Executive Summary

ZPE-Bio is a deterministic biosignal encoding product designed for high-fidelity ECG monitoring and auditable replay in constrained software and embedded environments. It uses directional 8-primitive waveform encoding plus **Hybrid Delta-Modulation** and **Weber-Fechner Log-Binning** to preserve diagnostic morphology while keeping the encoded stream deterministic.

### 1.1 Core Objectives
- **Deterministic ECG replay**: retain reproducible encode/decode behavior on the public ECG authority corpora.
- **PRD < 5% in clinical mode**: maintain diagnostic-fidelity reconstruction on the validated ECG path.
- **Embedded-capable implementation**: keep the Rust crate and reference targets usable for constrained environments.

---

## 2. Technical Specification

### 2.1 Geometric Primitives
The codec uses a 3-bit directional alphabet (0-7):
- `0`: FLAT (Maintain baseline)
- `1`: NORTH-EAST (Gentle rise)
- `2`: NORTH (Steep rise)
- `3`: NORTH-WEST (Reserved / 2D)
- `4`: WEST (Reserved / 2D)
- `5`: SOUTH-WEST (Reserved / 2D)
- `6`: SOUTH (Steep fall)
- `7`: SOUTH-EAST (Gentle fall)

### 2.2 Dual-Mode Encoding (Phase 1.1 Ratified)

| Mode | Bit Budget | Logic | Use Case |
|:---|:---|:---|:---|
| **TRANSPORT** | ~1.5 bytes/token | Direction-only + RLE | BLE screening, maximum battery life. |
| **CLINICAL** | ~2.125 bytes/token | Dir + Log-Magnitude + RLE | Diagnostic monitoring, regulatory data. |

### 2.3 Bionic Innovation: Weber-Fechner Log-Magnitudes (Phase 1.2 Ratified)
To maintain constant relative error across micro-volt P-waves and milli-volt QRS complexes, the codec uses a **64-entry base-2 logarithmic binning table** for the magnitude field in CLINICAL mode.
- **Table**: `LOG_MAG_TABLE[i] = round(1.091928^i)`
- **Benefit**: Achieves < 3% PRD with 6-bit magnitude indices, outperforming 8-bit linear encoding.

---

## 3. Implementation Status & Metrics

### 3.1 Host Manifold (Phase 1.0 - 1.2)
- [x] **Python Reference**: `codec.py` (Canonical)
- [x] **Rust Core**: `#![no_std]` crate with x86/ARM parity.
- [x] **Parity Success (Re-audit)**: parity passes after Rust rebuild (`python/zpe_bio/test_parity.py`, `DT-13`).
- [x] **Embedded Host Gate (Phase 3)**: `thumbv8m.main-none-eabi` build + DT-6/9/10/13/17 pass in consolidated report `validation/results/phase3_hostok_20260212T113430.json`.

### 3.2 Current Public Authority Snapshot
| Surface | Metric | Value | Source |
|:---|:---|:---|:---|
| **MIT-BIH** | Integrity passes | 48/48 | `validation/results/BENCHMARK_SUMMARY.md` |
| **PTB-XL** | Mean compression ratio | 1.576202x | `validation/results/ptbxl/summary.json` |
| **EDB** | Mean SNR | 52.468288 dB | `validation/results/edb/summary.json` |
| **NSTDB** | Mean SNR | 60.493187 dB | `validation/results/nstdb/summary.json` |

ECG is the governing public authority surface. EEG helpers and wearable paths remain outside the current headline proof boundary.

---

## 4. Falsification Protocol (The Hound of Popper)

### 4.1 Destruct Tests (DT)
- **DT-1 (Shape Destruction)**: Reconstructed QRS morphology audit.
- **DT-2 (Compression Regret)**: High-entropy noise threshold test.
- **DT-12 (Monotonicity)**: Parameter sweep verification.
- **DT-18 (Log-Magnitude Audit)**: Log vs Linear fidelity cross-validation.

### 4.2 Re-Falsification Delta (2026-02-12)

Current reproducible findings:
- Full priority suites are green on latest rerun:
  - P0: `validation/results/dt_results_20260212T130144.json`
  - P1: `validation/results/dt_results_20260212T125025.json`
  - P2: `validation/results/dt_results_20260212T124900.json`
- DT results archive generated: `validation/results/archives/dt_results_archive_20260212T130345.tar.gz`.
- Compression gate alignment fix applied in `DT-2` (transport mode audit path).
- Clinical gate alignment fix applied in benchmark runner (PRD pass restored to `<5%`).
- Phase-3 host gate is green in `validation/results/phase3_hostok_20260212T113430.json`.

Operational consequence:
- Internal execution runbook is complete through Phase 4.
- External clinical/legal closure items remain parked as `SUSPENDED_BY_OWNER` for deferred reactivation.

---

## 5. Execution Runbook

### Phase 1: Host Codec Implementation (COMPLETED)
1. Environment setup and repository skeleton.
2. Python reference implementation (Phase 1.1 Hybrid added).
3. Rust port and cross-validation harrness.
4. Bionic Log-Magnitude optimization (Phase 1.2).

### Current Phase State (2026-02-12)
1. Phase 1: COMPLETE
2. Phase 2: COMPLETE
3. Phase 3: COMPLETE (host-side embedded gate)
4. Phase 4: COMPLETE (owner park directive applied to external closure items)

### Deferred External Items (Parked)
1. Human Equivalence Gate completion (`DOC-012`, cardiologist-labeled kappa >= 0.85) — `SUSPENDED_BY_OWNER`.
2. Final regulatory pathway sign-off (510(k) vs De Novo) by regulatory/legal stakeholders — `SUSPENDED_BY_OWNER`.
3. Optional hardware-strengthening evidence: on-target timing and PPK2 power capture.

---

*This document is a living specification. It evolves through recursive falsification and data-driven pivots. Every claim is verified by byte-identical parity.*
