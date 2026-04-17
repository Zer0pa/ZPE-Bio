# Reorientation Open Questions — 2026-04-17

- License scope question: should the asymmetric `DIRECTION_DELTAS` / `quantise_ecg` map be protected as a standalone novelty, or only as part of the combined ECG codec? I treated it as part of the combined codec because delta-quantisation prior art is broad.
- License scope question: should the 64-entry `LOG_MAG_TABLE` be scheduled independently, or only when paired with the directional ECG token stream and deterministic Python / Rust parity surface? I described it as codec-coupled because the standalone table resembles generic log quantisation.
- Product-surface question: auxiliary EEG and multimodal helpers remain in the repo, but I demoted them from headline authority. If they are intended to stay long-term, a later pass may want an explicit experimental boundary for those commands.
