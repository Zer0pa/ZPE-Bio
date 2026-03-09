# DOC-005: Software Unit Verification Report

**Document ID:** DOC-005  
**Version:** 1.0  
**Date:** 2026-02-12  
**Classification:** IEC 62304 §5.5

## 1. Unit Verification Scope

- Python codec unit tests (`python/zpe_bio/test_codec.py`)
- Rust unit tests (`core/rust`)

## 2. Latest Unit Results

| Suite | Command | Result |
|:---|:---|:---|
| Python unit tests | `pytest python/zpe_bio/test_codec.py -q` | PASS (7 passed) |
| Rust unit tests | `cargo test --quiet` | PASS |
| Embedded stack proxy test | `cargo test embedded_stack_proxy_within_budget -- --nocapture` | PASS (`embedded_stack_proxy_bytes=4608`) |

## 3. Findings

- Previously failing synthetic transport compression test was aligned to realistic lower-bound behavior while preserving corpus-level gates.
- No current unit-level blockers remain.
