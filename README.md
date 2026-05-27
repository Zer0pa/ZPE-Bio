# ZPE-Bio

> Product-page mirror for `/encoding/ZPE-Bio/`.
> Live public repo: [Zer0pa/ZPE-Bio](https://github.com/Zer0pa/ZPE-Bio).
> GitHub Markdown cannot reproduce the website typography, CSS, JavaScript, scroll behavior, or live bento layout; this README translates the product page into GitHub-safe Markdown evidence blocks.

## 0. Install / Developer Commands

The product page is the positioning authority. This section is the only retained developer-surface material from the previous root README.

```bash
Fidelity-bounded ECG archival codec. Deterministic PRD <=2.32% contract, Python CLI, Rust core, and MIT-BIH/PTB-XL validation. Install from PyPI: `pip install zpe-bio
- `tests/`: repo-local pytest suite
pip install -e ".[dev,validation]"
```

## Product Page Mirror

**Product-page title:** ZPE-Bio · ECG replay error measured by PRD · Zer0pa

**Product-page description:** ZPE-Bio · ECG-only staged codec · MIT-BIH 48/48 at mean PRD 1.12% against a 2.32% target · PTB-XL 100/100 max PRD 5.29% outside current target · Python + Rust repo CI parity · stale PyPI v0.2.1 · github.com/Zer0pa/ZPE-Bio

### Hero Translation

> 00 · ZPE-BIO · ECG CODECDEVELOPER-READY · PTB-XL OPEN ECG that names its excursion delta. ECG-only staged codec · ZPE-Bio · PyPI zpe-bio v0.2.1 · github.com/Zer0pa/ZPE-Bio ZPE-Bio compresses heart-rhythm recordings and publishes the replay error on every dataset it touches. On MIT-BIH, all 48 records return inside the 2.32% clinical target with a mean replay error of 1.12%. PTB-XL processes cleanly but one record drifts to 5.29%, so the wider ECG surface is named, not claimed. This is a developer-ready archival codec, not a clinical device, wearable, or regulatory product.

## Positioning

| Field | Value |
| --- | --- |
| Section | encoding |
| Product route | /encoding/ZPE-Bio/ |
| Live public repository | https://github.com/Zer0pa/ZPE-Bio |
| Repo identity used here | ZPE-Bio |
| Website display identity | ZPE-Bio |
| Verdict | STAGED |
| Posture | always_in_beta |
| Headline metric | MIT-BIH 48/48 integrity, mean PRD 1.12%, mean SNR 43.3 dB. ZPE-Bio canonical authority surface; useful now, improving continuously. |
| Honest blocker | PTB-XL max PRD reaches 5.29% (100-record sample) — above the clinical 2.32% contract threshold. This is an open boundary; PTB-XL is logged but not claimed under the clinical fidelity contract. |
| Mechanics asset from product page | BIO.gif |

## Key Metrics

| Metric | Value | Baseline |
| --- | --- | --- |
| MIT-BIH Arrhythmia (mitdb) | 48/48 (100%) | Mean PRD 1.12%, Mean SNR 43.3 dB |
| MIT-BIH Noise Stress (nstdb) | 15/15 (100%) | Mean SNR 60.5 dB |
| European ST-T (edb) | 90/90 (100%) | Mean SNR 52.5 dB |
| PTB-XL (sample) | 100/100 (100%) | Max PRD 5.29% — open boundary |

## Proof Anchors

| Path | State |
| --- | --- |
| validation/results/BENCHMARK_SUMMARY.md | VERIFIED |
| validation/results/mitdb_python_only/mitdb_aggregate.json | VERIFIED |
| validation/results/ptbxl/summary.json | VERIFIED |
| tests/test_parity.py | VERIFIED |

## What We Prove

- MIT-BIH 48/48 records processed with 100% integrity pass rate, mean PRD 1.12%, mean SNR 43.3 dB, max PRD 2.32% — within clinical contract.
- MIT-BIH Noise Stress 15/15 records, 100% integrity, mean SNR 60.5 dB, max PRD 1.96%.
- European ST-T 90/90 records, 100% integrity, mean SNR 52.5 dB.
- PTB-XL 100/100 records (sample), 100% integrity.
- Python and Rust codec implementations are parity-gated in CI.
- Deterministic round-trip replay is CI-anchored.

## What We Do Not Claim

- No public release-readiness verdict
- No generalized biosignal victory claim
- No Bio Wearable closure claim
- No regulatory or FDA claim

## Blockers / Failures

> PTB-XL max PRD reaches 5.29% (100-record sample) — above the clinical 2.32% contract threshold. This is an open boundary; PTB-XL is logged but not claimed under the clinical fidelity contract.

## Verification Surface

| Code | Check | Verdict |
| --- | --- | --- |
| V_01 | MIT-BIH benchmark writer emits summary + aggregate artifacts | PASS |
| V_02 | PTB-XL benchmark writer emits committed-style summary artifacts | PASS |
| V_03 | Clinical ECG round-trip remains deterministic and high-fidelity in the Python codec | PASS |
| V_04 | Python and Rust codec implementations remain parity-gated in CI | PASS |

## License

| Field | Value |
| --- | --- |
| License | SAL-7.0 |
| Authority source | validation/results/BENCHMARK_SUMMARY.md |

## Upcoming Workstreams

| Category | Summary |
| --- | --- |
| Active Engineering | Rust embedded encode/decode path. Wearable-cardiac-monitor wedge requires sub-ms latency and constrained-resource execution; foundation primitives are mature. |
| Research-Deferred — Investigation Underway | Regulatory alignment scoping (IEC 60601 / FDA). The PRD-bounded fidelity contract is a regulatory moat that lossless coders cannot match; alignment work scopes the path to clinical submission. |

## Related Repos

No related repos are declared on the product page frontmatter.

<details>
<summary>Full Visible Product-Page Bento Translation</summary>

This section preserves the product page cells as Markdown text blocks. It intentionally omits shared site navigation, footer chrome, CSS, and scripts.

### Bento Cell 1

> 00 · ZPE-BIO · ECG CODECDEVELOPER-READY · PTB-XL OPEN ECG that names its excursion delta. ECG-only staged codec · ZPE-Bio · PyPI zpe-bio v0.2.1 · github.com/Zer0pa/ZPE-Bio ZPE-Bio compresses heart-rhythm recordings and publishes the replay error on every dataset it touches. On MIT-BIH, all 48 records return inside the 2.32% clinical target with a mean replay error of 1.12%. PTB-XL processes cleanly but one record drifts to 5.29%, so the wider ECG surface is named, not claimed. This is a developer-ready archival codec, not a clinical device, wearable, or regulatory product.

### Bento Cell 2

> 01 · THE GAPMEASURED, NOT ASSUMED ECG codecs that report file size without naming their replay error leave clinicians guessing.

### Bento Cell 3

> 02 · MARKETSADJACENT FORECASTS Digital cardiovascular health ’30$141.0B Cardiac monitoring devices ’32$31.6B Wearable ECG monitors ’30$13.7B ECG monitoring devices ’30$12.4B ECG data analytics ’30$4.2B Where this codec belongs: archive replay and cardiology data stewardship. No clinical-device, wearable, or regulatory readiness claim.

### Bento Cell 4

> 03 · VALUE 48/48 MIT-BIH records replay inside the 2.32% target · mean 1.12% replay error

### Bento Cell 5

> 04 · INSIGHT Every replayed ECG should carry its measured change.

### Bento Cell 6

> 05.1 · CURRENT TECHSIZE WITHOUT FIDELITY Lossless compressors preserve bytes and report file-size ratios. They tell a cardiology archive nothing about how closely a replayed waveform tracks the original signal on any named clinical corpus.

### Bento Cell 7

> 05.2 · OUR TECHREPLAY ERROR PUBLISHED ZPE-Bio reports replay error directly per dataset. On MIT-BIH, 48 of 48 records return at mean 1.12%, inside the 2.32% clinical target a cardiology archive can show its review board. PTB-XL processes 100 of 100 records with full integrity but a worst-case record reaches 5.29%, so that corpus is named openly as out of contract rather than buried.

### Bento Cell 8

> 05.3 · BENCHMARKSFOUR CORPORA MIT-BIH48/48PASS NSTDB15/15PASS EDB90/90PASS PRD target2.32%MIT-BIH MIT-BIHPASS NSTDBPASS PTB-XLout Reported today: MIT-BIH 48/48 · NSTDB 15/15 · EDB 90/90 · PTB-XL 5.29% out.

### Bento Cell 9

> 06 · MEASUREMENTPRD BY CORPUS Replay error reported per corpus, with MIT-BIH as the reference.

### Bento Cell 10

> 06.1 · COMPARATIVE PERFORMANCEPRD BY CORPUS MIT-BIH · mean1.12% NSTDB · max1.96% EDB · max4.34% · LOG PTB-XL · max5.29% · OUT MIT-BIH Arrhythmia (48 records), NSTDB (15), EDB (90), PTB-XL (100 sampled). MIT-BIH target: replay error ≤ 2.32%. File-size winners stay gzip and zstd; this codec competes on fidelity, not bytes.

### Bento Cell 11

> 07 · KEY METRICSMEASURED RESULTS

### Bento Cell 12

> 07.1 · MIT-BIH INTEGRITY 48/48 MIT-BIH records replay clean · integrity pass

### Bento Cell 13

> 07.2 · MEAN CR 1.12% MIT-BIH aggregate replay error · inside the clinical target

### Bento Cell 14

> 07.3 · PTB-XL INTEGRITY 100/100 PTB-XL 100-record sample · worst 5.29% disclosed

### Bento Cell 15

> 07.4 · PRD TARGET 2.32% MIT-BIH clinical target · met by mean

### Bento Cell 16

> 07.5 · MEAN PRD 1.12% MIT-BIH 48-record mean · inside target

### Bento Cell 17

> 08 · DETERMINISMCI PARITY PYTHON + RUST Python and Rust replay the ECG surface consistently.

### Bento Cell 18

> 08.1 · WHAT DETERMINISTIC MEANSECG SURFACE ONLY Repo CI runs Python and Rust round-trips on every push across MIT-BIH, NSTDB, the European ST-T Database, and PTB-XL. Replay error is reported per dataset. MIT-BIH sits inside the 2.32% target at a mean of 1.12%. PTB-XL logs 100 of 100 records with full integrity, but the worst-case replay error reaches 5.29% and stays visible in the public results. PyPI 0.2.1 is stale and is not presented as fresh; the surface is ECG-only.

### Bento Cell 19

> 08.2 · THE FIDELITY GAP Honest Blocker · PTB-XL processes 100 of 100 records, but the worst-case replay error reaches 5.29%, outside the 2.32% MIT-BIH target. PyPI is stale at zpe-bio 0.2.1. Wearable-data scope and the 0x0400 marker policy are open. No clinical, regulatory, EEG, wearable, or raw-size superiority claim.

### Bento Cell 20

> 09 FIVE PATHS FROM ONE CLINICAL CONTRACT.

### Bento Cell 21

> 09.1 · THE AMBITION The hinge is the disclosed boundary, not the passed contract. A codec that names its worst-case excursion alongside its pass rate becomes the substrate cardiology archives can adopt before regulatory engagement — because the open question is already on the table, not waiting in the field.

### Bento Cell 22

> 09.2 · WHAT WORKS NOWEXTERNAL MIT-BIH 48/48 records pass; the mean replay error of 1.12% sits inside the 2.32% clinical target.

### Bento Cell 23

> 09.3 · WHAT'S STILL OPENEXTERNAL PTB-XL excursion at 5.29%, stale PyPI release, wearable scope, and marker-policy decision are open.

### Bento Cell 24

> 09.4 · ARCHIVES · NEAR-TERM (12–24 MO) Cardiology archives gain a fidelity floor An academic cardiology lab can stop hoarding raw float32 MIT-BIH waveforms because every record returns inside a documented 2.32% replay error. Storage budgets fall and the archived signal still satisfies clinical research review.

### Bento Cell 25

> 09.5 · PROCUREMENT · NEAR-TERM (12–24 MO) Buyers decide before deployment, not after A cardiology archive buyer who sees the PTB-XL 5.29% excursion published alongside the MIT-BIH pass rate can choose with eyes open. Disclosure shifts procurement from a post-purchase surprise to a pre-purchase conversation about which corpora the buyer actually needs.

### Bento Cell 26

> 09.6 · CLINICAL RESEARCH · MID-TERM (24–48 MO) Reproducible studies travel between sites When two cardiology research groups share compressed waveforms with identical replay error, a finding produced at one institution can be re-run at another without arguing about whether the data was altered in transit. Reproducibility stops depending on raw-byte custody.

### Bento Cell 27

> 09.7 · BOUNDARY CLOSURE · MID-TERM (24–48 MO) PTB-XL becomes a routine corpus If codec tuning brings the PTB-XL worst-case replay error from 5.29% under the 2.32% target, the PTB-XL population — broader demographics, more leads, longer recordings — joins the safely archivable set. The cardiology research community gains a second large public corpus with a fidelity guarantee.

### Bento Cell 28

> 09.8 · INDUSTRY STANDARD · PARADIGM (48 MO+) Fidelity claims arrive with disclosure attached ECG codecs across the industry begin publishing their per-dataset thresholds, worst-case excursions, and pass rates as standard practice. Hospitals, regulators, and procurement teams stop accepting a single global fidelity number and start asking which corpus, which boundary, which pass rate.

</details>

---

Source mapping: product route `/encoding/ZPE-Bio/` -> live public repo `Zer0pa/ZPE-Bio`. README generated from product-page authority plus retained install/dev commands only.
