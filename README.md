<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Bio Masthead" width="100%">
</p>

# ZPE-Bio

48 MIT-BIH records. 1.12x mean compression. 2.85% mean PRD.
SAL v6.0. Free below $100M annual revenue. See [LICENSE](LICENSE).

---

## What This Is

Deterministic 8-primitive biosignal codec. ECG + EEG. Rust core. Python package. Embedded reference path.

Wave-1 and Wave-2 runbooks committed. ECG validation path committed. IMC contract-consumption artifacts committed.

One signal lane. Rust crate. Python package. Embedded reference path.

ECG + EEG codec in Rust and Python. Deterministic round-trip on real records.

MIT-BIH benchmark anchor: `docs/specs/ZPE_BIOSIGNAL_CODEC_PRD_v1.0.md`. Traceability anchor: `docs/regulatory/traceability/REQ_DT_MATRIX.md`.

| Proof anchor | Location |
|---|---|
| MIT-BIH benchmark anchor | `docs/specs/ZPE_BIOSIGNAL_CODEC_PRD_v1.0.md` |
| ECG validation | `python -m zpe_bio encode-ecg` |
| Family alignment | `docs/family/` |

Part of the [Zer0pa](https://github.com/Zer0pa) family. Platform layer: [ZPE-IMC](https://github.com/Zer0pa/ZPE-IMC).

---

ZPE-Bio is the biosignal sector repository for Zero-Point Encoding. It packages a deterministic 8-primitive biosignal codec, a Rust-backed core codec crate, and Bio-specific validation artifacts for Wave-1 and Wave-2 execution.

## Current Reality

- Runtime/package surface exists under `python/zpe_bio/`.
- Native codec surface exists under `core/rust/`.
- Embedded references exist under `embedded/`.
- Proof and readiness artifacts exist under `validation/benchmarks/` and `validation/runbooks/`.
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
- `validation/benchmarks/`: benchmark runners and validation entrypoints
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

Read this repo as the current biosignal proof surface and operator baseline.
