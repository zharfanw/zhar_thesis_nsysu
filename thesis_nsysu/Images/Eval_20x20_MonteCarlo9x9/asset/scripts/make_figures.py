import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ---- palette (dataviz skill reference palette, light mode) ----
C_SURFACE   = "#fcfcfb"
C_PRIMARY   = "#0b0b0b"
C_SECONDARY = "#52514e"
C_MUTED     = "#898781"
C_GRID      = "#e1e0d9"
C_BASELINE  = "#c3c2b7"
C_BLUE      = "#2a78d6"   # categorical slot 1 -- "without lens"
C_ORANGE    = "#eb6834"   # categorical slot 2 -- "with lens"
C_RED       = "#e34948"   # diverging pole (negative)
C_GOOD      = "#0ca30c"   # status good (paired win-rate marker only)

plt.rcParams.update({
    "figure.facecolor": C_SURFACE,
    "axes.facecolor": C_SURFACE,
    "savefig.facecolor": C_SURFACE,
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
    "text.color": C_PRIMARY,
    "axes.edgecolor": C_BASELINE,
    "axes.labelcolor": C_SECONDARY,
    "axes.titlecolor": C_PRIMARY,
    "xtick.color": C_MUTED,
    "ytick.color": C_MUTED,
    "grid.color": C_GRID,
    "axes.grid": True,
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "font.size": 10.5,
})

DATA = "asset/data"
OUT = "asset/figures"

wolens = pd.read_csv(f"{DATA}/wolens_per_drop_rx.csv")
lens = pd.read_csv(f"{DATA}/lens_per_drop_rx.csv")
per_rx_wolens = pd.read_csv(f"{DATA}/wolens_per_rx_summary.csv")
per_rx_lens = pd.read_csv(f"{DATA}/lens_per_rx_summary.csv")
mimo_wolens = pd.read_csv(f"{DATA}/wolens_mimo_per_drop.csv")
mimo_lens = pd.read_csv(f"{DATA}/lens_mimo_per_drop.csv")
paired = pd.read_csv(f"{DATA}/paired_diff_per_drop_rx.csv")

ANGLES = [60, 45, 30, 15, 0, -15, -30, -45, -60]


def style_ax(ax):
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(C_BASELINE)
    ax.grid(axis="y", alpha=0.6)
    ax.set_axisbelow(True)


