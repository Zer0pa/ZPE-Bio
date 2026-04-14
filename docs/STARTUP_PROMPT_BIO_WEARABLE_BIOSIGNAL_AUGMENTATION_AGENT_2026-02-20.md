# Startup Prompt: Folder-Local Sector Agent (Generic Maximalization Wave)

You are running inside the correct lane folder already.

## Mandatory Read Order
1. Read this startup prompt fully first.
2. Read the latest PRD in the current folder (`PRD_*`, newest date suffix).
3. Read PRD Appendix A/B/C and Appendix D `Maximalization Program (2026-02-21)` before any coding.
4. Read and extend existing runbooks in this folder before coding.

## Environment Bootstrap (Mandatory)
1. Source local environment file first: `set -a; [ -f .env ] && source .env; set +a`.
2. Verify tokenized download access only through environment variables; do not hardcode secrets in code/logs.
3. If `.env` is missing, fail fast and record blocker before implementation.

## Lane Ownership
1. Work only inside the current folder and its subfolders.
2. Keep all code, tests, runbooks, logs, and artifacts inside this folder.
3. Treat this lane as fully isolated from all other lanes.

## Forbidden Work
1. Do not edit sibling lanes, parent orchestration docs, IMC/IoT/Bio repos (unless this lane is Bio), or other projects.
2. Do not touch `/Users/zer0pa-build/ZPE Multimodality/packetgram`.
3. Do not touch `/Users/zer0pa-build/ZPE Multimodality/strokegram`.

## Engineering Mandate (Non-Negotiable)
1. Execute end-to-end as a production engineer: runbook -> implementation -> falsification -> regression -> artifact handoff.
2. Meet the PRD brief as minimum, then exceed it with measurable innovation beyond baseline acceptance gates.
3. Anti-toy rule: no demo shortcuts; prioritize deployment-grade robustness and failure transparency.
4. Resolve currently open lane gaps first (especially any `INCONCLUSIVE` core claims).

## Runbook-First Cognitive Offload (Mandatory)
Before production coding:
1. Create/extend master + gate runbooks including Maximalization gates.
2. Predeclare commands, expected outputs, fail signatures, rollback, deterministic seed policy, fallback options, and dataset/resource provenance locks.
3. Predeclare falsification route for every claim and every Appendix B resource item.

## Maximalization Execution Rules
1. Execute gates in strict PRD order, including Appendix D max-wave gates.
2. Popper-first: attempt to falsify before any claim promotion.
3. No threshold relaxation to force pass.
4. If a gate fails, patch minimally and rerun failed + downstream gates.
5. Keep implementation cohesive: no dead branches, no hidden fallback behavior.

## Artifact and Evidence Contract
1. Produce every PRD-required artifact file.
2. Must include: `concept_open_questions_resolution.md`, `concept_resource_traceability.json`, `quality_gate_scorecard.json`, `innovation_delta_report.md`, `integration_readiness_contract.json`, `residual_risk_register.md`.
3. Every claim status change must cite concrete evidence paths.
4. Mark uncertain outcomes as `UNTESTED` or `INCONCLUSIVE`.

## Completion Response Contract
Return once, at end, with:
1. Gate-by-gate PASS/FAIL (including maximalization gates).
2. Before/after metric deltas.
3. Claim status delta with evidence paths.
4. Explicit closure status for prior lane gaps and prior INCONCLUSIVE claims.
5. Quantified beyond-brief innovations and final GO/NO-GO.
