<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Bio Masthead" width="100%">
</p>

# ZPE-Bio

---

## What This Is

ZPE-Bio applies the ZPE deterministic 8-primitive encoding architecture to biosignal domains — ECG and EEG. The codec ships in both **Rust** (`core/rust/`) and **Python** (`python/zpe_bio/`), with embedded reference builds under `embedded/`.

Wave-1 and Wave-2 readiness artifacts are committed under `validation/results/` and `validation/runbooks/`. ECG validation runs deterministic round-trip fidelity checks against real records: `python -m zpe_bio encode-ecg --record-id 100 --samples 1000 --json`. IMC contract-consumption artifacts confirm family alignment. **Bio Wearable is NO_GO** — its closure bundles are retained for traceability, not treated as release proof.

For medical-device firmware teams and clinical-data infrastructure engineers evaluating deterministic biosignal encoding: this is the only lane in the family with both a Rust crate and Python package targeting the same signal domain, plus an embedded reference path. The proof lineage is auditable but the release surface is not green.

**Readiness: private-stage (2026-03-09).** Not a public release packet. Not a clean green-verification snapshot. Historical validation artifacts preserve host-specific paths (lineage, not path authority).

**Not claimed:** fresh green release commit, public release readiness, Bio Wearable viability, fully normalized artifact paths.

| Proof anchor | Location |
|---|---|
| Wave-1 / Wave-2 artifacts | `validation/results/`, `validation/runbooks/` |
| ECG validation | `python -m zpe_bio encode-ecg` |
| Family alignment | `docs/family/` |

Part of the [Zer0pa](https://github.com/zer0-point-energy) family. Platform layer: [ZPE-IMC](https://github.com/zer0-point-energy/ZPE-IMC).

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
