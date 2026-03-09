# DOC-008: Risk Management File (RMF)
## ZPE-Bio Codec

**Document ID:** DOC-008  
**Version:** 1.0  
**Date:** 2026-02-12  
**Classification:** IEC 62304 §7 / ISO 14971 aligned

| Hazard ID | Hazard | Severity | Probability | RPN | Mitigation | Residual Risk |
|:---|:---|:---|:---|:---|:---|:---|
| H-001 | Excessive signal distortion causes missed arrhythmia | Critical | Low | 6 | DT-1, DT-5, clinical-mode controls, Human Equivalence Gate | Low |
| H-002 | Embedded memory overrun causes monitor failure | Critical | Low | 6 | DT-6, fixed-capacity data structures, stack proxy guard | Low |
| H-003 | BLE payload corruption alters transmitted data | Major | Medium | 6 | DT-17 CRC-16-CCITT framing and detection checks | Low |
| H-004 | Threshold dynamics degrade morphology | Major | Medium | 6 | DT-15 adaptive-threshold tests and fallback profiles | Low |
| H-005 | PPG fidelity loss affects derived signals | Major | Low | 3 | DT-16 modality-specific audit | Low |
| H-006 | Cross-platform divergence causes inconsistent output | Major | Low | 3 | DT-13 parity + ARM compile audit | Very Low |
| H-007 | Excessive power draw shortens operational window | Minor | Low | 2 | DT-9 duty-cycle power regression checks | Very Low |

## Open Risks Requiring External Closure

- Clinical equivalence risk cannot be closed without cardiologist-labeled outcomes (`DOC-012`).
- Hardware runtime confirmation (on-target timer and power instrumentation) is recommended for regulatory confidence, though host gate is currently passing.
