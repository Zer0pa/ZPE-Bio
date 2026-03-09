# PRD Brief: ZPE-Bio Multimodal Augmentation (Smell + Taste)

## Objective
- Augment `zpe-bio` with transplant-safe smell and taste codec capabilities from the ZPE multimodality research stack.
- Keep all required implementation assets inside this repository (no symlinks, no runtime dependency on external folders).
- Preserve deterministic behavior and package usability via `pip install` + `zpe-bio` CLI.

## Scope Implemented
- Added new package namespace: `python/zpe_bio/multimodal/`.
- Transplanted smell modules:
  - `python/zpe_bio/multimodal/smell/*`
  - Includes phase-5 augmentation hooks (`molecular_bridge`, adaptation, z-episode pack/unpack).
- Transplanted taste modules:
  - `python/zpe_bio/multimodal/taste/*`
  - Rewired import dependencies from `artifacts.packetgram.*` to local `zpe_bio.multimodal.{core,diagram}`.
- Added minimal shared substrate:
  - `python/zpe_bio/multimodal/core/constants.py`
  - `python/zpe_bio/multimodal/diagram/quantize.py`
- Added multimodal CLI smoke command:
  - `zpe-bio multimodal [--json]`
- Version uplift:
  - `pyproject.toml` + `python/zpe_bio/__init__.py` set to `0.2.0`.

## Provenance (Copied Sources)
- Smell/core/diagram source lineage:
  - `/Users/prinivenpillay/ZPE Multimodality/ZPE-IMC/source/...`
- Taste source lineage:
  - `/Users/prinivenpillay/ZPE Multimodality/taste/source/...`

## Validation Added
- New tests:
  - `tests/test_multimodal_smell.py`
  - `tests/test_multimodal_taste.py`
  - `tests/test_multimodal_fusion.py`
  - `tests/test_multimodal_cli.py`
- Gate outcomes:
  - `pytest -q` passed (`15 passed`).
  - Editable install + executable check passed in isolated virtualenv:
    - `zpe-bio version` -> `0.2.0`
    - `zpe-bio multimodal --json` returns successful roundtrip metrics.
  - Added multimodal benchmark harness:
    - `scripts/benchmark_multimodal.py`
  - Added checksum provenance tooling:
    - `scripts/generate_multimodal_manifest.py`
    - `scripts/verify_multimodal_manifest.py`
    - `docs/multimodal/MULTIMODAL_TRANSPLANT_MANIFEST.sha256`

## Enterprise Hardening Notes
- Self-contained module copies eliminate fragile external path coupling.
- Deterministic pack/unpack assertions included for both smell and taste.
- Fusion scheduler extraction sanity validated for taste + smell + touch packet framing.
- Taste capability remains governance-sensitive in upstream dossier; keep canonical claim status conservative until domain validation closes.

## Release Readiness Checklist (Next)
- Maintain CI jobs for:
  - `pytest -q`
  - `ruff check`
  - manifest verification (`python scripts/verify_multimodal_manifest.py`)
  - packaging smoke (`zpe-bio multimodal --json`)
  - multimodal benchmark thresholds (`python scripts/benchmark_multimodal.py ...`)
- Add benchmark targets for multimodal encode/decode latency and memory.
- Add signed artifact manifest for transplanted module checksums.