# ============================================================
# Figure 0a / 0b -- standalone (single-scenario) results, one per
# notebook, BEFORE the two scenarios are combined for comparison.
# ============================================================
def plot_individual_scenario(df, per_rx, mimo_df, color, label, tag, fig_no):
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 8.6))

    # (a) capacity distribution -- histogram + median/p05/p95 markers
    ax = axes[0, 0]
    vals = df["capacity_bits_s_hz"].values
    med, p05, p95 = np.median(vals), np.percentile(vals, 5), np.percentile(vals, 95)
    ax.hist(vals, bins=20, color=color, alpha=0.85, edgecolor=C_SURFACE, linewidth=0.6)
    ax.axvline(med, color=C_PRIMARY, linewidth=1.6, label=f"median {med:.2f}")
    ax.axvline(p05, color=C_MUTED, linewidth=1.0, linestyle=(0, (3, 3)), label=f"p05 {p05:.2f}")
    ax.axvline(p95, color=C_MUTED, linewidth=1.0, linestyle=(0, (3, 3)), label=f"p95 {p95:.2f}")
    ax.set_xlabel("Capacity (bit/s/Hz)")
    ax.set_ylabel("Count (of 180 drop x angle)")
    ax.set_title("Capacity distribution", loc="left", fontsize=10.5, fontweight="bold")
    ax.legend(frameon=False, fontsize=7.5, loc="upper right")
    style_ax(ax)

    # (b) capacity vs angle, median +- 5-95%
    ax = axes[0, 1]
    d = per_rx.sort_values("rx_lens_angle_deg", ascending=False)
    ax.plot(d["rx_lens_angle_deg"], d["capacity_median"], marker="o", ms=6,
            color=color, linewidth=2.2, zorder=3)
    ax.fill_between(d["rx_lens_angle_deg"], d["capacity_p05"], d["capacity_p95"],
                     color=color, alpha=0.15, zorder=1)
    ax.set_xticks(ANGLES)
    ax.invert_xaxis()
    ax.set_xlabel("RX lens angle (deg)")
    ax.set_ylabel("Capacity (bit/s/Hz)")
    ax.set_title("Capacity per RX angle", loc="left", fontsize=10.5, fontweight="bold")
    style_ax(ax)

    # (c) RMS delay spread vs angle (median)
    ax = axes[0, 2]
    ds = df.groupby("rx_lens_angle_deg")["rms_delay_spread_ns"].median().reindex(ANGLES)
    ax.plot(ANGLES, ds.values, marker="o", ms=6, color=color, linewidth=2.2)
    ax.set_xticks(ANGLES)
    ax.invert_xaxis()
    ax.set_xlabel("RX lens angle (deg)")
    ax.set_ylabel("Median RMS delay spread (ns)")
    ax.set_title("Delay spread per RX angle", loc="left", fontsize=10.5, fontweight="bold")
    style_ax(ax)

    # (d)-(f) virtual 9x9 MIMO conditioning across the 20 drops (this scenario only)
    mimo_specs = [
        ("cond_median_db", "Condition number (dB)", "Condition number"),
        ("erank_median", "Effective rank (of 9)", "Effective rank"),
        ("capacity_10db", "Capacity @ 10 dB SNR (bit/s/Hz)", "Virtual 9x9 MIMO capacity"),
    ]
    for col_ax, (col, ylabel, title) in zip(axes[1, :], mimo_specs):
        bp = col_ax.boxplot([mimo_df[col]], patch_artist=True, widths=0.4,
                             medianprops=dict(color=C_PRIMARY, linewidth=1.6))
        bp["boxes"][0].set_facecolor(color)
        bp["boxes"][0].set_alpha(0.85)
        bp["boxes"][0].set_edgecolor(color)
        col_ax.set_xticklabels([label])
        col_ax.set_ylabel(ylabel)
        col_ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold")
        style_ax(col_ax)
    axes[1, 1].axhline(9, color=C_MUTED, linewidth=0.8, linestyle=(0, (2, 2)))
    axes[1, 1].annotate("9 = full rank", xy=(1.15, 9), fontsize=8, color=C_MUTED)

    fig.suptitle(f"Fig. {fig_no} -- Standalone results, {label} (20 drops x 9 angles = 180 rows; "
                 f"not yet compared to the other scenario)",
                 x=0.02, ha="left", fontsize=12.5, fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig0{tag}_{label.lower().replace(' ', '_')}_individual.png",
                dpi=200, bbox_inches="tight")
    plt.close(fig)


plot_individual_scenario(wolens, per_rx_wolens, mimo_wolens, C_BLUE, "Without lens", "a", "0a")
plot_individual_scenario(lens, per_rx_lens, mimo_lens, C_ORANGE, "With lens", "b", "0b")


# ============================================================
# Figure 1 -- aggregate capacity: box + empirical CDF
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))

ax = axes[0]
bp = ax.boxplot(
    [wolens["capacity_bits_s_hz"], lens["capacity_bits_s_hz"]],
    patch_artist=True, widths=0.5, showfliers=True,
    medianprops=dict(color=C_PRIMARY, linewidth=1.6),
    flierprops=dict(marker="o", markersize=3, markerfacecolor=C_MUTED,
                     markeredgecolor="none", alpha=0.5),
)
for patch, c in zip(bp["boxes"], [C_BLUE, C_ORANGE]):
    patch.set_facecolor(c)
    patch.set_alpha(0.85)
    patch.set_edgecolor(c)
