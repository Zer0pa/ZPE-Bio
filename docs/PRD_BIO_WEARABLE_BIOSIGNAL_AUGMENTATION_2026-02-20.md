# PRD: Bio Wearable-Biosignal Augmentation Wave-1

- Date: 2026-02-20
- Scope root: `<repo-root>`
- Concept anchor: `ZPE Sector Expansion Concept Docs/ZPE Wearable Health _ Biosignal — Concept Document.md`
- Priority: P0
- Reason: wearable/biosignal concept is an augmentation of existing Bio lane (not a separate new sector root)

## 1) Mission Objective (Measurable)
Augment existing Bio lane with wearable-ready modalities and validators, while preserving all current Bio wave guarantees.

Target outcomes:
1. ECG compression >= 20x with SNR >= 40 dB on benchmark set.
2. PPG compression >= 15x.
3. IMU compression >= 40x.
4. ECG morphology deviation <= 5% on QRS/PR/QTc metrics.
5. ECG-PPG alignment error < 10 ms after token alignment.
6. Token-space AF detection sensitivity >= 95% and specificity >= 90%.
7. Token-space fall detection recall >= 95% and precision >= 90%.
8. Embedded-profile runtime evidence <= 2 ms per ECG beat (proxy bench acceptable if hardware unavailable).

## 2) Baseline Evidence and Current Failure Points
Baseline anchors:
1. `validation/results/BIO_WAVE2_HANDOFF_MANIFEST.json`
2. `validation/results/bio_wave2_phase2_ecg_benchmark.json`
3. `ZPE Sector Expansion Concept Docs/ZPE Wearable Health _ Biosignal — Concept Document.md`

Current failure points:
1. Existing Bio wave does not cover full wearable set (PPG/IMU/EDA/SpO2 paths and associated tests) at required depth.
2. Existing ECG fidelity still has max PRD above strict clinical-lossless stretch target.
3. Wearable-specific artifact contract is absent.

## 3) In Scope / Out Of Scope
In scope:
1. Bio repo code/tests/runbooks/artifacts only.
2. Wearable modalities integration into Bio encode/decode + benchmark pipeline.
3. Token-space arrhythmia/fall evaluation harness with reproducible evidence.

Out of scope:
1. IMC/IoT or sector-expansion folder edits.
2. Clinical efficacy claims beyond measured codec/task metrics.

## 4) Claim Matrix (Wave-1 Augmentation)
| Claim ID | Claim | Pre-status | Required evidence |
|---|---|---|---|
| BIO-WEAR-C001 | ECG CR >= 20x and SNR >= 40 dB | UNTESTED | `bio_wear_ecg_benchmark.json` |
| BIO-WEAR-C002 | PPG CR >= 15x | UNTESTED | `bio_wear_ppg_benchmark.json` |
| BIO-WEAR-C003 | IMU CR >= 40x | UNTESTED | `bio_wear_imu_benchmark.json` |
| BIO-WEAR-C004 | ECG morphology deviation <= 5% | UNTESTED | `bio_wear_morphology_eval.json` |
| BIO-WEAR-C005 | ECG-PPG alignment < 10 ms | UNTESTED | `bio_wear_alignment_eval.json` |
| BIO-WEAR-C006 | AF sens/spec threshold met | UNTESTED | `bio_wear_af_eval.json` |
| BIO-WEAR-C007 | Fall detection precision/recall threshold met | UNTESTED | `bio_wear_fall_eval.json` |
| BIO-WEAR-C008 | Embedded-path latency evidence <= 2 ms/beat | UNTESTED | `bio_wear_embedded_latency.json` |

## 5) Falsification Plan (Popper-First)
1. DT-BIO-WEAR-1: malformed wearable packet corpus and mixed-modality contamination.
2. DT-BIO-WEAR-2: motion artifact stress on ECG/PPG alignment.
3. DT-BIO-WEAR-3: class-imbalance stress for AF/fall token-space classifiers.
4. DT-BIO-WEAR-4: deterministic replay on fixed-seed multimodal wearable set.
5. DT-BIO-WEAR-5: dependency/resource failure simulation and fallback validation.

