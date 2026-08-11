# -*- coding: utf-8 -*-
"""
Analisis skalabilitas metode Monte Carlo (section 11, Random-TX) untuk tiga ukuran
array TX/RX-scenario N=3, 5, 9 -- SEMUA dari notebook "v3" yang konsisten:

  - N=3 : Setupv3_20mx20m_lens_3x3_Patch_randomCom.ipynb
  - N=5 : Setupv3_20mx20m_lens_5x5_Patch_randomCom.ipynb   (v3 -- BUKAN v2)
  - N=9 : Setupv3_20mx20m_lens_9x9_Patch_randomCom.ipynb

Ini adalah versi PERBAIKAN dari analisis sebelumnya (folder
Analisis_Skalabilitas_MonteCarlo_3x3_5x5_9x9/), yang memakai notebook "v2" untuk
N=5 dan ternyata mengandung bug konversi radian ganda pada orientasi RX (lihat
README/README lama). Notebook v3 5x5 di sini memakai literal derajat langsung
untuk `rx_orientation_deg` (sama seperti v3 3x3/9x9), jadi bebas dari bug tsb.

PENTING: notebook TIDAK dieksekusi ulang. Seluruh angka di bawah disalin persis
dari output sel yang sudah tersimpan di ketiga notebook v3 (lihat
data/raw_logs/*.txt untuk teks mentahnya). Script ini murni mengubah angka
tersebut menjadi tabel (CSV) dan grafik (PNG) pembanding.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ---- palette (dataviz skill categorical theme, slots 1/2/3, light mode -- validated) ----
C_SURFACE   = "#fcfcfb"
C_PRIMARY   = "#0b0b0b"
C_SECONDARY = "#52514e"
C_MUTED     = "#898781"
C_GRID      = "#e1e0d9"
C_BASELINE  = "#c3c2b7"
C_N3 = "#2a78d6"   # categorical slot 1 -- N=3
C_N5 = "#eb6834"   # categorical slot 2 -- N=5 (v3, konsisten -- lihat README)
C_N9 = "#1baf7a"   # categorical slot 3 -- N=9

COLORS = {3: C_N3, 5: C_N5, 9: C_N9}

plt.rcParams.update({
    "figure.facecolor": C_SURFACE, "axes.facecolor": C_SURFACE, "savefig.facecolor": C_SURFACE,
    "font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
    "text.color": C_PRIMARY, "axes.edgecolor": C_BASELINE, "axes.labelcolor": C_SECONDARY,
    "axes.titlecolor": C_PRIMARY, "xtick.color": C_MUTED, "ytick.color": C_MUTED,
    "grid.color": C_GRID, "axes.grid": True, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "font.size": 10.5,
})

DATA = "../data"
FIG = "../figures"


def style_ax(ax, grid_axis="y"):
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(C_BASELINE)
    ax.grid(axis=grid_axis, alpha=0.6)
    ax.set_axisbelow(True)


# ============================================================
# 1. Data mentah (disalin dari data/raw_logs/*_key_cells_output.txt)
# ============================================================

# -- Section 8/10 (geometri TX tetap): evaluasi MIMO virtual N x N --
mimo_fixed = pd.DataFrame([
    dict(N=3, cond_median=3.8, cond_median_db=11.7, erank_median=1.61, capacity_10db=7.87),
    dict(N=5, cond_median=5.7, cond_median_db=15.1, erank_median=3.39, capacity_10db=14.24),
    dict(N=9, cond_median=86.7, cond_median_db=38.8, erank_median=4.25, capacity_10db=21.66),
])
mimo_fixed["erank_ratio_pct"] = mimo_fixed["erank_median"] / mimo_fixed["N"] * 100

# -- Section 10b: korelasi spasial sisi-RX (dari kombinasi N skenario lensa) --
rx_corr = pd.DataFrame([
    dict(N=3, mean_abs_rho=0.2700, max_abs_rho=0.3597),
    dict(N=5, mean_abs_rho=0.2334, max_abs_rho=0.4980),
    dict(N=9, mean_abs_rho=0.2721, max_abs_rho=0.7566),
])

# -- Section 9: kapasitas MRT & combined gain terbaik per skenario (geometri tetap) --
best_scn = pd.DataFrame([
    dict(N=3, best_combined_gain_db=-42.2, capacity_10db_mrt=3.459),
    dict(N=5, best_combined_gain_db=-42.2, capacity_10db_mrt=3.459),
    dict(N=9, best_combined_gain_db=-42.2, capacity_10db_mrt=3.459),
])

# -- Section 11: ringkasan agregat Monte Carlo (gabungan seluruh skenario RX) --
mc_summary = pd.DataFrame([
    dict(N=3, drops=20, total_runs=60, capacity_median=5.94, capacity_p05=3.00, capacity_p95=7.72,
         throughput_median_gbps=2.38, delay_spread_median_ns=59.13, outage_pct=0.0),
    dict(N=5, drops=20, total_runs=100, capacity_median=6.46, capacity_p05=3.97, capacity_p95=8.90,
         throughput_median_gbps=2.58, delay_spread_median_ns=63.46, outage_pct=0.0),
    dict(N=9, drops=20, total_runs=180, capacity_median=7.67, capacity_p05=5.02, capacity_p95=9.68,
         throughput_median_gbps=3.07, delay_spread_median_ns=65.00, outage_pct=0.0),
])

# -- Section 11c: ringkasan MIMO virtual per-drop (median atas 20 drop) --
mc_mimo_summary = pd.DataFrame([
    dict(N=3, cond_median=7.5, cond_median_db=17.5, cond_p05_db=8.9, cond_p95_db=26.6,
         erank_median=1.91, capacity_10db_median=8.03),
    dict(N=5, cond_median=17.1, cond_median_db=24.6, cond_p05_db=19.4, cond_p95_db=32.1,
         erank_median=2.77, capacity_10db_median=12.81),
    dict(N=9, cond_median=54.0, cond_median_db=34.6, cond_p05_db=29.4, cond_p95_db=40.6,
         erank_median=4.07, capacity_10db_median=21.11),
])
mc_mimo_summary["erank_ratio_pct"] = mc_mimo_summary["erank_median"] / mc_mimo_summary["N"] * 100

# -- Section 11c: 20 baris mentah per-drop (SVD kondisi kanal), disalin verbatim --
per_drop_3x3 = pd.DataFrame({
    "drop": range(20),
    "cond_median": [5.614554, 47.359507, 6.679171, 2.723774, 10.430168, 3.207719, 8.502340,
                    10.178578, 4.099768, 5.976525, 8.336039, 2.773531, 3.910407, 18.480723,
                    10.211499, 3.929194, 4.634246, 19.907837, 9.735358, 10.546754],
    "cond_median_db": [14.986306, 33.508143, 16.494451, 8.703420, 20.365826, 10.123926, 18.590769,
                       20.153742, 12.255185, 15.528974, 18.419194, 8.860659, 11.844440, 25.334379,
                       20.181790, 11.886070, 13.319582, 25.980482, 19.767039, 20.462377],
    "erank_median": [1.849163, 1.170168, 1.669664, 2.267442, 1.423794, 2.193106, 1.868969,
                     1.943281, 2.062271, 2.049612, 1.843007, 2.377759, 2.066256, 1.151376,
                     1.764466, 2.093591, 1.983869, 1.694824, 1.987682, 1.440816],
    "capacity_10db": [8.036146, 5.904545, 7.794513, 9.257696, 6.923503, 8.935914, 7.899759,
                      8.025299, 8.660684, 8.417321, 7.786162, 9.300830, 8.677340, 5.861637,
                      7.788671, 8.574350, 8.464852, 7.581847, 8.080320, 6.948955],
})

per_drop_5x5 = pd.DataFrame({
    "drop": range(20),
    "cond_median": [16.705011, 53.031558, 30.403171, 14.220766, 17.460318, 23.606284, 13.245332,
                    5.639657, 39.512727, 11.687142, 21.657047, 15.725244, 22.337769, 9.476096,
                    22.786496, 12.822067, 15.135275, 15.877880, 28.408083, 24.694127],
    "cond_median_db": [24.456935, 34.490688, 29.658378, 23.058460, 24.841043, 27.460553, 22.441257,
                       15.025054, 31.934740, 21.354166, 26.711985, 23.931948, 26.980796, 19.532589,
                       27.153551, 22.159161, 23.599806, 24.015850, 29.068839, 27.851874],
    "erank_median": [2.639223, 1.554712, 1.957915, 3.113829, 2.850481, 1.738099, 3.188311,
                     3.408017, 2.011245, 2.999209, 2.826695, 2.708704, 1.829691, 2.515734,
                     2.516489, 3.462028, 3.274889, 3.026223, 2.661111, 2.971865],
    "capacity_10db": [12.877628, 9.402682, 10.567950, 13.510842, 12.908906, 10.138351, 13.789251,
                      14.514124, 10.988956, 13.385111, 12.895609, 12.636609, 10.638084, 12.702362,
                      12.420956, 14.279155, 13.878848, 13.264977, 12.209444, 12.738143],
})

per_drop_9x9 = pd.DataFrame({
    "drop": range(20),
    "cond_median": [102.504814, 58.677116, 31.079870, 49.321808, 88.962949, 29.636329, 27.835605,
                    42.007108, 29.570931, 32.630327, 67.981466, 191.115936, 54.459033, 59.080725,
                    53.542369, 35.375819, 66.634376, 72.219433, 75.824872, 36.703127],
    "cond_median_db": [40.214885, 35.369375, 29.849584, 33.860780, 38.984183, 29.436488, 28.892013,
                       32.466456, 29.417300, 30.272429, 36.647811, 45.625938, 34.721399, 35.428916,
                       34.573952, 30.974130, 36.473967, 37.173081, 37.596234, 31.294061],
    "erank_median": [2.102429, 3.854705, 4.779534, 4.052973, 3.075012, 5.170830, 4.911908,
                     4.161029, 4.671378, 4.595243, 4.073347, 1.357218, 4.316185, 3.381483,
                     3.804882, 4.490692, 4.072262, 2.833265, 3.591539, 4.442494],
    "capacity_10db": [15.305732, 20.440963, 22.417293, 21.543840, 19.201188, 23.610169, 22.938540,
                      21.178098, 22.634780, 22.546315, 20.519151, 10.986784, 21.587283, 19.328334,
                      20.115246, 22.742015, 21.041830, 18.602197, 19.937936, 22.076935],
})
for df, N in ((per_drop_3x3, 3), (per_drop_5x5, 5), (per_drop_9x9, 9)):
    df["N"] = N
    df["erank_ratio_pct"] = df["erank_median"] / N * 100

per_drop_all = pd.concat([per_drop_3x3, per_drop_5x5, per_drop_9x9], ignore_index=True)

# -- Section 11: tabel per-skenario-RX Monte Carlo (median/p05/p95 kapasitas) --
mc_per_scenario = pd.DataFrame([
    # N=3
    dict(N=3, rx_lens_angle_deg=45, capacity_median=5.380282, capacity_p05=2.907510, capacity_p95=7.297654, snr_median_db=16.590826),
    dict(N=3, rx_lens_angle_deg=0, capacity_median=6.433945, capacity_p05=2.984139, capacity_p95=7.665920, snr_median_db=19.562149),
    dict(N=3, rx_lens_angle_deg=-45, capacity_median=5.784050, capacity_p05=3.716327, capacity_p95=8.503910, snr_median_db=17.895313),
    # N=5 (v3)
    dict(N=5, rx_lens_angle_deg=60, capacity_median=5.702155, capacity_p05=3.561451, capacity_p95=8.138091, snr_median_db=17.481945),
    dict(N=5, rx_lens_angle_deg=30, capacity_median=6.310228, capacity_p05=4.333645, capacity_p95=8.212238, snr_median_db=19.090183),
    dict(N=5, rx_lens_angle_deg=0, capacity_median=6.957178, capacity_p05=5.174754, capacity_p95=8.857847, snr_median_db=21.058067),
    dict(N=5, rx_lens_angle_deg=-30, capacity_median=7.278836, capacity_p05=5.451078, capacity_p95=9.517728, snr_median_db=21.945515),
    dict(N=5, rx_lens_angle_deg=-60, capacity_median=5.934236, capacity_p05=3.707421, capacity_p95=8.425823, snr_median_db=18.088249),
    # N=9
    dict(N=9, rx_lens_angle_deg=60, capacity_median=6.697347, capacity_p05=4.890896, capacity_p95=9.537766, snr_median_db=20.413094),
    dict(N=9, rx_lens_angle_deg=45, capacity_median=7.487707, capacity_p05=5.154093, capacity_p95=9.749459, snr_median_db=22.607607),
    dict(N=9, rx_lens_angle_deg=30, capacity_median=7.294540, capacity_p05=4.663241, capacity_p95=9.335979, snr_median_db=22.068260),
    dict(N=9, rx_lens_angle_deg=15, capacity_median=8.020621, capacity_p05=5.182103, capacity_p95=10.348151, snr_median_db=24.180822),
    dict(N=9, rx_lens_angle_deg=0, capacity_median=7.683814, capacity_p05=6.783537, capacity_p95=11.628092, snr_median_db=23.220303),
    dict(N=9, rx_lens_angle_deg=-15, capacity_median=8.283607, capacity_p05=6.217029, capacity_p95=9.714041, snr_median_db=24.991531),
    dict(N=9, rx_lens_angle_deg=-30, capacity_median=8.317599, capacity_p05=6.890205, capacity_p95=9.607496, snr_median_db=25.081303),
    dict(N=9, rx_lens_angle_deg=-45, capacity_median=8.127462, capacity_p05=6.238897, capacity_p95=9.356546, snr_median_db=24.498154),
    dict(N=9, rx_lens_angle_deg=-60, capacity_median=7.433225, capacity_p05=4.926395, capacity_p95=8.971201, snr_median_db=22.528591),
])

# -- Biaya komputasi: jumlah pemanggilan PathSolver, teoretis (bukan hasil ukur waktu) --
compute_cost = pd.DataFrame([
    dict(N=3, main_loop_actual=3, main_loop_naive_per_element=3 ** 2,
         mc_drops=20, mc_runs_total=60, mc_runs_naive_per_element=20 * 3 ** 2),
    dict(N=5, main_loop_actual=5, main_loop_naive_per_element=5 ** 2,
         mc_drops=20, mc_runs_total=100, mc_runs_naive_per_element=20 * 5 ** 2),
    dict(N=9, main_loop_actual=9, main_loop_naive_per_element=9 ** 2,
         mc_drops=20, mc_runs_total=180, mc_runs_naive_per_element=20 * 9 ** 2),
])

# ============================================================
# 2. Simpan seluruh tabel ke CSV
# ============================================================
mimo_fixed.to_csv(f"{DATA}/mimo_fixed_geometry_by_N.csv", index=False)
rx_corr.to_csv(f"{DATA}/rx_spatial_correlation_by_N.csv", index=False)
best_scn.to_csv(f"{DATA}/best_scenario_fixed_geometry_by_N.csv", index=False)
mc_summary.to_csv(f"{DATA}/montecarlo_aggregate_by_N.csv", index=False)
mc_mimo_summary.to_csv(f"{DATA}/montecarlo_mimo_per_drop_summary_by_N.csv", index=False)
per_drop_all.to_csv(f"{DATA}/montecarlo_mimo_per_drop_raw_N3_N5_N9.csv", index=False)
mc_per_scenario.to_csv(f"{DATA}/montecarlo_per_rx_scenario_by_N.csv", index=False)
compute_cost.to_csv(f"{DATA}/compute_cost_by_N.csv", index=False)
print("CSV tersimpan di", DATA)

Ns = [3, 5, 9]
bar_x = np.arange(len(Ns))


# ============================================================
# Fig 1 -- skalabilitas biaya komputasi (jumlah pemanggilan PathSolver)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))

legend_actual_naive = [
    Patch(facecolor=C_SECONDARY, label="Aktual (warna batang = N, lihat Fig. 2)"),
    Patch(facecolor=C_BASELINE, label="Naif (1 elemen TX / run)"),
]

ax = axes[0]
w = 0.35
actual = compute_cost["main_loop_actual"].values
naive = compute_cost["main_loop_naive_per_element"].values
ax.bar(bar_x - w / 2, actual, width=w, color=[COLORS[n] for n in Ns])
ax.bar(bar_x + w / 2, naive, width=w, color=C_BASELINE)
for x, v in zip(bar_x - w / 2, actual):
    ax.text(x, v + 1.5, f"{v:.0f}", ha="center", fontsize=9, color=C_PRIMARY)
for x, v in zip(bar_x + w / 2, naive):
    ax.text(x, v + 1.5, f"{v:.0f}", ha="center", fontsize=9, color=C_SECONDARY)
ax.set_xticks(bar_x); ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("Jumlah panggilan PathSolver")
ax.set_title("Loop utama (geometri tetap, sec. 8)", loc="left", fontsize=10.5, fontweight="bold")
ax.legend(handles=legend_actual_naive, frameon=False, fontsize=7.5, loc="upper left")
style_ax(ax)

ax = axes[1]
mc_actual = compute_cost["mc_runs_total"].values
mc_naive = compute_cost["mc_runs_naive_per_element"].values
ax.bar(bar_x - w / 2, mc_actual, width=w, color=[COLORS[n] for n in Ns])
ax.bar(bar_x + w / 2, mc_naive, width=w, color=C_BASELINE)
for x, v in zip(bar_x - w / 2, mc_actual):
    ax.text(x, v + 15, f"{v:.0f}", ha="center", fontsize=9, color=C_PRIMARY)
for x, v in zip(bar_x + w / 2, mc_naive):
    ax.text(x, v + 15, f"{v:.0f}", ha="center", fontsize=9, color=C_SECONDARY)
ax.set_xticks(bar_x); ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("Jumlah panggilan PathSolver")
ax.set_title("Monte Carlo Random-TX (sec. 11)", loc="left", fontsize=10.5, fontweight="bold")
ax.legend(handles=[Patch(facecolor=C_SECONDARY, label="Aktual (warna batang = N)"),
                    Patch(facecolor=C_BASELINE, label="Naif (20 drop x N²)")],
          frameon=False, fontsize=7.5, loc="upper left")
style_ax(ax)

fig.suptitle("Fig. 1 — Skalabilitas biaya komputasi vs ukuran array N", fontsize=12, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(f"{FIG}/fig1_compute_cost_scalability.png", dpi=150, bbox_inches="tight")
plt.close(fig)


# ============================================================
# Fig 2 -- MIMO virtual geometri tetap (sec. 10) vs N
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))

ax = axes[0]
vals = mimo_fixed["cond_median_db"].values
ax.bar(bar_x, vals, color=[COLORS[n] for n in Ns], width=0.55)
for x, v in zip(bar_x, vals):
    ax.text(x, v + 0.8, f"{v:.1f} dB", ha="center", fontsize=9)
ax.set_xticks(bar_x); ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("Condition number median (dB)")
ax.set_title("(a) Condition number", loc="left", fontsize=10.5, fontweight="bold")
style_ax(ax)

ax = axes[1]
vals = mimo_fixed["erank_ratio_pct"].values
ax.bar(bar_x, vals, color=[COLORS[n] for n in Ns], width=0.55)
for x, v, n in zip(bar_x, vals, Ns):
    erv = mimo_fixed.loc[mimo_fixed.N == n, "erank_median"].iloc[0]
    ax.text(x, v + 1.2, f"{erv:.2f}/{n}\n({v:.0f}%)", ha="center", fontsize=8.5)
ax.set_xticks(bar_x); ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("Effective rank / N (%)")
ax.set_ylim(0, 80)
ax.set_title("(b) Effective rank (rasio)", loc="left", fontsize=10.5, fontweight="bold")
style_ax(ax)

ax = axes[2]
vals = mimo_fixed["capacity_10db"].values
ax.bar(bar_x, vals, color=[COLORS[n] for n in Ns], width=0.55)
for x, v in zip(bar_x, vals):
    ax.text(x, v + 0.5, f"{v:.1f}", ha="center", fontsize=9)
ax.set_xticks(bar_x); ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("Kapasitas @ 10 dB (bit/s/Hz)")
ax.set_title("(c) Kapasitas MIMO @10dB", loc="left", fontsize=10.5, fontweight="bold")
style_ax(ax)

fig.suptitle("Fig. 2 — MIMO virtual N×N, geometri TX tetap (sec. 10) vs N", fontsize=12, fontweight="bold", y=1.03)
fig.tight_layout()
fig.savefig(f"{FIG}/fig2_mimo_fixed_geometry_vs_N.png", dpi=150, bbox_inches="tight")
plt.close(fig)


# ============================================================
# Fig 3 -- korelasi spasial sisi-RX (sec. 10b) vs N
# ============================================================
fig, ax = plt.subplots(figsize=(6.5, 4.6))
w = 0.35
mean_v = rx_corr["mean_abs_rho"].values
max_v = rx_corr["max_abs_rho"].values
ax.bar(bar_x - w / 2, mean_v, width=w, color=[COLORS[n] for n in Ns])
ax.bar(bar_x + w / 2, max_v, width=w, color=[COLORS[n] for n in Ns], alpha=0.45)
for x, v in zip(bar_x - w / 2, mean_v):
    ax.text(x, v + 0.015, f"{v:.2f}", ha="center", fontsize=8.5)
for x, v in zip(bar_x + w / 2, max_v):
    ax.text(x, v + 0.015, f"{v:.2f}", ha="center", fontsize=8.5)
ax.set_xticks(bar_x); ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("|ρ| off-diagonal")
ax.set_ylim(0, 0.9)
ax.legend(handles=[Patch(facecolor=C_SECONDARY, label="Mean |ρ| off-diagonal"),
                    Patch(facecolor=C_SECONDARY, alpha=0.45, label="Max |ρ| off-diagonal")],
          frameon=False, fontsize=8.5, loc="upper left")
ax.set_title("Fig. 3 — Korelasi spasial sisi-RX (sec. 10b) vs N", loc="left", fontsize=11, fontweight="bold")
style_ax(ax)
fig.tight_layout()
fig.savefig(f"{FIG}/fig3_rx_correlation_vs_N.png", dpi=150, bbox_inches="tight")
plt.close(fig)


# ============================================================
# Fig 4 -- Monte Carlo agregat (sec. 11) vs N: kapasitas, throughput, delay spread
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))

ax = axes[0]
med = mc_summary["capacity_median"].values
p05 = mc_summary["capacity_p05"].values
p95 = mc_summary["capacity_p95"].values
yerr = np.vstack([med - p05, p95 - med])
ax.bar(bar_x, med, color=[COLORS[n] for n in Ns], width=0.55, zorder=3)
ax.errorbar(bar_x, med, yerr=yerr, fmt="none", ecolor=C_PRIMARY, elinewidth=1.3, capsize=4, zorder=4)
for x, v in zip(bar_x, med):
    ax.text(x, v + 0.35, f"{v:.2f}", ha="center", fontsize=9, zorder=5)
ax.set_xticks(bar_x); ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("Kapasitas SISO ekuivalen (bit/s/Hz)")
ax.set_title("(a) Median kapasitas (bar p05–p95)", loc="left", fontsize=10, fontweight="bold")
style_ax(ax)

ax = axes[1]
vals = mc_summary["throughput_median_gbps"].values
ax.bar(bar_x, vals, color=[COLORS[n] for n in Ns], width=0.55)
for x, v in zip(bar_x, vals):
    ax.text(x, v + 0.05, f"{v:.2f}", ha="center", fontsize=9)
ax.set_xticks(bar_x); ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("Throughput ideal median (Gbit/s)")
ax.set_title("(b) Median throughput ideal", loc="left", fontsize=10, fontweight="bold")
style_ax(ax)

ax = axes[2]
vals = mc_summary["delay_spread_median_ns"].values
ax.bar(bar_x, vals, color=[COLORS[n] for n in Ns], width=0.55)
for x, v in zip(bar_x, vals):
    ax.text(x, v + 1, f"{v:.1f}", ha="center", fontsize=9)
ax.set_xticks(bar_x); ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("RMS delay spread median (ns)")
ax.set_title("(c) Median RMS delay spread", loc="left", fontsize=10, fontweight="bold")
style_ax(ax)

fig.suptitle("Fig. 4 — Ringkasan agregat Monte Carlo Random-TX (sec. 11) vs N", fontsize=12, fontweight="bold", y=1.03)
fig.tight_layout()
fig.savefig(f"{FIG}/fig4_montecarlo_aggregate_vs_N.png", dpi=150, bbox_inches="tight")
plt.close(fig)


# ============================================================
# Fig 5 -- distribusi per-drop (boxplot, 20 drop asli) sec. 11c: condition number & effective rank
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))

ax = axes[0]
data = [per_drop_all.loc[per_drop_all.N == n, "cond_median_db"].values for n in Ns]
bp = ax.boxplot(data, patch_artist=True, widths=0.5, medianprops=dict(color=C_PRIMARY, linewidth=1.6))
for patch, n in zip(bp["boxes"], Ns):
    patch.set_facecolor(COLORS[n]); patch.set_alpha(0.75); patch.set_edgecolor(C_PRIMARY)
ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("Condition number per-drop (dB)")
ax.set_title("(a) Sebaran condition number, 20 drop", loc="left", fontsize=10.5, fontweight="bold")
style_ax(ax)

ax = axes[1]
data = [per_drop_all.loc[per_drop_all.N == n, "erank_ratio_pct"].values for n in Ns]
bp = ax.boxplot(data, patch_artist=True, widths=0.5, medianprops=dict(color=C_PRIMARY, linewidth=1.6))
for patch, n in zip(bp["boxes"], Ns):
    patch.set_facecolor(COLORS[n]); patch.set_alpha(0.75); patch.set_edgecolor(C_PRIMARY)
ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("Effective rank / N (%)")
ax.set_title("(b) Sebaran effective rank (rasio), 20 drop", loc="left", fontsize=10.5, fontweight="bold")
style_ax(ax)

fig.suptitle("Fig. 5 — Sebaran kondisi kanal MIMO virtual per-drop (sec. 11c) vs N", fontsize=12, fontweight="bold", y=1.03)
fig.tight_layout()
fig.savefig(f"{FIG}/fig5_mimo_per_drop_boxplot_vs_N.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("Semua figure tersimpan di", FIG)
