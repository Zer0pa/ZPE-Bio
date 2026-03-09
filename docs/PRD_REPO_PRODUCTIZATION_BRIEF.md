# PRD Brief: ZPE-Bio Repo Productization and Enterprise Hardening

Date: 2026-02-19  
Owner: Product/Engineering  
Execution Agent: Codex coding agent (end-to-end)

## 1) Objective

Prepare ZPE-Bio for immediate developer and open-source adoption by shipping:

1. A clean installable Python package (`pip install` flow).
2. A usable executable CLI (`zpe-bio` command).
3. CI-enforced quality gates across Python and Rust.
4. Repo hygiene suitable for public collaboration.

## 2) Scope

In scope:

1. Packaging, executable interface, CI/CD, lint/test hardening, repo hygiene.
2. Python and Rust interface safety/coherence improvements.
3. Validation harness packaging isolation and reproducibility.

Out of scope:

1. Algorithm redesign of the 8-primitive codec.
2. New clinical claims or benchmark goal changes.
3. Writing `README` and `LICENSE` (explicitly excluded; owner will add).

## 3) Current State Summary (Recon Baseline)

Strengths:

1. Core codec implementation exists in Python and Rust.
2. Existing validation framework and benchmark scripts are present.
3. Wheel build works in principle.
4. Unit tests currently pass in local environment.

Gaps blocking repo readiness:

1. No public CI workflows.
2. No executable entrypoint (`python -m zpe_bio` fails without `__main__`).
3. Lint quality debt in Python and clippy failures in Rust.
4. Import-path hacks (`sys.path.insert`, `from python.zpe_bio...`) reduce installability.
5. Generated/cache artifacts and large datasets pollute version-control boundaries.
6. Minor spec/config drift risk across runbook constants vs implementation.

## 4) Productization Principles

1. Preserve algorithm behavior unless explicitly required for stability/safety.
2. Prefer deterministic tooling and repeatable outputs.
3. Separate core library/runtime from heavy research/validation assets.
4. Enforce quality in CI before release tagging.
5. No silent threshold/gate relaxation.

## 5) Target Release Outcome

Release candidate is accepted only if all are true:

1. `pip install .` succeeds in a fresh venv and `zpe-bio --help` works.
2. `ruff check` returns zero issues.
3. `pytest -q` passes with no warnings.
4. `cargo test --release` passes.
5. `cargo clippy --release -- -D warnings` passes.
6. `python -m build` produces wheel and sdist successfully.
7. CI workflows pass on required matrix (Linux + macOS at minimum).
8. Repo is clean from generated artifacts after running default gates.

## 6) Execution Plan (Agent Backlog)

### Phase A: Repo Hygiene and Artifact Control (P0)

Tasks:

1. Add `.gitignore` to exclude caches, local envs, build outputs, targets, generated reports.
2. Add `MANIFEST.in` to constrain sdist content.
3. Ensure package build does not include tests/bench artifacts unintentionally.
4. Normalize treatment of large datasets and generated results:
   - keep only what is intentionally versioned;
   - move/ignore transient outputs.

Deliverables:

1. `.gitignore`
2. `MANIFEST.in`
3. Clean `git status` after quality gates.

Verification:

1. `git status --short`
2. `python -m build`
3. Inspect wheel content (`unzip -l dist/*.whl`)

---

### Phase B: Packaging and Install UX (P0)

Tasks:

1. Refactor imports to package-native style (`from zpe_bio...`) and remove path hacks.
2. Move tests to dedicated test folder if required for clean package boundary.
3. Update `pyproject.toml` metadata for public package quality.
4. Add CLI entrypoint in `[project.scripts]`.
5. Add `python/zpe_bio/__main__.py`.

Deliverables:

1. Updated `pyproject.toml`
2. `python/zpe_bio/cli.py` (or equivalent)
3. `python/zpe_bio/__main__.py`

Verification:

1. Fresh venv install test.
2. `zpe-bio --help` returns usage.
3. Basic encode/decode CLI smoke run succeeds.

---

### Phase C: Python Quality Hardening (P0)

Tasks:

1. Resolve all `ruff` violations in package + scripts designated as maintained.
2. Eliminate pytest warnings and anti-patterns (e.g., test returns bool).
3. Enforce strict minimal lint baseline in CI.

Deliverables:

1. Clean lint output.
2. Stable test suite without warnings.

Verification:

1. `ruff check python scripts validation`
2. `pytest -q`

---

### Phase D: Rust Core Hardening (P1)

Tasks:

1. Fix clippy-denied issues (error typing, needless loops, FFI pointer safety).
2. Harden FFI contracts:
   - null pointer checks,
   - explicit unsafe boundaries,
   - deterministic error codes.
3. Maintain Python/Rust parity behavior.

Deliverables:

1. Clippy-clean Rust core.
2. Safe FFI contract comments/docs.

Verification:

1. `cargo fmt --check`
2. `cargo test --release`
3. `cargo clippy --release -- -D warnings`
4. parity test pass

---

### Phase E: CI/CD and Release Gates (P0)

Tasks:

1. Add GitHub workflows for Python and Rust.
2. Configure matrix builds (Python versions + OS matrix).
3. Include build artifact jobs for wheel/sdist.
4. Add required checks policy recommendations.

Deliverables:

1. `.github/workflows/ci-python.yml`
2. `.github/workflows/ci-rust.yml`
3. Optional release workflow skeleton.

Verification:

1. CI runs green in PR context.
2. Local parity with CI commands.

---

### Phase F: Cohesion and Traceability (P1)

Tasks:

1. Reconcile constants/spec drift between code and governing docs.
2. Add a compact `docs/RELEASE_CHECKLIST.md` covering developer release path.
3. Add `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md` templates (README/LICENSE excluded).

Deliverables:

1. Updated docs for collaboration and governance.

Verification:

1. Manual review for consistency.
2. Confirm no unresolved TODO in release checklist.

## 7) Prioritization and Sequence

Must execute in order:

1. Phase A
2. Phase B
3. Phase C
4. Phase D
5. Phase E
6. Phase F

Reason: packaging and hygiene first prevents rework and CI churn.

## 8) Acceptance Criteria (Final Sign-off)

All must pass:

1. Install + executable UX.
2. Python lint/test clean.
3. Rust fmt/test/clippy clean.
4. CI workflows exist and pass.
5. Repo free of obvious generated artifact churn.
6. No README/LICENSE authored by agent.

## 9) Risks and Mitigations

1. Risk: breaking parity while hardening FFI.
   Mitigation: lock parity tests as non-negotiable gate.

2. Risk: removing tracked assets required by validation flows.
   Mitigation: keep deterministic fetch scripts/checksums before untracking.

3. Risk: over-tight lint rules causing slow progress.
   Mitigation: strict core gates + scoped exemptions only when justified.

## 10) Final Report Contract (Agent Output)

At completion, agent must provide one final report only:

1. What changed (file-level summary).
2. Commands run and exact pass/fail results.
3. Remaining risks or intentional deferrals.
4. Clear statement whether release candidate is ready.

No intermediate approval checkpoints required unless blocked by missing credentials or external access limits.