## 6) Acceptance Criteria (Quantitative)
Mandatory:
1. BIO-WEAR-C001..C008 PASS with direct evidence.
2. 0 uncaught crashes in malformed/adversarial suite.
3. Determinism replay 5/5 hash-consistent.
4. Legacy Bio wave gates remain non-regressed.

Stretch:
1. Improve ECG max PRD toward <= 1.0 while keeping wearable additions green.

## 7) Mandatory Artifacts to Output
Output root:
- `validation/results/2026-02-20_bio_wearable_augmentation/`

Required files:
1. `handoff_manifest.json`
2. `before_after_metrics.json`
3. `falsification_results.md`
4. `claim_status_delta.md`
5. `command_log.txt`
6. `bio_wear_ecg_benchmark.json`
7. `bio_wear_ppg_benchmark.json`
8. `bio_wear_imu_benchmark.json`
9. `bio_wear_morphology_eval.json`
10. `bio_wear_alignment_eval.json`
11. `bio_wear_af_eval.json`
12. `bio_wear_fall_eval.json`
13. `bio_wear_embedded_latency.json`
14. `determinism_replay_results.json`
15. `regression_results.txt`

## 8) Execution Order With Hard Gates
1. Gate A: runbook + resource lock + baseline freeze.
2. Gate B: wearable modality encode/decode paths.
3. Gate C: fidelity/compression/alignment metrics.
4. Gate D: AF/fall eval + malformed/adversarial/determinism.
5. Gate E: full regression + packaging + claim adjudication.

## 9) Stop Conditions and Rollback Criteria
Stop on deterministic mismatch, uncaught crash, or regression in prior Bio core guarantees.
Rollback to last green checkpoint, patch minimally, rerun failed/downstream gates.

## 10) No Hand-Wavy Claims Rule
No “clinical-grade wearable ready” claim without direct metric evidence in this artifact set.

## 11) Runbook-First Cognitive Offload (Mandatory)
Before coding, create:
1. `validation/runbooks/RUNBOOK_BIO_WEARABLE_MASTER.md`
2. gate runbooks A-E
3. command ledger and risk register

## 12) Resource/Link Failure Protocol
If a target resource is unavailable:
1. capture exact failure,
2. use nearest open substitute,
3. log comparability impact,
4. keep affected claims open where equivalence is not established.


## Appendix A) Engineering Non-Negotiables (2026-02-20 Refinement)
1. End-to-end execution is mandatory: runbook-first planning, implementation, falsification campaigns, regression pack, and complete artifact handoff.
2. Meeting baseline PRD acceptance criteria is minimum only. Lane must deliver measurable augmentation beyond the baseline brief.
3. Anti-toy enforcement: demo-only outputs are non-compliant. Deliver deployment-grade robustness, stress behavior, and explicit failure transparency.
4. Problem-solving autonomy is mandatory: diagnose blockers, select nearest viable alternatives, and preserve scientific comparability.
5. Claims are evidence-bound only. No evidence path means `UNTESTED` or `INCONCLUSIVE`.

## Appendix B) Concept-Richness Coverage Checklist (Mandatory)
Resolve this checklist in runbooks before coding, and map each line to evidence artifacts:
1. PTB-XL included as primary ECG benchmark source.
2. MIMIC-IV-ECG included where access permits; fallback logged if unavailable.
3. WFDB I/O path validated for ingest/export integrity.
4. PhysioNet resource-lock and provenance captured for all downloaded records.
5. HealthyPi Move (or nearest open hardware proxy) path included for device realism checks.
6. NeuroKit2 used for morphology and signal-quality validation.
7. OpenECG benchmark conventions reflected in comparator table.
8. Biosignal Compression Toolbox or equivalent incumbent baseline included.
9. MERIT motion-artifact insights captured in artifact stress tests.

Checklist closure rule:
1. If an item cannot be executed, log failure signature, substitution chosen, and comparability impact.
2. If equivalence is unproven, keep dependent claims open as `INCONCLUSIVE`.

