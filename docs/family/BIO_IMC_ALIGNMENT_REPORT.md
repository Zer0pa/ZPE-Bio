# BIO-IMC Alignment Report (Wave-1)

## Scope
- Bio repo: repository root (`.`)
- IMC freeze source: `ZPE-IMC` `docs/family/` release contract surface
- Alignment mode: artifact-level only (no IMC runtime import coupling)

## Freeze Verification
- IMC contract version consumed: `wave1.0`
- IMC compatibility vector sha256:
  `9c8b905f6c1d30d057955aa9adf0f7ff9139853494dca673e5fbe69f24fba10e`
- Canonical metric authority:
  `IMC_COMPATIBILITY_VECTOR.json` `canonical_demo_metrics.total_words = 844`

## Shared Contract Assumptions
1. 20-bit word layout with mode/version/payload bit boundaries.
2. Extension-mode modality markers retained (`touch=0x0800`, `smell=0x0200`, `taste=0x0400`, etc.).
3. Dispatch semantics reference IMC frozen precedence ordering.
4. Bio compatibility gates validate packet extraction and deterministic replay against frozen assumptions.

## Bio Guarantees in Wave-1 Refinement
1. Python/Rust parity remains a required gate (`tests/test_parity.py`, CI Rust matrix).
2. Golden packet fixture added and enforced (`tests/fixtures/wave1_golden_packets.json`, `tests/test_packet_compatibility.py`).
3. Strict unsupported-version decode behavior added for packet ingress:
   `UnsupportedPacketVersionError` for smell/touch version drift when `strict_versions=True`.

## Known Divergences (Intentional)
1. Bio release includes biosignal-specific command lanes not part of IMC CLI.
2. Bio CLI demo outputs are not canonicalized against IMC total words; IMC vector remains authority for family-level compatibility.
3. Bio release engineering includes biomedical falsification gates beyond IMC release scope.

## Coordination Outcome
Wave-1 alignment is **compatible at artifact contract level** with IMC freeze `wave1.0`, with canonical authority pinned to IMC vector (`844`) and divergences explicitly documented for non-breaking sector specialization.
