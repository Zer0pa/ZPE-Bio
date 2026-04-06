# MIT-BIH Python-Only Benchmark Summary

Generated: `2026-04-06T17:19:07.936628+00:00`
Dataset: `validation/datasets/mitdb`
Records processed: `48`
Mode: `clinical` | Threshold mode: `adaptive_rms`

## Aggregate

| Metric | Value |
| --- | ---: |
| Mean compression ratio | 1.323216 |
| Median compression ratio | 1.316049 |
| Min compression ratio | 1.253408 |
| Max compression ratio | 1.388166 |
| Mean SNR (dB) | 43.294294 |
| Mean RMSE (uV) | 3.235821 |
| Mean encode time (us) | 286804.472 |
| Mean decode time (us) | 128961.385 |
| Mean PRD (%) | 1.115854 |
| Max PRD (%) | 2.324893 |
| Integrity passes | 48/48 |

## By Diagnosis Bucket

Diagnosis grouping is derived from MIT-BIH header comment text. Records without explicit normal-sinus phrasing remain in `normal_or_unannotated` rather than being relabeled.

| Diagnosis bucket | Records | Mean CR | Median CR | Mean SNR (dB) | Mean RMSE (uV) |
| --- | ---: | ---: | ---: | ---: | ---: |
| arrhythmia_or_conduction_disorder | 37 | 1.318587 | 1.313176 | 42.962161 | 3.201989 |
| normal_or_unannotated | 11 | 1.338786 | 1.341224 | 44.411471 | 3.349620 |

## Per-Record Table

