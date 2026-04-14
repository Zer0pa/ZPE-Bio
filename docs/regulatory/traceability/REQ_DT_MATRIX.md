# Requirements to Destruct Test Traceability Matrix

Evidence sources used:

- `/Users/zer0pa-build/ZPE Bio/zpe-bio/validation/results/dt_results_20260212T104642.json`
- `/Users/zer0pa-build/ZPE Bio/zpe-bio/validation/results/dt_results_20260212T112710.json`
- `/Users/zer0pa-build/ZPE Bio/zpe-bio/validation/results/dt_results_20260212T103331.json`
- `/Users/zer0pa-build/ZPE Bio/zpe-bio/validation/results/phase3_hostok_20260212T113430.json`

| Requirement ID | Description | DT(s) | DT Status | Evidence |
|:---|:---|:---|:---|:---|
| REQ-CODEC-1 | 8-primitive chain code | DT-1, DT-5 | PASS | `dt_results_20260212T104642.json` |
| REQ-CODEC-2 | Quantisation to active directions | DT-3, DT-12 | PASS | `dt_results_20260212T104642.json`, `dt_results_20260212T112710.json` |
| REQ-CODEC-3 | RLE compression | DT-2 | PASS | `dt_results_20260212T104642.json` |
| REQ-CODEC-4 | Adaptive threshold | DT-15 | PASS | `dt_results_20260212T104642.json` |
| REQ-CODEC-5 | PPG codec | DT-16 | PASS | `dt_results_20260212T104642.json` |
| REQ-EMBED-1 | RAM <= 32 KB | DT-6 | PASS | `phase3_hostok_20260212T113430.json` |
| REQ-EMBED-2 | Power budget | DT-9 | PASS | `dt_results_20260212T112710.json`, `phase3_hostok_20260212T113430.json` |
| REQ-EMBED-3 | Encode < 1 ms | DT-10 | PASS | `dt_results_20260212T112710.json`, `phase3_hostok_20260212T113430.json` |
| REQ-BLE-1 | Packet framing with CRC | DT-17 | PASS | `dt_results_20260212T112710.json`, `phase3_hostok_20260212T113430.json` |
| REQ-SEC-1 | No data-dependent timing | DT-14 | PASS | `dt_results_20260212T103331.json` |
| REQ-REG-1 | IEC 62304 Class B package | DOC-001..DOC-012 | IN_PROGRESS | `/Users/zer0pa-build/ZPE Bio/zpe-bio/docs/regulatory/` |
| REQ-REG-2 | Cardiologist kappa >= 0.85 | Human Equiv Gate | SUSPENDED_BY_OWNER | `DOC-012_HUMAN_EQUIVALENCE_GATE_REPORT.md` |
| REQ-REG-3 | MIT-BIH benchmark coverage | DT-1 | PASS | `dt_results_20260212T104642.json` |

## Residual Risk Notes

- DT-9 and DT-10 are currently host-side proxies for embedded runtime behavior.
- On-target timing and power capture are recommended follow-up evidence when hardware instrumentation is available.
