# Reorientation Open Questions — 2026-04-17

- License scope question: should the asymmetric `DIRECTION_DELTAS` / `quantise_ecg` map be protected as a standalone novelty, or only as part of the combined ECG codec? I treated it as part of the combined codec because delta-quantisation prior art is broad.
- License scope question: should the 64-entry `LOG_MAG_TABLE` be scheduled independently, or only when paired with the directional ECG token stream and deterministic Python / Rust parity surface? I described it as codec-coupled because the standalone table resembles generic log quantisation.
