# DOC-003: Software Architecture Document (SAD)

**Document ID:** DOC-003  
**Version:** 1.0  
**Date:** 2026-02-12  
**Classification:** IEC 62304 §5.3

## 1. Architecture Overview

ZPE-Bio architecture has three layers:

1. Core codec layer (`core/rust`, `python/zpe_bio/codec.py`)
2. Validation layer (`validation/destruct_tests`, benchmarks)
3. Embedded integration layer (`embedded/nrf5340`)

## 2. Core Components

| Component | Path | Responsibility |
|:---|:---|:---|
| Quantiser | `core/rust/src/quantise.rs` | Deterministic direction mapping |
| Encoder/Decoder | `core/rust/src/codec.rs` | Stream encode/decode and token assembly |
| RLE | `core/rust/src/rle.rs` | Run-length token compression |
| FFI | `core/rust/src/ffi.rs` | Host binding surface for parity/latency checks |

## 3. Validation Components

| Component | Path | Responsibility |
|:---|:---|:---|
| DT runner | `validation/destruct_tests/run_all_dts.py` | Structured DT execution |
| Benchmarks | `validation/benchmarks/*.py` | Dataset-wide and phase-specific metrics |
| Result artifacts | `validation/results/*.json` | Timestamped immutable evidence |

## 4. Embedded Components

| Component | Path | Responsibility |
|:---|:---|:---|
| Target config | `embedded/nrf5340/.cargo/config.toml` | Thumb target and linker args |
| Firmware entry | `embedded/nrf5340/src/main.rs` | Main loop scaffold and encode smoke path |
| Linker memory map | `embedded/nrf5340/memory.x` | Flash/RAM region bounds |

## 5. Safety-Relevant Design Decisions

- No heap allocation in embedded path (fixed-capacity data structures).
- Deterministic tokenization and parity controls.
- CRC framing test for transmission-integrity risk reduction.

## 6. Residual Architecture Risks

- On-target power and timing need hardware instrumentation for final closure.
- Human-equivalence requirement depends on external clinical review.
