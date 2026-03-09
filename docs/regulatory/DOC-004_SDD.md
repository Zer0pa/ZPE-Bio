# DOC-004: Software Detailed Design (SDD)

**Document ID:** DOC-004  
**Version:** 1.0  
**Date:** 2026-02-12  
**Classification:** IEC 62304 §5.4

## 1. Quantisation Design

- Input: delta between current sample and reconstructed sample.
- Output: direction code in 3-bit domain.
- Decision logic: thresholded absolute delta with sign-aware mapping.

## 2. Token Stream Design

- Token tuple: `(direction, magnitude_index, run_count)`.
- Transport mode uses fixed magnitude index.
- Clinical mode maps magnitudes via log table.

## 3. RLE Design

- Consecutive identical `(direction, magnitude)` tokens are merged.
- Run count saturates at `u16::MAX`.
- Decoding expands runs deterministically in-order.

## 4. FFI Boundary Design

- `zpe_encode` is the exported C ABI function.
- Input pointers are converted to slices with caller-provided lengths.
- Output capacity is caller-controlled; overflow returns explicit error code.

## 5. Embedded Main-Loop Design

- Entry point configures minimal no_std runtime.
- 1-second window placeholder is encoded using transport profile.
- Idle behavior uses `wfi()` to preserve low-power semantics.

## 6. Defensive Controls

- Deterministic parity test between Python and Rust token streams.
- DT-17 CRC error-detection check with injected corruption.
- Stack proxy guard test in Rust unit tests (`embedded_stack_proxy_within_budget`).
