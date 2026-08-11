# Monte Carlo Method Scalability Analysis (v3, consistent): N = 3×3, 5×5, 9×9

## Technical summary

This document compares the *Random-TX* Monte Carlo method (notebook section 11) across three TX-array / RX-lens-scenario sizes: **N = 3, 5, and 9**, from three consistent **"v3"** notebooks:

1. **N = 3** — [`Setupv3_20mx20m_lens_3x3_Patch_randomCom.ipynb`](Setupv3_20mx20m_lens_3x3_Patch_randomCom.ipynb)
2. **N = 5** — [`Setupv3_20mx20m_lens_5x5_Patch_randomCom.ipynb`](Setupv3_20mx20m_lens_5x5_Patch_randomCom.ipynb)
3. **N = 9** — [`Setupv3_20mx20m_lens_9x9_Patch_randomCom.ipynb`](Setupv3_20mx20m_lens_9x9_Patch_randomCom.ipynb)

All three notebooks use a 20 m × 20 m × 3 m room, 38 GHz, 20 Monte Carlo *drops*, 100,000 ray-tracing samples per source, 10 dBm per TX, and the same random seed (20260718). The **only** thing that differs is the number of TX elements / RX lens-angle scenarios (N). Numbers in this document are **not recomputed** — every value is taken from cell outputs already stored in the three notebooks (see `MonteCarlo_Scalability_Analysis_v3_3x3_5x5_9x9/data/raw_logs/`).

> **Version note.** This is the **corrected** version of an earlier comparison ([`ANALISIS_SKALABILITAS_MONTE_CARLO_3x3_5x5_9x9.md`](ANALISIS_SKALABILITAS_MONTE_CARLO_3x3_5x5_9x9.md), Indonesian), which used the **"v2"** notebook for the N=5 data point (`Setupv2_20mx20m_lens_5x5_Patch_randomCom.ipynb`). That v2 notebook turned out to contain a double radian-conversion bug in `rx_orientation_deg` (a value already in radians, returned by `rotate_antenna(...)`, was converted a second time through `np.deg2rad()`), which made power/gain-based metrics for N=5 in the old analysis under-estimated and non-monotonic in N. The **v3** notebook used here sets orientation with plain degree literals (same as N=3 and N=9) and does **not** contain that bug. As shown below, the result is a much cleaner, fully consistent picture. *(An Indonesian-language version of this same corrected comparison is also available: [`ANALISIS_SKALABILITAS_MONTE_CARLO_v3_3x3_5x5_9x9.md`](ANALISIS_SKALABILITAS_MONTE_CARLO_v3_3x3_5x5_9x9.md).)*

**Key findings:**

- **Compute cost grows linearly with N** (not quadratically), thanks to the "simultaneous TX, one shared pattern" design — 3, 5, 9 PathSolver runs per fixed-geometry scenario (versus a naive 9, 25, 81 if each TX element were simulated one at a time).
- **Capacity increases monotonically with N across almost every metric** — virtual-MIMO capacity @10dB (7.9 → 14.2 → 21.7 bit/s/Hz), median aggregate Monte Carlo capacity (5.94 → 6.46 → 7.67 bit/s/Hz), median ideal throughput (2.38 → 2.58 → 3.07 Gbit/s), and median RMS delay spread (59.1 → 63.5 → 65.0 ns).
- **Virtual-MIMO condition number worsens monotonically with N**, both on fixed geometry (11.7 → 15.1 → 38.8 dB) and averaged over 20 Monte Carlo drops (17.5 → 24.6 → 34.6 dB).
- **The effective-rank-to-N ratio tends to decrease for larger N** — a clean, monotonic diminishing-returns pattern in the per-drop Monte Carlo data (64% → 55% → 45%), even though one single fixed-geometry data point briefly shows N=5 with the highest ratio (68%) — discussed in section 2.
- Because all three notebooks are now genuinely consistent ("v3" throughout), **no anomaly/bug was found** this time — every trend can be read at face value.

## Data sources and assets

All CSV tables, PNG figures, raw logs, and the script that produced them are stored in a dedicated folder:
[`MonteCarlo_Scalability_Analysis_v3_3x3_5x5_9x9/`](MonteCarlo_Scalability_Analysis_v3_3x3_5x5_9x9/) (see the `README.md` inside for a map of the contents).

## Scope and simulation parameters

