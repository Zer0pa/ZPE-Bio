# ZPE-Bio Spec Constants (Repo Canonical)

Date: 2026-02-19  
Source of truth for this repository release candidate: `python/zpe_bio/codec.py` and `core/rust/src/codec.rs`.

## Encoding and Sampling

| Constant | Value | Python Source | Rust Source |
| --- | --- | --- | --- |
| ECG sample rate | `250` Hz | `ECG_SAMPLE_RATE` | input-context, unchanged |
| PPG sample rate | `100` Hz | `PPG_SAMPLE_RATE` | input-context, unchanged |
| Max RLE run length | `65535` | `MAX_RLE_COUNT` | `u16::MAX` guard in encoder |

## Adaptive Threshold (Clinical Path)

| Constant | Value | Python | Rust |
| --- | --- | --- | --- |
| `ADAPTIVE_K` | `0.15` | `ADAPTIVE_K` | `ADAPTIVE_K` |
| `ADAPTIVE_THR_MIN` | `0.001` | `ADAPTIVE_THR_MIN` | `ADAPTIVE_THR_MIN` |
| `ADAPTIVE_ALPHA` | `0.95` | `ADAPTIVE_ALPHA` | `ADAPTIVE_ALPHA` |

## Mode Defaults

| Mode | Threshold | Step | Notes |
| --- | --- | --- | --- |
| `transport` | `0.050` | `0.050` | direction-only + RLE |
| `clinical` | `0.001` | `0.001` | direction + log-magnitude + RLE |

## Magnitude Quantization

1. `LOG_MAG_TABLE` has 64 entries.
2. Binning base is `1.091928`.
3. Python/Rust parity is enforced through `tests/test_parity.py`.

## Reconciliation Note

External historical runbooks may reference older threshold floors. For this repo productization cycle, the values above are authoritative and parity-tested.
