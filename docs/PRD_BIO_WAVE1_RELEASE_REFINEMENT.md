# PRD: Bio Wave-1 Coordinated Release Refinement

Date: 2026-02-20
Owner: Product/Engineering
Repo: `/Users/prinivenpillay/ZPE Bio/zpe-bio`
Scope: code + release engineering only
Priority: P0

## 1. Mission

Ship Bio as an independently releasable biomedical artefact aligned with IMC compatibility constraints, without coupling Bio release operations to IMC runtime code.

## 2. Position in the Release Family

Bio is sector-focused and must remain independently operable. Where multimodal transport semantics overlap with IMC, Bio must consume IMC compatibility outputs as reference artifacts only.

Upstream dependency (artifact-level only):
1. `IMC_INTERFACE_CONTRACT.md`
2. `IMC_COMPATIBILITY_VECTOR.json`
3. `IMC_RELEASE_NOTE_FOR_BIO_IOT.md`

## 3. Current Baseline

Observed baseline:
1. Package: `zpe-bio==0.2.0`
2. CLI commands available: `roundtrip`, `version`, `multimodal`
3. Local python tests: `22 PASS`
4. Rust release tests: `PASS`
5. CI workflows exist (`ci-python.yml`, `ci-rust.yml`, `release-skeleton.yml`)
6. Repo has active uncommitted changes and mixed release artifacts.

## 4. Target State

Bio release candidate is acceptable only if all are true:
1. Core and multimodal behavior are deterministic and contract-tested.
2. Python/Rust parity is mandatory in CI matrix.
3. Wire-format compatibility tests are pinned and passing.
4. Single canonical release artifact set for target version.
5. IMC-aligned compatibility note is produced for release wave.

## 5. Non-Goals

1. No migration into IMC repo.
2. No cross-repo build orchestration in the same pipeline.
3. No clinical/regulatory claim expansion in this coding cycle.

## 6. Cross-Repo Coordination Contract (Bio Outputs)

Generate:
1. `docs/family/BIO_IMC_ALIGNMENT_REPORT.md`
2. `docs/family/BIO_COMPATIBILITY_VECTOR.json`
3. `docs/family/BIO_RELEASE_NOTE_FOR_COORDINATION.md`

`BIO_COMPATIBILITY_VECTOR.json` minimum schema:
1. `bio_package_version`
2. `imc_contract_version_consumed`
3. `shared_marker_assumptions`
4. `packet_compatibility_guarantees`
5. `known_divergences`
6. `breaking_change_policy`

## 7. Execution Protocol (Runbook-First)

Before edits:
1. `validation/runbooks/RUNBOOK_BIO_WAVE1_MASTER.md`
2. `validation/runbooks/RUNBOOK_BIO_WAVE1_PHASE_<N>.md`

For each phase:
1. execute,
2. capture logs,
3. gate,
4. patch,
5. rerun phase gates,
6. advance only on green.

## 8. Phase Plan

### Phase 0: Baseline Freeze
Tasks:
1. Capture package metadata, CLI surface, and test inventory.
2. Re-run local quality commands (python + rust).
3. Snapshot existing workflow files.

Outputs:
1. `validation/results/bio_wave1_phase0_inventory.txt`
2. `validation/results/bio_wave1_phase0_baseline.txt`

Gate:
1. Baseline passes.

### Phase 1: Repo Hygiene and Version Canonicalization
Tasks:
1. Remove stale/redundant built artifacts from tracked release path.
2. Normalize single target version outputs.
3. Ensure package metadata consistency across files.

Outputs:
1. `validation/results/bio_wave1_phase1_hygiene.txt`
2. `validation/results/bio_wave1_phase1_version_consistency.txt`

Gate:
1. No mixed-version release confusion.

### Phase 2: Runtime Surface Hardening
Tasks:
1. Stabilize CLI JSON contract and add strict tests.
2. Separate core vs multimodal dependency lanes (extras + guarded imports).
3. Add explicit unsupported-version error behavior for packet decode.

Outputs:
1. `validation/results/bio_wave1_phase2_cli_contract.txt`
2. `validation/results/bio_wave1_phase2_dependency_lanes.txt`

Gate:
1. Fresh install and command smoke pass.

### Phase 3: Parity and Compatibility Reinforcement
Tasks:
1. Make Python/Rust parity required across CI matrix.
2. Add golden packet fixtures for wire compatibility.
3. Add deterministic replay test for seeded runs.

Outputs:
1. `validation/results/bio_wave1_phase3_parity.txt`
2. `validation/results/bio_wave1_phase3_golden_packets.txt`

Gate:
1. Parity and golden fixtures green.

### Phase 4: CI + Release Workflow Finalization
Tasks:
1. Ensure CI workflows enforce required checks.
2. Upgrade release workflow to full publish-ready pipeline with integrity artifacts.
3. Emit required-checks set for branch protection.

Outputs:
1. `validation/results/bio_wave1_phase4_ci.txt`
2. `validation/results/bio_wave1_phase4_release_pipeline.txt`

Gate:
1. Workflow dry-run and lint green.

### Phase 5: IMC Alignment Publication
Tasks:
1. Read IMC contract artifacts.
2. Map Bio shared assumptions + divergences.
3. Publish Bio alignment files in `docs/family`.

Outputs:
1. `docs/family/BIO_IMC_ALIGNMENT_REPORT.md`
2. `docs/family/BIO_COMPATIBILITY_VECTOR.json`
3. `docs/family/BIO_RELEASE_NOTE_FOR_COORDINATION.md`
4. `validation/results/bio_wave1_phase5_alignment.txt`

Gate:
1. Alignment report complete and machine-readable vector valid.

### Phase 6: RC Rehearsal and Handover
Tasks:
1. Execute full release preflight commands from clean env.
2. Produce final readiness + issue register.

Outputs:
1. `validation/results/BIO_WAVE1_RELEASE_READINESS_REPORT.md`
2. `validation/results/bio_wave1_phase6_rc_rehearsal.txt`

Gate:
1. All P0 gates pass.

## 9. Acceptance Criteria

Release-ready if all are true:
1. Phase gates pass.
2. Core/multimodal lanes are explicit and tested.
3. Parity and golden compatibility checks pass.
4. IMC alignment artifacts are published.

## 10. Risks

1. Drift between Python and Rust behavior.
2. Hidden dependence on stale build artifacts.
3. Compatibility assumptions diverging from IMC wave freeze.

Mitigation:
1. Required parity gate.
2. Canonical version output checks.
3. Mandatory Phase 5 alignment checkpoint.