ax.set_xticklabels(["Without lens\n(n=180)", "With lens\n(n=180)"])
ax.set_ylabel("Capacity (bit/s/Hz)")
ax.set_title("Aggregate capacity distribution", loc="left", fontsize=11, fontweight="bold")
style_ax(ax)

ax = axes[1]
for series, color, label in [
    (wolens["capacity_bits_s_hz"], C_BLUE, "Without lens"),
    (lens["capacity_bits_s_hz"], C_ORANGE, "With lens"),
]:
    vals = np.sort(series.values)
    y = np.arange(1, len(vals) + 1) / len(vals)
    ax.plot(vals, y, color=color, linewidth=2, label=label)
ax.axhline(0.5, color=C_BASELINE, linewidth=0.8, linestyle=(0, (3, 3)))
ax.axhline(0.05, color=C_BASELINE, linewidth=0.8, linestyle=(0, (1, 2)))
ax.set_xlabel("Capacity (bit/s/Hz)")
ax.set_ylabel("Empirical CDF")
ax.set_title("Capacity CDF (all drops x angles)", loc="left", fontsize=11, fontweight="bold")
ax.legend(frameon=False, loc="lower right", fontsize=9)
style_ax(ax)

fig.suptitle("Fig. 1 -- Aggregate SISO capacity: without lens vs with lens",
             x=0.02, ha="left", fontsize=12.5, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(f"{OUT}/fig1_capacity_aggregate.png", dpi=200, bbox_inches="tight")
plt.close(fig)


# ============================================================
# Figure 2 -- median capacity vs RX angle, with 5-95% band
# ============================================================
fig, ax = plt.subplots(figsize=(8.5, 5.2))

for df_rx, color, label in [
    (per_rx_wolens, C_BLUE, "Without lens"),
    (per_rx_lens, C_ORANGE, "With lens"),
]:
    d = df_rx.sort_values("rx_lens_angle_deg", ascending=False)
    ax.plot(d["rx_lens_angle_deg"], d["capacity_median"], marker="o", ms=6,
            color=color, linewidth=2.2, label=label, zorder=3)
    ax.fill_between(d["rx_lens_angle_deg"], d["capacity_p05"], d["capacity_p95"],
                     color=color, alpha=0.15, zorder=1)

best = per_rx_lens.loc[per_rx_lens["capacity_median"].idxmax()]
ax.annotate(f"best: {best['rx_lens_angle_deg']:+.0f} deg\n{best['capacity_median']:.2f} bit/s/Hz",
            xy=(best["rx_lens_angle_deg"], best["capacity_median"]),
            xytext=(best["rx_lens_angle_deg"] - 28, best["capacity_median"] + 1.0),
            fontsize=8.5, color=C_SECONDARY,
            arrowprops=dict(arrowstyle="-", color=C_MUTED, lw=0.8))

worst = per_rx_lens.loc[per_rx_lens["capacity_median"].idxmin()]
ax.annotate(f"weakest: {worst['rx_lens_angle_deg']:+.0f} deg\n{worst['capacity_median']:.2f} bit/s/Hz",
            xy=(worst["rx_lens_angle_deg"], worst["capacity_median"]),
            xytext=(worst["rx_lens_angle_deg"] + 4, worst["capacity_median"] - 2.0),
            fontsize=8.5, color=C_SECONDARY,
            arrowprops=dict(arrowstyle="-", color=C_MUTED, lw=0.8))

ax.set_xticks(ANGLES)
ax.set_xlabel("RX lens angle (deg)")
ax.set_ylabel("Capacity (bit/s/Hz)")
ax.set_title("Fig. 2 -- Median capacity per RX angle (shaded band = 5th-95th percentile)",
             loc="left", fontsize=11.5, fontweight="bold")
ax.legend(frameon=False, loc="upper center", ncol=2, fontsize=9.5)
ax.invert_xaxis()
style_ax(ax)
fig.tight_layout()
fig.savefig(f"{OUT}/fig2_capacity_vs_angle.png", dpi=200, bbox_inches="tight")
plt.close(fig)


# ============================================================
# Figure 3 -- paired per-drop capacity difference (lens - no lens), by angle
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.35, 1]})