## Appendix C) Evaluation and Integration-Readiness Contract
Every lane run must include, in addition to core PRD artifacts:
1. `quality_gate_scorecard.json`
2. `innovation_delta_report.md` (quantified beyond-brief gains)
3. `integration_readiness_contract.json`
4. `residual_risk_register.md`
5. `concept_open_questions_resolution.md`
6. `concept_resource_traceability.json`

Scoring policy:
1. Concept-open-questions from the concept document must be resolved in `concept_open_questions_resolution.md` with evidence links.
2. Every Appendix B checklist item must be mapped in `concept_resource_traceability.json` with source and artifact pointers.
3. Apply `SECTOR_EXECUTION_QUALITY_RUBRIC_2026-02-20.md`.
4. Lane is `NO-GO` on any non-negotiable gate failure, regardless of aggregate score.
5. Lane cannot be marked complete unless beyond-brief innovations are evidenced and reproducible.

## Appendix D) Maximalization Program (2026-02-21)

### D1) Mission Upgrade
Launch and complete Bio wearable augmentation from zero execution to evidence-complete, publication-grade wearable multimodal stream validation.

### D2) Lane-Specific Hard Gaps To Close
1. Execute the entire lane (currently not started) with full artifact contract.
2. Close ECG/PPG/IMU alignment and morphology validity on real benchmark sources.
3. Close AF/fall evaluation with robust class-balance and deterministic replay.
4. Establish embedded-path latency evidence beyond proxy where feasible.

### D3) Maximalization Resource Pack (Mandatory)
1. PTB-XL and MIMIC-IV-ECG (or declared fallback with strict comparability notes).
2. WFDB and PhysioNet provenance lock pipeline.
3. NeuroKit2-based morphology validation suite.
4. Wearable motion-artifact stress battery inspired by MERIT-like conditions.

### D4) Hard Gates (Max Wave)
1. Gate M1: BIO-WEAR-C001..C008 all adjudicated with evidence.
2. Gate M2: multimodal alignment and morphology claims remain stable under artifact-heavy stress.
3. Gate M3: determinism replay 5/5 and uncaught crash rate 0% preserved.
4. Gate M4: previous Bio core guarantees remain non-regressed.

### D5) Popperian Kill Tests
1. Falsify AF/fall classifier stability under class imbalance and noise bursts.
2. Falsify cross-sensor timing under dropped or delayed segments.
3. Falsify morphology fidelity on challenging ECG morphotypes.

### D6) No-Holds-Barred Augmentation Track
1. Fused ECG/PPG/IMU/EDA latent stream with patient-specific adaptation.
2. Uncertainty-calibrated compressed-domain clinical-event inference.
3. On-device adaptive bitrate/compute profile for battery-constrained wearables.

### D7) Acceptance Upgrade For Max Wave
1. Lane cannot claim readiness until first full run produces complete handoff artifacts.
2. Proxy-only clinical comparability must be explicitly bounded and not overstated.
3. Embedded latency claims require target-profile evidence wherever executable.

## Appendix E) NET-NEW Resource Ingestion and RunPod Readiness (2026-02-21)

### E1) Evidence Inputs (Mandatory)
1. `ZPE 10-Lane NET-NEW Resource Maximization Pack.md`
2. `ZPE 10-Lane NET-NEW Resource Maximization Pack.pdf`
3. Claims stay evidence-bound; theory and synthetic-only paths cannot close clinical proxy claims.

### E2) Attempt-All Rule and Impracticality Criteria
1. Attempt all E3 resources with command-level evidence.
2. Allowed impracticality codes only: `IMP-LICENSE`, `IMP-ACCESS`, `IMP-COMPUTE`, `IMP-STORAGE`, `IMP-NOCODE`.
3. Credential-gated datasets require documented request status and fallback strategy.

