# ZPE-Bio Novelty Card

**Product:** ZPE-Bio  
**Domain:** Deterministic biosignal encoding with current public authority on ECG waveforms  
**What we sell:** Auditable ECG encoding and replay for medical-device firmware and clinical-data pipelines

## Novel contributions

1. **Asymmetric 8-state ECG directional quantiser** — ZPE-Bio converts sample deltas into a lane-specific eight-state directional alphabet, then carries those directions through deterministic token packing and replay. Code: [`python/zpe_bio/codec.py`](../../../python/zpe_bio/codec.py) (lines 40-48, 95-170); Rust mirror: [`core/rust/src/quantise.rs`](../../../core/rust/src/quantise.rs) (lines 1-37) and [`core/rust/src/codec.rs`](../../../core/rust/src/codec.rs) (lines 70-158). Nearest prior art (if known): generic delta modulation, chain codes, and run-length encoding. What is genuinely new here: the specific asymmetric delta map, the clinical/transport split around that map, and its use as the governing ECG replay surface with retained proof artifacts.
2. **Weber-Fechner log-magnitude binning inside the ECG token stream** — Clinical mode couples each non-flat direction token to a fixed 64-entry logarithmic magnitude table so micro-volt and milli-volt morphology can live inside one deterministic codec boundary. Code: [`python/zpe_bio/codec.py`](../../../python/zpe_bio/codec.py) (lines 24-27, 160-170); Rust mirror: [`core/rust/src/codec.rs`](../../../core/rust/src/codec.rs) (lines 23-33, 107-126). Nearest prior art (if known): log-domain quantisers in signal compression. What is genuinely new here: the coupling of this exact fixed log table to the directional ECG token stream and its mirrored Python/Rust parity surface.

## Standard techniques used (explicit, not novel)

- Delta encoding
- Run-length encoding
- Adaptive threshold / envelope tracking
- Log-domain quantisation as a general technique
- Python / NumPy numerics
- Rust `no_std` implementation techniques
- WFDB-based ECG dataset ingest

## Compass-8 / 8-primitive architecture

YES — the governing ECG codec uses an 8-state directional map implemented in [`python/zpe_bio/codec.py`](../../../python/zpe_bio/codec.py) (lines 40-48, 95-114) and mirrored in [`core/rust/src/quantise.rs`](../../../core/rust/src/quantise.rs) (lines 1-37).

## Open novelty questions for the license agent

- Should the asymmetric `DIRECTION_DELTAS` / `quantise_ecg` mapping be scheduled as a standalone novelty claim, or only as part of the combined ECG codec?
- Should the 64-entry `LOG_MAG_TABLE` be protected independently, or only when paired with the directional ECG token stream and deterministic parity boundary?