ax = axes[0]
g = paired.groupby("rx_lens_angle_deg")["capacity_diff"].median().reindex(ANGLES)
colors = [C_BLUE if v >= 0 else C_RED for v in g.values]
bars = ax.bar([str(a) for a in ANGLES], g.values, color=colors, width=0.62, zorder=3)
ax.axhline(0, color=C_BASELINE, linewidth=1.0)
for rect, v in zip(bars, g.values):
    ax.annotate(f"{v:+.2f}", (rect.get_x() + rect.get_width() / 2, v),
                textcoords="offset points", xytext=(0, 4 if v >= 0 else -12),
                ha="center", fontsize=8, color=C_SECONDARY)
ax.set_xlabel("RX lens angle (deg)")
ax.set_ylabel("Median paired capacity diff (bit/s/Hz)")
ax.set_title("Median (lens - no lens) per angle, paired by identical TX geometry",
             loc="left", fontsize=10.5, fontweight="bold")
style_ax(ax)

ax = axes[1]
win_rate = paired.groupby("rx_lens_angle_deg").apply(
    lambda s: (s["capacity_diff"] > 0).mean() * 100).reindex(ANGLES)
bars = ax.bar([str(a) for a in ANGLES], win_rate.values, color=C_ORANGE, alpha=0.85, width=0.62, zorder=3)
ax.axhline(50, color=C_BASELINE, linewidth=1.0, linestyle=(0, (3, 3)))
ax.set_ylim(0, 100)
ax.set_xlabel("RX lens angle (deg)")
ax.set_ylabel("Drops where lens wins (%)")
ax.set_title("Lens win-rate per angle (of 20 paired drops)", loc="left", fontsize=10.5, fontweight="bold")
for rect, v in zip(bars, win_rate.values):
    ax.annotate(f"{v:.0f}%", (rect.get_x() + rect.get_width() / 2, v),
                textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8, color=C_SECONDARY)
style_ax(ax)

fig.suptitle("Fig. 3 -- Paired per-drop capacity difference (180 identical-TX pairs)",
             x=0.02, ha="left", fontsize=12.5, fontweight="bold", y=1.03)
fig.tight_layout()
fig.savefig(f"{OUT}/fig3_paired_diff_by_angle.png", dpi=200, bbox_inches="tight")
plt.close(fig)


# ============================================================
# Figure 4 -- RMS delay spread comparison
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))

ax = axes[0]
bp = ax.boxplot(
    [wolens["rms_delay_spread_ns"], lens["rms_delay_spread_ns"]],
    patch_artist=True, widths=0.5, showfliers=True,
    medianprops=dict(color=C_PRIMARY, linewidth=1.6),
    flierprops=dict(marker="o", markersize=3, markerfacecolor=C_MUTED,
                     markeredgecolor="none", alpha=0.5),
)
for patch, c in zip(bp["boxes"], [C_BLUE, C_ORANGE]):
    patch.set_facecolor(c)
    patch.set_alpha(0.85)
    patch.set_edgecolor(c)
ax.set_xticklabels(["Without lens", "With lens"])
ax.set_ylabel("RMS delay spread (ns)")
ax.set_title("Aggregate delay-spread distribution", loc="left", fontsize=11, fontweight="bold")
style_ax(ax)

