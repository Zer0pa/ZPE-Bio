# Validation Results

This directory was empty until the Python-only benchmark path was executed against
the bundled MIT-BIH dataset at `validation/datasets/mitdb/`.

## Hardware Boundary

Embedded and hardware validation still belongs to `embedded/nrf5340/` and the
runbooks under `validation/runbooks/`. Those workflows require device access.

## CPU-Only Benchmarks

The Python codec benchmarks in this repo run on any machine with the validation
dependencies installed. The committed result sets under this directory come from
that CPU-only path, not from the nRF5340 hardware lane.

## Contents

- `mitdb_python_only/`: per-record MIT-BIH benchmark payloads plus aggregate JSON/CSV
- `BENCHMARK_SUMMARY.md`: human-readable MIT-BIH summary report
- Additional dataset subdirectories: PhysioNet benchmark outputs committed by action-item execution
