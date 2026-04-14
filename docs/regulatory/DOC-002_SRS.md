# DOC-002: Software Requirements Specification (SRS)

**Document ID:** DOC-002  
**Version:** 1.0  
**Date:** 2026-02-12  
**Classification:** IEC 62304 §5.2

## 1. Functional Requirements

| Requirement ID | Requirement | Verification |
|:---|:---|:---|
| REQ-CODEC-1 | Encode biosignals using deterministic geometric primitive stream | DT-1, DT-5 |
| REQ-CODEC-2 | Deterministic quantisation without stochastic drift | DT-3, DT-12 |
| REQ-CODEC-3 | RLE token stream compression support | DT-2 |
| REQ-CODEC-4 | Adaptive threshold operation for ECG fidelity | DT-15 |
| REQ-CODEC-5 | PPG encoding support | DT-16 |
| REQ-BLE-1 | Framing with CRC corruption detection | DT-17 |

## 2. Embedded Constraints

| Requirement ID | Requirement | Limit | Verification |
|:---|:---|:---|:---|
| REQ-EMBED-1 | Codec static RAM budget | <= 32768 bytes | DT-6 |
| REQ-EMBED-2 | Power budget proxy | < 5 mW avg (duty-cycle proxy) | DT-9 |
| REQ-EMBED-3 | Encoding latency | < 1 ms / 250-sample window | DT-10 |

## 3. Security and Reliability

| Requirement ID | Requirement | Verification |
|:---|:---|:---|
| REQ-SEC-1 | No observable data-dependent timing leak in host audit | DT-14 |
| REQ-DET-1 | Host and ARM-manifold deterministic parity controls | DT-13 |

## 4. Regulatory Requirements

| Requirement ID | Requirement | Verification |
|:---|:---|:---|
| REQ-REG-1 | IEC 62304 Class B documentation package | DOC-001..DOC-012 |
| REQ-REG-2 | Cardiologist equivalence kappa >= 0.85 | DOC-012 |

## 5. Traceability

See `docs/regulatory/traceability/REQ_DT_MATRIX.md`.
