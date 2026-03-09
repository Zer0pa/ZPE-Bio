# Legal Boundaries

This note is a repo-surface summary only. The root license files are the legal source of truth.

## License Surface

- Repository license selector: `../LICENSE`
- Apache text: `../LICENSE-APACHE`
- MIT text: `../LICENSE-MIT`
- Python metadata and Rust crate metadata both declare the repo as dual-licensed `Apache-2.0 OR MIT`

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
