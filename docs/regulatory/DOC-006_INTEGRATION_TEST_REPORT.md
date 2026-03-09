# DOC-006: Software Integration Test Report

**Document ID:** DOC-006  
**Version:** 1.0  
**Date:** 2026-02-12  
**Classification:** IEC 62304 §5.6

## 1. Integration Scope

- DT suites across P0/P1/P2 priorities
- Rust/Python parity integration
- Embedded thumb compile integration

## 2. Evidence Artifacts

- `/Users/prinivenpillay/ZPE Bio/zpe-bio/validation/results/dt_results_20260212T104642.json` (P0)
- `/Users/prinivenpillay/ZPE Bio/zpe-bio/validation/results/dt_results_20260212T112710.json` (P1)
- `/Users/prinivenpillay/ZPE Bio/zpe-bio/validation/results/dt_results_20260212T103331.json` (P2)
- `/Users/prinivenpillay/ZPE Bio/zpe-bio/validation/results/phase3_hostok_20260212T113430.json` (Phase 3 host gate)

## 3. Gate Summary

| Gate | Status |
|:---|:---|
| Phase 1 integration gate | PASS |
| Phase 2 falsification gate | PASS |
| Phase 3 embedded host gate | PASS |

## 4. Residual Integration Notes

- DT-9 and DT-10 currently represent host proxies for embedded runtime behavior.
- Hardware instrumentation is recommended for production-evidence strengthening.
