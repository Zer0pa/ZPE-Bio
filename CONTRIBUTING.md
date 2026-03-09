# Contributing

## Development Setup

1. Create a virtual environment and activate it.
2. Install dependencies:
   `python -m pip install -e ".[dev,validation]"`
3. Run local gates before opening a PR:
   - `ruff check python scripts validation`
   - `pytest -q`
   - `cd core/rust && cargo fmt --check && cargo test --release && cargo clippy --release -- -D warnings`

## Pull Request Rules

1. Keep changes scoped and evidence-backed.
2. Do not commit generated artifacts (`dist/`, `target/`, caches, or benchmark outputs).
3. Preserve Python/Rust parity behavior.
4. Update docs when user-facing behavior or release gates change.

## Commit Quality

1. Prefer small, reviewable commits.
2. Include tests with behavior changes.
3. Keep CI green on Linux and macOS.
