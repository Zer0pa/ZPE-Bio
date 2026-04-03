# ZPE-Bio

---

## What This Is

> ZPE-Bio is a deterministic biosignal encoding system for ECG and EEG signal domains, with a Rust-backed core codec and Python package surface.

**This repo is a staged proof surface, not a public release packet.** It contains real Wave-1 and Wave-2 execution artifacts but remains in private staging. Bio Wearable is NO_GO — its closure bundles are retained for traceability, not as release proof.

### Commercial Wedge

This is for medical-device firmware teams, clinical-data infrastructure teams, and wearable-health platform engineers who need deterministic, reproducible biosignal encoding with auditable proof lineage. The business value is reproducibility and auditability for biosignal pipelines — currently demonstrated in staging, not in public release.

### Technical Wedge

The technical edge is a deterministic 8-primitive biosignal codec with both Python and Rust implementations, validated against ECG round-trip fidelity and EEG encoding paths. Wave-1 and Wave-2 readiness artifacts are committed with IMC contract-consumption alignment.

### Current Readiness

**STAGED_PROOF_SURFACE** — Private staging repository as of 2026-03-09. Not a public release packet. Not a clean green-verification snapshot.

### What Is Proved

- Runnable Python and Rust codec surfaces with maintained test suites
- Committed Wave-1 and Wave-2 readiness artifacts
- ECG validation commands with deterministic round-trip fidelity
- IMC contract-consumption artifacts for family alignment
- Source tree substance is real and testable

### What Is Not Being Claimed

- No fresh green release commit
- No public release readiness
- Bio Wearable remains NO_GO — closure bundles are traceability only
- Historical validation artifact paths not fully normalized
- Ruff and multimodal manifest verification not re-cleared in this phase

### Ideal First Buyer

Medical-device firmware team or clinical-data infrastructure team evaluating deterministic biosignal encoding with proof lineage (future — not current release).

### Deployment Model

Python package (`pip install -e ".[dev]"`), Rust crate (`core/rust/`), and embedded reference builds. Private staged — not a public packaged release.

### Authority / Proof Anchors

- `validation/results/` — committed proof and readiness artifacts
- `validation/runbooks/` — execution runbooks
- Wave-1 and Wave-2 execution artifacts
- ECG validation: `python -m zpe_bio encode-ecg --record-id 100 --samples 1000 --json`

### Role In The Zer0pa Family

ZPE-Bio validates that the ZPE encoding architecture generalizes to biosignal domains (ECG, EEG). It sits in the staged/validation tier alongside Neuro, Mocap, and Prosody, demonstrating family breadth while the primary commercial wedges (IoT, XR, Robotics, Geo) lead market entry. The platform layer is ZPE-IMC.

---

ZPE-Bio is the biosignal sector repository for Zero-Point Encoding. It packages a deterministic 8-primitive biosignal codec, a Rust-backed core codec crate, and Bio-specific validation artifacts for Wave-1 and Wave-2 execution.

This repository is a private staging surface as of 2026-03-09. It is not a public release packet and it is not a clean green-verification snapshot.

## Current Reality

- Runtime/package surface exists under `python/zpe_bio/`.
- Native codec surface exists under `core/rust/`.
- Embedded references exist under `embedded/`.
- Proof and readiness artifacts exist under `validation/results/` and `validation/runbooks/`.
- Family alignment artifacts exist under `docs/family/`.

## Current Status Snapshot

- Wave-1 repo substance is real.
- Wave-2 execution artifacts are present but mixed.
- Bio Wearable remains `NO_GO`; its closure bundles are retained for traceability, not treated as release proof.
- Historical validation artifacts preserve host-specific paths and should be read as lineage, not as current path authority.

## Fast Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m zpe_bio --help
python -m zpe_bio roundtrip --mode clinical --samples 250
```

For ECG validation commands:

```bash
python -m pip install -e ".[validation]"
python -m zpe_bio encode-ecg --record-id 100 --samples 1000 --json
```

Optional EEG support requires extra packages and local dataset acquisition:

```bash
python -m pip install -e ".[validation,bioeeg]"
```

## What This Repo Proves Today

- The source tree contains runnable Python and Rust codec surfaces.
- The source tree contains committed Wave-1 and Wave-2 readiness artifacts.
- The source tree contains IMC contract-consumption artifacts for family alignment.

## What It Does Not Prove Today

- It does not prove a fresh green release commit.
- It does not prove public-release readiness.
- It does not prove Bio Wearable closure.
- It does not prove that every historical validation artifact path has been normalized.

## Repository Map

- `python/zpe_bio/`: Python package and CLI
- `core/rust/`: Rust codec crate
- `embedded/`: embedded reference builds
- `tests/`: maintained pytest suite
- `scripts/`: operator scripts and generators
- `validation/results/`: committed proof and readiness artifacts
- `validation/runbooks/`: execution runbooks
- `docs/`: repo docs, family alignment, and regulatory material

## Audit And Boundaries

- Proof index: `PROOF_INDEX.md`
- Short audit path: `AUDITOR_PLAYBOOK.md`
- Public/operator limits: `PUBLIC_AUDIT_LIMITS.md`
- Docs landing: `docs/README.md`
- Legal boundary summary: `docs/LEGAL_BOUNDARIES.md`

## Open Contradictions

- Historical GO prose exists, but this staged repo still carries unresolved correctness work.
- `ruff` and multimodal manifest verification were not re-cleared in this phase.
- Regulatory and startup documents still contain historical absolute-path references outside the active front door.

Read this repo as a private staged baseline for Phase 4.5 and Phase 5, not as a release verdict.
