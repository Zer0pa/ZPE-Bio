# MIT-BIH codec comparison (Wave-CB)

Records: 48 (full corpus, all 48 MIT-BIH .dat files).

Lossless comparators on raw int16 .dat bytes (mean CR):
- gzip (level 6): 1.429
- zlib (level 6): 1.429
- zstd (level 3): 1.412

ZPE-Bio (clinical mode, 10k-sample window, fidelity-bounded-lossy, mean PRD ~1.12%, max PRD <= 2.32%): 1.323

Honest framing: ZPE-Bio is a fidelity-bounded-lossy ECG codec; gzip/zlib/zstd are lossless byte compressors. Direct CR comparison is not apples-to-apples. Loss on raw CR is expected and surfaced honestly here.
