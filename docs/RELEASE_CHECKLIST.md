# ZPE-Bio Release Checklist

Date: 2026-02-19
Scope: Python package UX, Rust core quality, CI gate parity, and repo hygiene.

## Mandatory Local Gates

| Gate | Command | Expected Result |
| --- | --- | --- |
| Python lint | `ruff check python scripts validation` | `All checks passed!` |
| Python tests | `pytest -q` | all tests pass, no warnings |
| Rust format | `cargo fmt --check` (in `core/rust`) | no diff |
| Rust tests | `cargo test --release` (in `core/rust`) | pass |
| Rust clippy | `cargo clippy --release -- -D warnings` (in `core/rust`) | pass |
| Package build | `python -m build` | wheel + sdist created |
| Install UX | fresh venv `pip install .` then `zpe-bio --help` | CLI help displays |
| CLI smoke | `zpe-bio roundtrip --mode clinical --samples 250` | compression/fidelity output |

## Mandatory CI Gates

| Workflow | Required Matrix |
| --- | --- |
| `ci-python.yml` | Linux + macOS, Python 3.10/3.11 |
| `ci-rust.yml` | Linux + macOS |

Branch protection recommendations are defined in `docs/CI_REQUIRED_CHECKS.md`.

## Packaging Boundary Checks

1. `MANIFEST.in` excludes validation/bench artifacts from sdist.
2. `.gitignore` excludes generated caches, build targets, and run outputs.
3. `unzip -l dist/*.whl` includes only runtime package files for `zpe_bio`.