ax = axes[1]
d_w = per_rx_wolens.sort_values("rx_lens_angle_deg", ascending=False)
d_l = per_rx_lens.sort_values("rx_lens_angle_deg", ascending=False)
ds_w = wolens.groupby("rx_lens_angle_deg")["rms_delay_spread_ns"].median().reindex(ANGLES)
ds_l = lens.groupby("rx_lens_angle_deg")["rms_delay_spread_ns"].median().reindex(ANGLES)
ax.plot(ANGLES, ds_w.values, marker="o", ms=6, color=C_BLUE, linewidth=2.2, label="Without lens")
ax.plot(ANGLES, ds_l.values, marker="o", ms=6, color=C_ORANGE, linewidth=2.2, label="With lens")
ax.set_xticks(ANGLES)
ax.invert_xaxis()
ax.set_xlabel("RX lens angle (deg)")
ax.set_ylabel("Median RMS delay spread (ns)")
ax.set_title("Median delay spread per angle", loc="left", fontsize=11, fontweight="bold")
ax.legend(frameon=False, fontsize=9.5)
style_ax(ax)

fig.suptitle("Fig. 4 -- RMS delay spread: without lens vs with lens",
             x=0.02, ha="left", fontsize=12.5, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(f"{OUT}/fig4_delay_spread.png", dpi=200, bbox_inches="tight")
plt.close(fig)


# ============================================================
# Figure 5 -- virtual 9x9 MIMO conditioning, per drop (20 drops)
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))

ax = axes[0]
bp = ax.boxplot([mimo_wolens["cond_median_db"], mimo_lens["cond_median_db"]],
                patch_artist=True, widths=0.5,
                medianprops=dict(color=C_PRIMARY, linewidth=1.6))
for patch, c in zip(bp["boxes"], [C_BLUE, C_ORANGE]):
    patch.set_facecolor(c); patch.set_alpha(0.85); patch.set_edgecolor(c)
ax.set_xticklabels(["Without\nlens", "With\nlens"])
ax.set_ylabel("Condition number (dB)")
ax.set_title("Condition number", loc="left", fontsize=10.5, fontweight="bold")
style_ax(ax)

ax = axes[1]
bp = ax.boxplot([mimo_wolens["erank_median"], mimo_lens["erank_median"]],
                patch_artist=True, widths=0.5,
                medianprops=dict(color=C_PRIMARY, linewidth=1.6))
for patch, c in zip(bp["boxes"], [C_BLUE, C_ORANGE]):
    patch.set_facecolor(c); patch.set_alpha(0.85); patch.set_edgecolor(c)
ax.axhline(9, color=C_MUTED, linewidth=0.8, linestyle=(0, (2, 2)))
ax.annotate("9 = full rank", xy=(1.5, 9), xytext=(1.4, 8.3), fontsize=8, color=C_MUTED)
ax.set_xticklabels(["Without\nlens", "With\nlens"])
ax.set_ylabel("Effective rank (of 9)")
ax.set_title("Effective rank", loc="left", fontsize=10.5, fontweight="bold")
style_ax(ax)

ax = axes[2]
bp = ax.boxplot([mimo_wolens["capacity_10db"], mimo_lens["capacity_10db"]],
                patch_artist=True, widths=0.5,
                medianprops=dict(color=C_PRIMARY, linewidth=1.6))
for patch, c in zip(bp["boxes"], [C_BLUE, C_ORANGE]):
    patch.set_facecolor(c); patch.set_alpha(0.85); patch.set_edgecolor(c)
ax.set_xticklabels(["Without\nlens", "With\nlens"])
ax.set_ylabel("Capacity @ 10 dB SNR (bit/s/Hz)")
ax.set_title("Virtual 9x9 MIMO capacity", loc="left", fontsize=10.5, fontweight="bold")
style_ax(ax)

fig.suptitle("Fig. 5 -- Virtual 9x9 MIMO conditioning across 20 drops (not a physical single-RX result)",
             x=0.02, ha="left", fontsize=12, fontweight="bold", y=1.03)
fig.tight_layout()
fig.savefig(f"{OUT}/fig5_mimo_conditioning.png", dpi=200, bbox_inches="tight")
plt.close(fig)

print("All figures written to", OUT)
