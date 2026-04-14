# Legal Boundaries

This note is a repo-surface summary only. The root license file is the legal source of truth.

## License Surface

- Repository license: `../LICENSE` (Zer0pa Source-Available License v6.2)
- SPDX: `LicenseRef-Zer0pa-SAL-6.2`
- Python metadata and Rust crate metadata both declare the repo as `LicenseRef-Zer0pa-SAL-6.2`

## Claim Boundaries

- This staged repo contains biosignal codec code and committed validation artifacts.
- It does not grant clinical efficacy claims.
- It does not grant human-equivalence claims.
- It does not grant Bio Wearable release claims.

## Data Boundaries

- `validation/datasets/mitdb/` is staged for ECG-oriented local verification.
- Larger local-only dataset mirrors are excluded from the staged git surface.

## Audit Boundaries

- Historical result artifacts may preserve machine-specific paths.
- Those paths are provenance traces, not current repo instructions.
