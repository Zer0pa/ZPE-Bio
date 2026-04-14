Use this prompt with the same coding agent:

---
You are executing an add-on integration brief in `<repo-root>`.

Primary brief:
- `docs/PRD_ZPE_BIO_TOUCH_MENTAL_ADDON_BRIEF.md`

Context:
- Smell+taste are already integrated in `python/zpe_bio/multimodal`.
- CI, benchmark harness, and checksum manifest scaffolding already exist.

Task:
1. Implement the add-on brief end-to-end without pausing for approvals.
2. Transplant touch+mental modules from:
   - `ZPE-IMC/source/touch`
   - `ZPE-IMC/source/mental`
3. Keep everything self-contained in this repository (no symlinks, no runtime external imports).
4. Update multimodal CLI smoke path, benchmarks, tests, CI, and manifest as defined in the brief.
5. Run full local validation and fix failures.

Required final report format:
- Section 1: What changed (files and rationale)
- Section 2: Validation command results
- Section 3: Remaining risks (severity-ordered)
- Section 4: Exact next actions (numbered, minimal)

Do not return intermediate updates. Return only once all tasks are complete.
---
