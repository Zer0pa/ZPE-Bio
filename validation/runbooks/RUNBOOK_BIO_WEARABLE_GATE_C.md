# RUNBOOK: BIO WEARABLE GATE C (Quantitative Metrics)

## Commands
1. Compute CR/SNR for ECG and CR for PPG/IMU.
2. Compute morphology deviation (QRS/PR/QTc) via NeuroKit2 workflow.
3. Compute ECG-PPG token alignment error under nominal + stress scenarios.
4. Compute embedded-profile proxy latency per beat.
5. Apply scoring rubric draft entries for dimensions 1/4/8/10 using gate evidence.

## Expected Artifacts
1. `before_after_metrics.json`
2. `bio_wear_morphology_eval.json`
3. `bio_wear_alignment_eval.json`
4. `bio_wear_embedded_latency.json`
5. `quality_gate_scorecard.json` (partial C-claim fields)
6. `clinical_proxy_limitations.md` (draft bounds from proxy measurements)

## Fail Signatures
1. Metrics missing required thresholds or key fields.
2. Morphology extractor failure on all attempted records.
3. Alignment metrics unavailable without impracticality justification.
4. Claimed PASS without threshold check evidence for C001..C005/C008.

## Rollback
1. Patch metric evaluators and rerun Gate C end-to-end.
