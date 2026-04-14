# DOC-001: Software Development Plan (SDP)
## ZPE-Bio 8-Primitive Biosignal Compression Codec

**Document ID:** DOC-001  
**Version:** 1.0  
**Date:** 2026-02-12  
**Author:** Codex Execution Agent  
**Classification:** IEC 62304 §5.1

## 1. Purpose

This document defines the software development process and controls for ZPE-Bio, an 8-primitive biosignal compression codec targeting host and embedded medical-adjacent workflows.

## 2. Scope

- Software item: `zpe-bio-codec` and associated validation harness
- Safety classification: IEC 62304 Class B
- Platforms: x86-64 host and ARM Cortex-M (`thumbv8m.main-none-eabi`)

## 3. Development Lifecycle

- Model: falsification-driven V-model
- Source control: Git repository under `<repo-root>`
- Validation framework: DT-1 through DT-17
- Gating control: `RUNBOOK_00_MASTER.md` phase gates

## 4. Development Environment

- Rust toolchain: stable 1.90 (host), nightly for selected analysis utilities
- Python runtime: `.venv` in repo root
- Key datasets: MIT-BIH Arrhythmia (`validation/datasets/mitdb`)
- Build targets: `x86_64-apple-darwin`, `thumbv8m.main-none-eabi`

## 5. SOUP Inventory

| SOUP | Version Band | Justification |
|:---|:---|:---|
| heapless | 0.8.x | Fixed-capacity no_std collections |
| defmt / defmt-rtt | 0.3 / 0.4 | Embedded diagnostics |
| numpy | 1.x | Numeric operations for reference implementation |
| wfdb | 4.x | MIT-BIH loading and decoding |

## 6. Risk Management Reference

See `docs/regulatory/DOC-008_RMF.md`.

## 7. Verification Strategy

- Unit: Python pytest + Rust unit tests
- Integration: P1/P2 DT suites
- System: MIT-BIH benchmark and host/embedded-proxy Phase 3 gates
- Acceptance: Human Equivalence Gate (`DOC-012`)

## 8. Configuration Management

See `docs/regulatory/DOC-010_CONFIGURATION_MANAGEMENT_PLAN.md`.
