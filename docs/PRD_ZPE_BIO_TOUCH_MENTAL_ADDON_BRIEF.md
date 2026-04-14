# PRD Add-On Brief: Touch + Mental Integration

## Why This Add-On Exists
- `touch` and `mental` were not included in the first augmentation pass to keep blast radius constrained while landing smell/taste, packaging, CI, and manifest scaffolding safely.
- Dossier lane status supports adding both now:
  - `mental`: defended, HOP-C022/C023 reinforced, fuzz pass reported.
  - `touch`: defended, HOP-C024 pass, malformed crash rate 0.0 reported.

## Objective
- Extend `zpe-bio` multimodal stack from smell+taste to smell+taste+touch+mental with self-contained source copies and production gates.
- Preserve deterministic transport, type-bit exclusivity, and packaging usability.

## Scope
- In scope:
  - transplant `touch` and `mental` modules from `/Users/zer0pa-build/ZPE Multimodality/ZPE-IMC/source`.
  - integrate APIs under `python/zpe_bio/multimodal`.
  - add regression tests, fuzz safety checks, benchmarks, CI gates, and checksum manifest updates.
- Out of scope:
  - changing claim-state language for taste.
  - refactoring biosignal codec core logic.
  - external folder runtime dependencies.

## Source of Truth
- Touch source:
  - `/Users/zer0pa-build/ZPE Multimodality/ZPE-IMC/source/touch`
- Mental source:
  - `/Users/zer0pa-build/ZPE Multimodality/ZPE-IMC/source/mental`

## Execution Plan
### 1. Transplant and Wire Modules
- Copy into:
  - `python/zpe_bio/multimodal/touch/*`
  - `python/zpe_bio/multimodal/mental/*`
- Ensure no import paths reference external tree.
- Keep code ASCII and deterministic behavior unchanged from source.

### 2. Public API Integration
- Export both packages from:
  - `python/zpe_bio/multimodal/__init__.py`
- Keep backwards compatibility for smell/taste imports.

### 3. CLI Expansion
- Extend `zpe-bio multimodal` to include:
  - touch encode/decode smoke (header/step integrity).
  - mental encode/decode smoke (RLE/raw compatibility and profile handling).

### 4. Test Matrix
- Add tests:
  - `tests/test_multimodal_touch.py`
  - `tests/test_multimodal_mental.py`
  - extend `tests/test_multimodal_fusion.py` for trimodal taste+smell+touch and safety tails.
- Minimum checks:
  - deterministic pack results.
  - type bit correctness and no high-bit collisions.
  - roundtrip integrity for core structures.
  - malformed/dirty stream resilience (no uncaught crash on malformed ints).

### 5. Performance and Memory Gates
- Extend `scripts/benchmark_multimodal.py` with touch and mental workloads.
- Add threshold flags:
  - `--max-touch-ms`
  - `--max-mental-ms`
- Keep same reporting shape and CI fail-on-threshold behavior.

### 6. Provenance and Manifest
- Regenerate checksum manifest with newly added files:
  - `docs/multimodal/MULTIMODAL_TRANSPLANT_MANIFEST.sha256`
- Ensure `scripts/verify_multimodal_manifest.py` passes.

### 7. CI and Release Gates
- Update `.github/workflows/ci-python.yml` to validate:
  - manifest verification
  - pytest
  - benchmark thresholds including touch/mental
  - CLI multimodal smoke

## Acceptance Criteria
- `pytest -q` passes with new modality tests.
- `python scripts/verify_multimodal_manifest.py` passes.
- `python scripts/benchmark_multimodal.py ...` passes with touch/mental thresholds.
- `PYTHONPATH=python python -m zpe_bio multimodal --json` reports successful touch/mental checks.
- No external imports from `/Users/zer0pa-build/ZPE Multimodality/...` remain in runtime modules.

## Risk Controls
- Parser hardening:
  - reject incomplete tail packets (do not emit partial packets).
  - non-int and malformed-int campaigns should not raise uncaught exceptions.
- Keep claim wording conservative where canonical science validation is pending (taste remains placeholder-governed).