| Parameter | N=3 | N=5 | N=9 |
|---|---:|---:|---:|
| Room dimensions | 20×20×3 m | 20×20×3 m | 20×20×3 m |
| Frequency / bandwidth | 38 GHz / 400 MHz | same | same |
| Frequency points (N_F) | 401 | 401 | 401 |
| TX elements (fixed geometry) | 3 | 5 | 9 |
| TX array aperture (Y) | ±0.45 m | ±0.90 m | ±1.80 m |
| RX lens-angle scenarios | 3 (−45°, 0°, +45°) | 5 (−60°…+60°, 30° step) | 9 (−60°…+60°, 15° step) |
| Monte Carlo drops | 20 | 20 | 20 |
| Ray samples/source (Monte Carlo) | 100,000 | 100,000 | 100,000 |
| Power per TX | 10 dBm | 10 dBm | 10 dBm |
| Noise figure / temperature | 7 dB / 290 K | same | same |
| Random seed | 20260718 | 20260718 | 20260718 |
| Total PathSolver runs, fixed geometry (sec. 8) | 3 | 5 | 9 |
| Total PathSolver runs, Monte Carlo (sec. 11) | 60 (20×3) | 100 (20×5) | 180 (20×9) |

All parameters are identical except N and the set of lens angles tested (see [Limitations](#limitations-and-caveats), item 3) — a good setup for a clean scalability comparison.

## 1. Compute-cost scalability

![Fig. 1 — Compute-cost scalability](MonteCarlo_Scalability_Analysis_v3_3x3_5x5_9x9/figures/fig1_compute_cost_scalability.png)

| | N=3 | N=5 | N=9 | Ratio 9/3 |
|---|---:|---:|---:|---:|
| Actual runs (fixed geometry, simultaneous TX) | 3 | 5 | 9 | 3× |
| Naive runs (1 TX element / run) | 9 | 25 | 81 | 9× |
| Actual Monte Carlo runs (20 drops × N) | 60 | 100 | 180 | 3× |
| Naive Monte Carlo runs (20 drops × N²) | 180 | 500 | 1620 | 9× |

Because all TX elements share the same pattern and radiate simultaneously in a single Sionna scene, the number of `PathSolver` calls grows **linearly with N**, not quadratically. Going from N=3 to N=9 (a 3× increase in element count), the actual compute cost rises 3× (9 vs 180 Monte Carlo runs), while a naive scheme (each TX element simulated on its own) would rise 9× (81 vs 1620 runs). This "simultaneous TX, one shared pattern" trick is the design decision that keeps the N=9 configuration (180 runs × 100,000 ray samples) practical to run at all, versus the 1620 runs a naive scheme would require.

Note that this linearity is linearity in the **number of solver calls**, not in the **cost per call** — the ray-tracing cost of each individual call itself likely also grows with N (more simultaneous sources means more ray paths to trace for the same `samples_per_src`), so the real speed-up over the naive scheme is likely larger than the "run count" ratio alone suggests, but its magnitude was not measured here (no wall-clock timing log is stored in any of the three notebooks).

## 2. Virtual N×N MIMO on fixed TX geometry (section 10)

![Fig. 2 — MIMO on fixed geometry](MonteCarlo_Scalability_Analysis_v3_3x3_5x5_9x9/figures/fig2_mimo_fixed_geometry_vs_N.png)

| Metric | N=3 | N=5 | N=9 |
|---|---:|---:|---:|
| Condition number, median | 3.8 (11.7 dB) | 5.7 (15.1 dB) | 86.7 (38.8 dB) |
| Effective rank, median | 1.61 / 3 (54%) | 3.39 / 5 (68%) | 4.25 / 9 (47%) |
| Capacity @10dB | 7.87 bit/s/Hz | 14.24 bit/s/Hz | 21.66 bit/s/Hz |

The "N×N MIMO" matrix here is a synthetic combination of N different RX-lens measurements (not N simultaneously active receivers — see the physical caveat in the source notebooks), evaluated via SVD of the combined channel.

Median condition number rises monotonically with N: 11.7 dB (N=3) → 15.1 dB (N=5) → 38.8 dB (N=9). **Capacity @10dB also rises monotonically**, and is now much more evenly spaced (7.87 → 14.24 → 21.66 bit/s/Hz) than in the earlier analysis that used the flawed N=5 data.

One notable feature: **the effective-rank ratio at this N=5 point is actually the highest of the three (68%)**, rather than sitting neatly between N=3 (54%) and N=9 (47%). This is **not** a sign of a bug (there is no orientation issue here — see the configuration check in the README) but rather a **single-fixed-geometry-sample characteristic**: section 10 combines only one fixed realization per N, so it is sensitive to how well that particular geometry's five lens angles happen to match the RX position. Section 5 (Monte Carlo, averaged over 20 drops rather than one point) shows a smoother and monotonically decreasing pattern (64% → 55% → 45%) — confirming that the "68% at N=5" is single-sample variance, not the underlying scalability trend. This is a useful reminder that a single fixed-geometry metric (section 10) carries non-trivial sample variance, and more reliable scalability conclusions should lean on the multi-drop average (section 11c, see section 5 below).

Despite conditioning getting worse, **absolute capacity keeps rising** with N (7.87 → 14.24 → 21.66 bit/s/Hz) because full-eigenmode capacity sums the contribution of every spatial mode at once — even weak/correlated modes still add a little capacity in the high-SNR regime. This is the classic *diminishing-but-positive returns* pattern: capacity rises, but not proportionally to N (21.66 bit/s/Hz at N=9 is not 3× the 7.87 bit/s/Hz at N=3, even though N itself tripled).

## 3. RX-side spatial correlation (section 10b)

![Fig. 3 — RX-side spatial correlation](MonteCarlo_Scalability_Analysis_v3_3x3_5x5_9x9/figures/fig3_rx_correlation_vs_N.png)

| Metric | N=3 | N=5 | N=9 |
|---|---:|---:|---:|
| Mean \|ρ\| off-diagonal | 0.270 | 0.233 | 0.272 |
| Max \|ρ\| off-diagonal | 0.360 | 0.498 | 0.757 |

Mean correlation now sits in a sane, similar range across all three N (0.23–0.27) — no more anomaly like the old N=5 (0.53). Max correlation rises sensibly from N=3 to N=9 (0.36 → 0.50 → 0.76): the more lens-angle scenarios compared pairwise, the higher the chance of finding a pair that happens to look very similar to each other (a "birthday-paradox"-like effect from more pairwise comparisons), not because the average itself is rising.

## 4. Random-TX Monte Carlo aggregate summary (section 11)

![Fig. 4 — Monte Carlo aggregate summary](MonteCarlo_Scalability_Analysis_v3_3x3_5x5_9x9/figures/fig4_montecarlo_aggregate_vs_N.png)

| Metric | N=3 | N=5 | N=9 |
|---|---:|---:|---:|
| Median capacity | 5.94 bit/s/Hz | 6.46 bit/s/Hz | 7.67 bit/s/Hz |
| Capacity 5th–95th percentile | 3.00–7.72 | 3.97–8.90 | 5.02–9.68 |
| Median ideal throughput | 2.38 Gbit/s | 2.58 Gbit/s | 3.07 Gbit/s |
| Median RMS delay spread | 59.13 ns | 63.46 ns | 65.00 ns |
| Outage, capacity < 1 bit/s/Hz | 0.0% | 0.0% | 0.0% |

This now rises **cleanly and monotonically** with N across every aggregate metric, matching the basic physical expectation: more TX elements non-coherently summing power at the receiver → higher received SNR → higher equivalent-SISO capacity and ideal throughput. Median capacity rises +29% from N=3 to N=9 (5.94 → 7.67 bit/s/Hz), with N=5 (6.46) sitting proportionally right in between — strong confirmation that this N=5 data is now clean, unlike the earlier bugged run where it fell *below* N=3.

Median RMS delay spread also rises monotonically (59.1 → 63.5 → 65.0 ns), consistent with the TX array aperture growing wider (±0.45 m → ±0.90 m → ±1.80 m), which spreads out the range of path lengths from TX elements to the RX (and to obstacles), widening the delay profile.

## 5. Per-drop virtual-MIMO channel condition (section 11c)

![Fig. 5 — Per-drop distribution](MonteCarlo_Scalability_Analysis_v3_3x3_5x5_9x9/figures/fig5_mimo_per_drop_boxplot_vs_N.png)

| Metric (median over 20 drops) | N=3 | N=5 | N=9 |
|---|---:|---:|---:|
| Condition number | 7.5 (17.5 dB) | 17.1 (24.6 dB) | 54.0 (34.6 dB) |
| Effective rank | 1.91/3 (64%) | 2.77/5 (55%) | 4.07/9 (45%) |
| Capacity @10dB | 8.03 bit/s/Hz | 12.81 bit/s/Hz | 21.11 bit/s/Hz |

This is the most convincing figure in the document: built from 20 raw per-drop rows per N (not just a single summary point), so both the average and the spread are far more robust to sample variance than section 2. **All three metrics show a clean, monotonic trend with N:**

- Median condition number rises monotonically (17.5 → 24.6 → 34.6 dB), with the spread (IQR and whiskers) also widening with N — drop-to-drop variation at N=9 is much wider than at N=3, showing that random TX geometry has a bigger impact on conditioning as the array grows.
- Effective-rank ratio decreases monotonically (64% → 55% → 45%) — a classic diminishing-returns pattern: adding elements doesn't yield independent spatial modes in the same proportion, even though absolute capacity keeps rising.
- Capacity @10dB rises monotonically (8.03 → 12.81 → 21.11 bit/s/Hz).

The N=3 and N=5 boxplots in panel (a) overlap slightly at their whisker tips, but their boxes (IQR) are each clearly separated from N=9 — showing a clear separation especially for a large jump in array size (3→9), and a more gradual one for a small jump (3→5).

## Limitations and caveats

1. **The number of drops (20) and ray samples (100,000) are still the initial settings**, not the final settings recommended by the notebooks (100–500 drops, 1,000,000 samples/source) — this applies equally to all three N, so it does not bias one N over another, but it still limits statistical precision (see the wide whiskers in Fig. 5, drawn from only 20 samples per N).
2. **Compute cost here is purely theoretical** (number of `PathSolver` calls), not a real wall-clock measurement — no timing log is stored in any of the three notebooks to verify how much real-world speed-up the scalability actually delivers.
3. **The lens-angle scenarios differ across N** (3 angles for N=3, 5 for N=5, 9 for N=9, with different angular spacing — 45°, 30°, and 15° respectively) — not an identical subset/superset, so some of the variation could stem from the different angle combinations/spacing, not purely from N. A uniform angle set (e.g., always 0°, ±30°, ±60° across all three N) would make the comparison tighter.
4. **N×N MIMO is virtual/synthetic** (see the physical caveat in each source notebook) — the reported MIMO capacity is not something a single physical RX could realize simultaneously.
5. **Capacity is the ideal Shannon bound**, not accounting for modulation, coding, protocol overhead, or practical channel estimation.
6. **Total transmit power grows with N** (each TX stays at 10 dBm) — the aggregate SISO-capacity comparison across N (section 4) is not a comparison at a fixed total power budget; part of the capacity increase comes from the increase in total transmit power, not purely from the element count.
7. **Section 2 (fixed geometry) is a single sample**, not an average — as discussed in section 2, a single-geometry metric like the effective-rank ratio can deviate from the smoother multi-drop trend in section 5 (Monte Carlo, 20 drops). For scalability claims, section 5 is more reliable than section 2.

## Conclusion

After aligning the data source to the consistent "v3" notebook family for all three N, the scalability comparison is **much cleaner and more trustworthy** than the earlier analysis (which was contaminated by the RX-orientation bug in the v2 N=5 notebook).

On the **compute-cost** side, the "simultaneous TX with one shared pattern" design keeps cost growth **linear in N** (not quadratic) — this is what keeps the N=9 configuration (180 Monte Carlo runs) practical to run at all, versus 1620 runs under a naive one-element-per-run scheme.

On the **channel-performance** side, nearly every metric now rises **cleanly and monotonically** with N: virtual-MIMO capacity, median Monte Carlo aggregate capacity and throughput, and median RMS delay spread. This confirms the basic physical expectation — a larger TX array increases combined received power and system capacity.

However, this scalability is **not free of trade-offs**: virtual-MIMO condition number worsens monotonically with N (both on fixed-geometry and 20-drop-averaged data), and the effective-rank-to-N ratio tends to decrease (most clearly in the Monte Carlo data of section 5, 64% → 55% → 45%) — showing the classic diminishing-returns pattern in MIMO array scaling: adding elements raises absolute capacity, but the proportion of truly independent spatial modes actually shrinks.

**Further recommendations:** (1) increase the number of drops (100–500) and ray samples (1,000,000/source) for better statistical precision on this scalability claim; (2) standardize the lens-angle set tested across all three N so the comparison is not confounded by different angle combinations (caveat #3); (3) add wall-clock timing per `PathSolver` run if a precise (not just run-count) compute-scalability claim is needed; (4) if comparing at a fixed total power budget (rather than fixed power per element) is of interest, reduce power per TX by `10*log10(N)` dB relative to the N=3 baseline.
