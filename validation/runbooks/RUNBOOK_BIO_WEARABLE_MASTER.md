# RUNBOOK: BIO WEARABLE AUGMENTATION MASTER

## Scope
- Repo root: `<repo-root>`
- PRD: `docs/PRD_BIO_WEARABLE_BIOSIGNAL_AUGMENTATION_2026-02-20.md`
- Startup prompt: `docs/STARTUP_PROMPT_BIO_WEARABLE_BIOSIGNAL_AUGMENTATION_AGENT_2026-02-20.md`

## Artifact Root
- `validation/results/2026-02-20_bio_wearable_augmentation/`

## Deterministic Policy
1. Global seed: `20260220`
2. All synthetic fallback generators must accept and persist this seed.
3. Determinism gate requires `5/5` hash-consistent replay.

## Baseline/Comparator Locks
1. Baseline manifest lock:
   - `validation/results/BIO_WAVE2_HANDOFF_MANIFEST.json`
   - `validation/results/bio_wave2_phase2_ecg_benchmark.json`
2. Comparator integrity lock:
   - Incumbent: gzip/lzma stream compression baselines
   - Modern: PTB-XL/OpenECG conventions where resource access allows

## Gate Order (Strict)
1. Gate A: baseline freeze + environment + resource lock
2. Gate B: wearable modality pipeline build (ECG/PPG/IMU/EDA proxy lanes)
3. Gate C: quantitative metrics (compression/fidelity/morphology/alignment/latency)
4. Gate D: AF/fall + adversarial + determinism campaigns
5. Gate E: full regression, packaging, adjudication, handoff
6. Gate F (2026-02-21 closure): triage FAIL/INCONCLUSIVE claims and produce commercialization-safe closure bundle.

## Maximalization Hard Gates
1. `M1`: BIO-WEAR-C001..C008 all adjudicated with evidence.
2. `M2`: morphology/alignment claims rechecked under motion-artifact stress.
3. `M3`: determinism replay `5/5` and uncaught crash rate `0%`.
4. `M4`: prior Bio wave guarantees remain non-regressed.

## Appendix E Hard Gates
1. `E-G1`: 100% of E3 resources attempted with command-level evidence.
2. `E-G2`: no PASS claim closed from synthetic-only evidence when open real datasets were available.
3. `E-G3`: credential-gated datasets include explicit request/access-state tracking.
4. `E-G4`: every skipped resource has valid `IMP-*` record.
5. `E-G5`: if any `IMP-COMPUTE`, emit full RunPod readiness artifact set.

## Mandatory Artifact Set (Execution + Appendices)
1. Core PRD artifacts (handoff, metrics, falsification, claim delta, command log, C001..C008 evidence, determinism, regression).
2. Appendix C artifacts (`quality_gate_scorecard.json`, `innovation_delta_report.md`, `integration_readiness_contract.json`, `residual_risk_register.md`, `concept_open_questions_resolution.md`, `concept_resource_traceability.json`).
3. Appendix E artifacts (`max_resource_lock.json`, `max_resource_validation_log.md`, `max_claim_resource_map.json`, `impracticality_decisions.json`, `credential_status_log.json`, `clinical_proxy_limitations.md`, `net_new_gap_closure_matrix.json`, and RunPod artifacts only when needed).

## Falsification Route (Claim-wise)
1. BIO-WEAR-C001: falsify ECG CR/SNR via noisy/morphology-diverse records.
2. BIO-WEAR-C002: falsify PPG CR under motion artifacts and baseline drift.
3. BIO-WEAR-C003: falsify IMU CR under high-frequency movement bursts.
4. BIO-WEAR-C004: falsify morphology stability on QRS/PR/QTc on difficult leads.
5. BIO-WEAR-C005: falsify ECG-PPG alignment under dropped/delayed segment simulation.
6. BIO-WEAR-C006: falsify AF classifier under class imbalance and burst-noise.
7. BIO-WEAR-C007: falsify fall classifier under heavy non-fall perturbations.
8. BIO-WEAR-C008: falsify latency claim on repeated beat-level benchmark runs.

## Appendix B/E Resource Attempt Rule
1. Attempt every listed resource with command-level evidence.
2. Allowed impracticality codes only:
   - `IMP-LICENSE`, `IMP-ACCESS`, `IMP-COMPUTE`, `IMP-STORAGE`, `IMP-NOCODE`
3. Every impracticality decision must include:
   - attempted command
   - error signature
   - fallback
   - comparability/claim impact

## Rollback Policy
1. Patch minimally and rerun failed gate + all downstream gates.
2. Stop on uncaught crash, determinism break, or prior-wave regression.
3. No threshold relaxation to force PASS.

## Gate F Claim Closure Queue (2026-02-21)
1. `BIO-WEAR-C001`:
   - Root-cause path: codec CR/SNR frontier audit on PTB-XL + MIT-BIH.
   - Closure actions: run transform/predictive codec experiments; if no operating point satisfies CR>=20x and SNR>=40dB, mark `PAUSED_EXTERNAL` with evidence.
2. `BIO-WEAR-C006`:
   - Root-cause path: AF sensitivity under class imbalance.
   - Closure actions: feature redesign + threshold search on AFDB/MIT-BIH holdout; require sens>=0.95 and spec>=0.90.
3. `BIO-WEAR-C007`:
   - Root-cause path: fall labels synthetic-only.
   - Closure actions: attempt open real fall-labeled wearable datasets; if unavailable/commercially unsafe, mark `PAUSED_EXTERNAL`.
4. `BIO-WEAR-C008`:
   - Root-cause path: host-path latency >2 ms/beat.
   - Closure actions: profile Python path and Rust/native path; if local hardware path remains infeasible, produce RunPod/target-device readiness artifacts with concrete command plan.

## Gate F Mandatory Artifacts
1. `execution_log.md` (claim-by-claim root cause + actions + outcomes).
2. `commercialization_risk_register.md`.
3. `runpod_readiness_manifest.json`.
4. refreshed `quality_gate_scorecard.json`, `claim_status_delta.md`, `residual_risk_register.md`.
