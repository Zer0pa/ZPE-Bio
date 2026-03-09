# Architecture

This document maps the current ZPE-Bio staged repo structure.

## Runtime Surface

- `python/zpe_bio/codec.py`: reference biosignal codec
- `python/zpe_bio/cli.py`: CLI entry point for roundtrip, ECG, EEG, benchmark, multimodal, and chemosense commands
- `python/zpe_bio/bio_wave2.py`: Wave-2 command helpers and dataset/error wiring
- `python/zpe_bio/multimodal/`: smell, taste, touch, mental, and diagram lane helpers

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

## Data Surface

- `validation/datasets/mitdb/`: staged ECG dataset mirror used by Bio Wave-1 and Wave-2 ECG flows
- `validation/datasets/eeg/`, `validation/datasets/sisfall/`, `validation/datasets/wearable_device_dataset/`: local-only mirrors intentionally excluded from staged git scope

## Repo-Boundary Rule

The canonical repo root is this inner `zpe-bio/` directory only. Nothing in the outer workspace wrapper is part of the staged GitHub repo.
