# BIO Coordination Note (Wave-1)

Release Wave: `Wave-1`  
Bio Package: `zpe-bio==0.2.0`  
IMC Freeze Consumed: `wave1.0` (`IMC_COMPATIBILITY_VECTOR.json`)

## Coordination Guarantees
1. Bio consumes IMC coordination artifacts by reference only; no runtime coupling to IMC package internals.
2. Canonical cross-repo coordination authority is pinned to the IMC compatibility vector (`total_words=844`).
3. Bio compatibility vector and alignment report are published in `docs/family/`.

## Bio Wave-1 Refinement Highlights
1. Version canonicalization and stale artifact cleanup completed for release hygiene.
2. Runtime decode hardening added for unsupported packet version handling in strict mode.
3. Golden packet fixture and deterministic replay tests added for wire-format confidence.
4. Python/Rust parity enforced across CI Rust matrix dimensions (OS + Python version).
5. Release workflow upgraded with gated quality checks and integrity manifest generation.

## Divergence Notes
1. Bio includes biosignal-focused CLI surfaces that are not part of IMC runtime contract.
2. Bio demo stream metrics are not used as canonical IMC compatibility authority.

## Downstream Action Items
1. Coordination owner: mark required checks as:
   - `CI Python / lint-test-build`
   - `CI Rust / rust-quality`
   - `Release / quality-gates`
   - `Release / build-and-attest`
2. Consumer teams: replay against Bio and IMC compatibility vectors before promoting release tags.
