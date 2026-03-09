# FAQ

## What is this repo?

The ZPE-Bio sector repo: a deterministic biosignal codec plus Bio-specific validation and coordination artifacts.

## Is this a public release snapshot?

No. This is a staged private repo baseline prepared on 2026-03-09.

## What is the main package surface?

`python/zpe_bio/` with the `zpe-bio` CLI entry point.

## Where is the proof surface?

Committed proof artifacts live under `validation/results/`, indexed by `../PROOF_INDEX.md`.

## Why are some datasets missing from git?

Large EEG, SisFall, and wearable mirrors were kept local-only to keep the staged repo bounded. Later verification phases can reacquire or attach them explicitly.

## Is Bio Wearable part of the current pass?

Its artifacts are present, but its status remains `NO_GO`.
