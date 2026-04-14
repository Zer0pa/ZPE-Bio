# DOC-010: Configuration Management Plan

**Document ID:** DOC-010  
**Version:** 1.0  
**Date:** 2026-02-12  
**Classification:** IEC 62304 §8

## 1. Repository Baseline

- Root: `/Users/zer0pa-build/ZPE Bio/zpe-bio`
- Governing docs: PRD + RUNBOOK series in project root
- Evidence artifacts: `/Users/zer0pa-build/ZPE Bio/zpe-bio/validation/results`

## 2. Controlled Items

| Item Type | Location | Control |
|:---|:---|:---|
| Source code | `core/`, `python/`, `embedded/` | Git tracked |
| Tests and DT scripts | `validation/destruct_tests/` | Git tracked |
| Regulatory docs | `docs/regulatory/` | Git tracked |
| Results artifacts | `validation/results/` | Timestamped immutable files |

## 3. Change Control

- Requirement-impacting gate changes require PRD amendment and explicit rationale.
- Runbook phase statuses must be updated only after evidence-backed gate completion.
- DT changes require justification and re-execution evidence.

## 4. Build Reproducibility

- Python execution uses repo-local `.venv`.
- Rust target builds specify explicit target triples.
- Phase 3 consolidated execution is reproducible via:
  - `python validation/benchmarks/phase3_hostok_report.py`

## 5. Release Candidate Criteria

- All non-external gates pass.
- Regulatory docs DOC-001..DOC-012 exist.
- External blocker log is explicit for unresolved clinical/human tasks.