| Record | Diagnosis bucket | CR | SNR (dB) | RMSE (uV) | Encode (us) | Decode (us) | Integrity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 100 | normal_or_unannotated | 1.341224 | 41.497192 | 3.152792 | 695902.603 | 397779.984 | pass |
| 101 | normal_or_unannotated | 1.316352 | 41.903749 | 2.803783 | 492569.956 | 108240.598 | pass |
| 102 | arrhythmia_or_conduction_disorder | 1.311067 | 40.508525 | 2.800429 | 400334.819 | 696357.186 | pass |
| 103 | normal_or_unannotated | 1.350416 | 40.852424 | 3.645916 | 394491.568 | 196130.945 | pass |
| 104 | arrhythmia_or_conduction_disorder | 1.314233 | 41.299674 | 3.106670 | 398616.583 | 201517.291 | pass |
| 105 | arrhythmia_or_conduction_disorder | 1.320764 | 42.467927 | 2.934059 | 400020.353 | 201407.514 | pass |
| 106 | arrhythmia_or_conduction_disorder | 1.301660 | 40.798739 | 3.959609 | 492433.888 | 201250.155 | pass |
| 107 | arrhythmia_or_conduction_disorder | 1.325820 | 49.539565 | 2.980285 | 402403.051 | 202038.544 | pass |
| 108 | arrhythmia_or_conduction_disorder | 1.299292 | 41.537930 | 2.568015 | 394634.257 | 197052.551 | pass |
| 109 | arrhythmia_or_conduction_disorder | 1.311819 | 44.943477 | 2.909536 | 406019.382 | 196218.703 | pass |
| 111 | arrhythmia_or_conduction_disorder | 1.285409 | 39.994389 | 2.716137 | 504956.117 | 197858.381 | pass |
| 112 | normal_or_unannotated | 1.348504 | 49.415312 | 3.003415 | 497482.281 | 203474.869 | pass |
| 113 | arrhythmia_or_conduction_disorder | 1.313629 | 42.329823 | 3.604081 | 399636.988 | 199604.802 | pass |
| 114 | arrhythmia_or_conduction_disorder | 1.287581 | 38.969896 | 2.523014 | 592786.740 | 109072.009 | pass |
| 115 | normal_or_unannotated | 1.361517 | 43.511444 | 3.915201 | 302862.701 | 107149.007 | pass |
| 116 | arrhythmia_or_conduction_disorder | 1.364931 | 47.494811 | 4.723600 | 405133.724 | 190727.962 | pass |
| 117 | normal_or_unannotated | 1.315595 | 49.314416 | 2.838010 | 598728.358 | 107620.069 | pass |
| 118 | arrhythmia_or_conduction_disorder | 1.295463 | 50.403741 | 3.272048 | 404699.909 | 194855.528 | pass |
| 119 | arrhythmia_or_conduction_disorder | 1.313176 | 48.902891 | 3.522471 | 107590.760 | 19165.767 | pass |
| 121 | normal_or_unannotated | 1.330451 | 49.949336 | 2.782229 | 398364.237 | 108066.453 | pass |
| 122 | normal_or_unannotated | 1.279652 | 49.168572 | 3.267323 | 46670.852 | 19464.394 | pass |
| 123 | arrhythmia_or_conduction_disorder | 1.315746 | 48.249307 | 3.394024 | 107951.915 | 19064.740 | pass |
| 124 | arrhythmia_or_conduction_disorder | 1.352014 | 48.911002 | 3.208956 | 45796.474 | 36374.443 | pass |
| 200 | arrhythmia_or_conduction_disorder | 1.316807 | 42.892229 | 3.064066 | 92156.851 | 19356.036 | pass |
| 201 | arrhythmia_or_conduction_disorder | 1.358119 | 38.751303 | 3.110836 | 132755.565 | 19000.650 | pass |
| 202 | arrhythmia_or_conduction_disorder | 1.297669 | 39.793348 | 2.663419 | 47341.413 | 19697.721 | pass |
| 203 | arrhythmia_or_conduction_disorder | 1.253408 | 43.514073 | 3.537188 | 47732.008 | 19698.740 | pass |
| 205 | arrhythmia_or_conduction_disorder | 1.373957 | 41.375135 | 3.276080 | 46657.654 | 48072.773 | pass |
| 207 | arrhythmia_or_conduction_disorder | 1.299883 | 42.033090 | 2.525906 | 47478.362 | 19687.830 | pass |
| 208 | arrhythmia_or_conduction_disorder | 1.291364 | 44.708318 | 3.366185 | 97261.489 | 24422.057 | pass |
| 209 | normal_or_unannotated | 1.318326 | 38.471323 | 3.378491 | 58184.994 | 21604.025 | pass |
| 210 | arrhythmia_or_conduction_disorder | 1.317111 | 39.939263 | 2.867856 | 48782.864 | 19524.243 | pass |
| 212 | arrhythmia_or_conduction_disorder | 1.305675 | 40.210328 | 3.510342 | 47651.288 | 106546.614 | pass |
| 213 | arrhythmia_or_conduction_disorder | 1.384778 | 44.385696 | 4.262370 | 46111.920 | 18970.691 | pass |
| 214 | arrhythmia_or_conduction_disorder | 1.293117 | 44.152323 | 3.115622 | 48050.383 | 19861.259 | pass |
| 215 | arrhythmia_or_conduction_disorder | 1.292679 | 38.644033 | 3.339251 | 65073.171 | 68051.190 | pass |
| 217 | arrhythmia_or_conduction_disorder | 1.296786 | 46.818291 | 2.819096 | 402420.990 | 108701.505 | pass |
| 219 | arrhythmia_or_conduction_disorder | 1.368691 | 46.094645 | 3.728485 | 46091.660 | 18963.591 | pass |
| 220 | normal_or_unannotated | 1.388166 | 43.880888 | 4.061810 | 171733.163 | 193755.412 | pass |
| 221 | arrhythmia_or_conduction_disorder | 1.288598 | 41.037948 | 3.074280 | 399110.806 | 107371.562 | pass |
| 222 | arrhythmia_or_conduction_disorder | 1.290635 | 36.825671 | 2.651056 | 399260.404 | 195086.383 | pass |
| 223 | arrhythmia_or_conduction_disorder | 1.374452 | 46.159939 | 3.404541 | 310900.200 | 195097.104 | pass |
| 228 | arrhythmia_or_conduction_disorder | 1.284975 | 42.715009 | 2.955774 | 401015.880 | 107424.851 | pass |
| 230 | normal_or_unannotated | 1.376439 | 40.561527 | 3.996849 | 493704.302 | 299737.453 | pass |
| 231 | arrhythmia_or_conduction_disorder | 1.340909 | 40.224089 | 3.232151 | 398271.197 | 195146.443 | pass |
| 232 | arrhythmia_or_conduction_disorder | 1.318478 | 38.702705 | 2.750818 | 229934.898 | 19665.521 | pass |
| 233 | arrhythmia_or_conduction_disorder | 1.371154 | 44.190851 | 3.619558 | 400206.870 | 106947.378 | pass |
| 234 | arrhythmia_or_conduction_disorder | 1.355863 | 40.079956 | 3.375767 | 398638.822 | 107263.533 | pass |

## Artifacts

- Per-record JSON: `validation/results/mitdb_python_only`
- Aggregate JSON: `validation/results/mitdb_python_only/mitdb_aggregate.json`
- Summary CSV: `validation/results/mitdb_python_only/mitdb_summary.csv`

