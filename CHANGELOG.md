# Changelog

All notable repo-surface changes to ZPE-Bio are documented here.

This changelog tracks the staged repo surface, not a public release line.

## Unreleased

### Added

- Runnable example scripts under `examples/`
- WFDB interop and clean-install tests
- Repo-level benchmark index (`BENCHMARKS.md`)
- Public PhysioNet benchmark summaries for PTB-XL, NSTDB, EDB, and Sleep-EDF
- Optional dependency groups for test and docs workflows
- Root repo front door (`README.md`)
- Repo-level audit and proof entry points
- Repo-level legal/license surface
- Docs landing and boundary notes

### Changed

- Packaging metadata now points to the root README and declared dual license
- Active front-door docs now use repo-relative path language instead of machine-specific roots
- Local-only dataset directories are excluded from staged git scope
- PhysioNet benchmark payloads now include gzip baseline comparisons and direct Sleep-EDF EDF acquisition
- README benchmark snapshot now points to the committed Phase-3 benchmark artifacts

### Removed

- Nothing removed from committed proof history; only disposable local build/caches are cleaned in this phase
