# Reorientation Fix Log — 2026-04-17

## Review Scope

- Reviewed the root README and changelog.
- Reviewed the repo-surface docs under `docs/`, including architecture, legal, product-surface metadata, family/co-ordination notes, the historical PRD, and the regulatory blocker/pathway records.
- Left formal regulatory blocker records intact where they remain current and honest.

## Drift

- [`README.md`](../../../README.md) (lines 7-57) — replaced stale private-stage / release-not-green phrasing, removed the unsupported gzip headline section, and reset the top-line authority surface to ECG-backed retained artifacts.
- [`docs/specs/ZPE_BIOSIGNAL_CODEC_PRD_v1.0.md`](../../specs/ZPE_BIOSIGNAL_CODEC_PRD_v1.0.md) (lines 1-68) — retired the stale confidential / poison-pill header and replaced the old benchmark snapshot with the current public authority table.
- [`CHANGELOG.md`](../../../CHANGELOG.md) (lines 3-20) — corrected the stale "dual license" note to `LicenseRef-Zer0pa-SAL-6.2`.

## Clarity

- [`docs/ARCHITECTURE.md`](../../ARCHITECTURE.md) (lines 7-29) — marked ECG as the governing public authority and demoted EEG / multimodal helpers to auxiliary surfaces.
- [`docs/market_surface.json`](../../market_surface.json) (lines 4-22) — rewrote buyer, status, and deployment copy to say exactly what the product proves now.

## Consistency

- [`README.md`](../../../README.md) (lines 24-55) and [`docs/specs/ZPE_BIOSIGNAL_CODEC_PRD_v1.0.md`](../../specs/ZPE_BIOSIGNAL_CODEC_PRD_v1.0.md) (lines 60-68) — aligned the visible authority set to MIT-BIH, PTB-XL, EDB, and NSTDB.
- [`README.md`](../../../README.md) (lines 13, 35-38) and [`docs/family/BIO_IMC_ALIGNMENT_REPORT.md`](../../family/BIO_IMC_ALIGNMENT_REPORT.md) (lines 27-33) — aligned IMC references to artifact-level coordination instead of platform-style dependency language.

## Framing

- [`README.md`](../../../README.md) (lines 7-13, 91-93) — rewrote the front door so ZPE-Bio speaks as an independent biosignal product rather than a staged lane inside a shared platform.
- [`docs/family/BIO_RELEASE_NOTE_FOR_COORDINATION.md`](../../family/BIO_RELEASE_NOTE_FOR_COORDINATION.md) (lines 1-29) — renamed and reframed the note around cross-repo coordination.

## Beta posture

- [`README.md`](../../../README.md) (lines 11, 51-57, 91-93) — replaced negative staging language with the "always in beta" posture while keeping the authority boundary explicit.
- [`docs/market_surface.json`](../../market_surface.json) (lines 4-9) — changed status / deployment wording from private staged to active beta.

## Primitive scope

- [`README.md`](../../../README.md) (lines 7-9) and [`docs/ARCHITECTURE.md`](../../ARCHITECTURE.md) (lines 7-10, 29) — narrowed the authoritative surface to ECG while keeping the 8-primitive claim tied to the actual codec implementation.
- [`docs/specs/ZPE_BIOSIGNAL_CODEC_PRD_v1.0.md`](../../specs/ZPE_BIOSIGNAL_CODEC_PRD_v1.0.md) (lines 16-21, 27-48) — preserved the 8-primitive mechanic as a lane-specific codec description instead of a portfolio-wide narrative.

## Honest limits

- [`README.md`](../../../README.md) (lines 40-45, 153-158) — surfaced EEG non-authority, Bio Wearable `NO_GO`, and NaN-input limits plainly.
- Reviewed [`docs/regulatory/BLOCKERS.md`](../../regulatory/BLOCKERS.md) (lines 5-28) and [`docs/regulatory/PATHWAY_DECISION.md`](../../regulatory/PATHWAY_DECISION.md) (lines 3-21) — kept `SUSPENDED_BY_OWNER` entries because they are current blocker records, not stale defensive framing.
