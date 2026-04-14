# DOC-007: Software System Testing Report

**Document ID:** DOC-007  
**Version:** 1.0  
**Date:** 2026-02-12  
**Classification:** IEC 62304 §5.7

## 1. System Test Inputs

- MIT-BIH corpus tests and falsification harness
- Cross-platform parity checks
- Embedded target compile and section audits

## 2. Current System Metrics Snapshot

From `validation/results/phase3_hostok_20260212T113430.json`:

- DT-6 static RAM: 1088 bytes
- DT-9 mean TX reduction: 9.04x
- DT-9 min TX reduction: 5.58x
- DT-10 mean latency: 0.0200 ms
- DT-10 p99 latency: 0.0311 ms
- DT-17 CRC detection: 100.000%

## 3. Verdict

System-level software gates are currently PASS for host and embedded-proxy validation paths.

## 4. Open External Test Requirement

Human Equivalence Gate (kappa >= 0.85) is pending external cardiologist evaluation.