### E3) Lane Resource Intake Plan (No-Skip Core)
| Resource | Required action | Claim linkage |
|---|---|---|
| NeuroKit2 | Run full preprocessing and morphology extraction pipeline | BIO-WEAR-C004, BIO-WEAR-C005 |
| WFDB Python | Use one-line PhysioNet ingestion for all benchmark datasets | BIO-WEAR-C001, BIO-WEAR-C002, BIO-WEAR-C003 |
| MIT-BIH Arrhythmia DB | Run ECG fidelity and arrhythmia proxy benchmarks | BIO-WEAR-C001, BIO-WEAR-C004, BIO-WEAR-C006 |
| Pulse Transit Time PPG | Run synchronized ECG+PPG+IMU fusion benchmarks | BIO-WEAR-C002, BIO-WEAR-C003, BIO-WEAR-C005 |
| Wearable stress+exercise dataset | Run state classification robustness benchmark | BIO-WEAR-C007 |
| MIMIC-IV ECG | Attempt scale benchmark and PRD/stability tracking | BIO-WEAR-C001, BIO-WEAR-C006 |
| Rhythm-SNN reference | Document battery-aware temporal coding alignment | BIO-WEAR-C008 |
| Synthetic biosignal generator | Use only as bootstrap fallback with explicit flag | BIO-WEAR-C002, BIO-WEAR-C003 |

### E4) RunPod Readiness Contract (GPU-Dependent Paths)
If local compute limits large-scale model or benchmark execution:
1. Produce `runpod_readiness_manifest.json` with runtime image and package lock.
2. Produce `runpod_exec_plan.md` with benchmark phases, expected runtime, and outputs.
3. Produce `runpod_dataset_stage_manifest.json` with credentialed/open dataset staging steps.
4. Complete local dry-run validation before escalation.

### E5) Additional Mandatory Artifacts (Max Wave)
Place in `validation/results/2026-02-20_bio_wearable_augmentation/`:
1. `max_resource_lock.json`
2. `max_resource_validation_log.md`
3. `max_claim_resource_map.json`
4. `impracticality_decisions.json`
5. `credential_status_log.json`
6. `clinical_proxy_limitations.md`
7. `runpod_readiness_manifest.json` (required when any `IMP-COMPUTE`)
8. `net_new_gap_closure_matrix.json`

### E6) Hard Gates (Appendix E)
1. `E-G1`: 100% of E3 resources attempted with evidence.
2. `E-G2`: No wearable claim can be PASS from synthetic-only evidence when open real datasets are available.
3. `E-G3`: Credential-gated datasets require explicit request-state tracking.
4. `E-G4`: Every skipped resource needs valid `IMP-*` records.
5. `E-G5`: RunPod readiness artifacts mandatory for compute-constrained closures.

## Appendix F) Gap-Closure Rebrief v2 (2026-02-21)

### F1) Input Anchors (Mandatory)
1. `ZPE 10-Lane Gap Closure.md`
2. Bio wearable artifact bundle at `validation/results/2026-02-20_bio_wearable_augmentation/`.

### F2) Commercialization Gate (Mandatory)
1. Prefer permissive/open clinical-proxy datasets (MIT-BIH, PTB-XL, open PhysioNet assets).
2. If required validation is human-trial/IRB/device-bound and no open substitute exists, mark claim `PAUSED_EXTERNAL`.

### F3) Atomic Closure Queue (Bio Wearable)
Mac/CPU-first:
1. Re-tune compression/fidelity pipeline to recover BIO-WEAR-C001.
2. Improve AF sensitivity path and rerun BIO-WEAR-C006.
3. Re-run fall detection with stronger open-labeled alternatives where available.

GPU transition (RunPod):
1. Use RTX 4090 for accelerated model selection/hyperparameter sweeps where CPU loop is inefficient.
2. Re-run latency/fidelity coupled experiments for BIO-WEAR-C008 closure attempts.

### F4) RTX 4090 Planning (Bio Wearable)
1. Required GPU: `Conditional` (recommended for faster remediation loops).
2. Estimated runtime on 1x4090: `2-6h`.

### F5) Gate Upgrade
1. `F-G1`: BIO-WEAR-C001/C006/C008 must move to PASS/FAIL with full evidence.
2. `F-G2`: any remaining synthetic-only clinical proxy path explicitly marked `PAUSED_EXTERNAL` or `INCONCLUSIVE` with justification.
