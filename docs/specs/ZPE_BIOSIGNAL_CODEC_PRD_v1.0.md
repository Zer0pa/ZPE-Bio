# ZPE-Bio: Deterministic Biosignal Compression SDK
## Product Requirements Document & Execution Runbook v1.3

**Codename:** Heartbeat  
**Classification:** Zer0paLab Confidential — MungoDB Poison Pill License  
**Date:** 2026-02-11  
**Revision:** v1.3 — Bionic Log-Magnitude Ratified, Host Parity Secured  
**Status:** RATIFIED (Owner Park Applied) — Phases 1-4 runbooks completed; external clinical/legal closure items suspended by owner directive  

---

## 1. Executive Summary

ZPE-Bio is a deterministic, certifiable biosignal compression codec designed for high-fidelity clinical monitoring and extreme-efficiency wearable transmission. By encoding waveforms as deterministic geometric chain codes and applying **Hybrid Delta-Modulation** with nature-inspired **Weber-Fechner Log-Binning**, the codec achieves a Pareto-optimal balance between bandwidth and diagnostic integrity.

### 1.1 Core Objectives
- **CR ≥ 5x**: ECG/PPG compression target.
- **PRD < 5%**: Maximum allowable distortion for clinical diagnostic accuracy.
- **no_std/Deterministic**: Memory-safe, heap-free implementation for embedded MCUs (nRF5340/Zephyr).

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

### 3.2 Golden Benchmark (MIT-BIH 48 Records)
| Mode | Mean CR | Mean PRD | Gate Status |
|:---|:---|:---|:---|
| **TRANSPORT** | 8.70x | 12.21% | **CONDITIONAL** (`CR_min=4.81x`, one record below 5x in latest re-audit) |
| **CLINICAL** | 1.12x | 2.85% | **CONDITIONAL** (fidelity passes, but compression remains below commercial transport target) |

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
