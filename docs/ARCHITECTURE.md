# Architecture

This document maps the current ZPE-Bio product surface.

## Runtime Surface

- `python/zpe_bio/codec.py`: governing ECG codec surface; directional delta quantisation and log-magnitude encoding live here
- `python/zpe_bio/cli.py`: CLI entry point for roundtrip, ECG, benchmark, and auxiliary EEG/multimodal commands
- `python/zpe_bio/bio_wave2.py`: ECG ingest helpers plus auxiliary EEG, chemosense, and multimodal wiring
- `python/zpe_bio/multimodal/`: auxiliary smell, taste, touch, mental, and diagram helpers not used as the current headline authority surface

## Native Surface

- `core/rust/`: Rust codec crate and FFI boundary

## Embedded Surface

- `embedded/nrf5340/`: embedded reference target
- `embedded/stm32wb/`: embedded reference target material

## Validation Surface

- `tests/`: maintained pytest suite
- `validation/results/`: committed readiness and proof artifacts
- `validation/runbooks/`: execution runbooks
- `validation/benchmarks/`: benchmark runners
- `validation/destruct_tests/`: destructive/falsification checks

Current retained public authority is ECG. EEG helpers and multimodal commands are part of the repo surface, but they are not benchmarked to the same level as the ECG path.

## Data Surface

- `validation/datasets/mitdb/`: staged ECG dataset mirror used by Bio Wave-1 and Wave-2 ECG flows
- `validation/datasets/eeg/`, `validation/datasets/sisfall/`, `validation/datasets/wearable_device_dataset/`: local-only mirrors intentionally excluded from staged git scope

## Repo-Boundary Rule

The canonical repo root is this inner `zpe-bio/` directory only. Nothing in the outer workspace wrapper is part of the staged GitHub repo.
