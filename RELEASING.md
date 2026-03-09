# Releasing

This repository is private-first. Do not treat a staged private push as a release verdict.

## Hard Gate

No public release action is allowed until all of the following are true:

- the exact release commit has passed Phase 5 verification
- the exact release commit has been inspected on its staged private remote
- unresolved correctness gaps are either closed or explicitly accepted by the operator
- Bio Wearable status is represented honestly in the release surface

## Current Blockers

- this phase did not rerun the full verification stack
- Wave-2 lint and multimodal manifest correction remain open
- large local-only datasets are intentionally excluded from the staged repo

## Private Staging Rule

Use the private GitHub repo as the only staging target. Do not change visibility, create a public release, or publish package artifacts from this phase output.
