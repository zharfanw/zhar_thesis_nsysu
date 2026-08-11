r"""Per-method channel evaluation (HFSS Hybrid, HFSS SBR+, Sionna-RT).

This program is derived from ``compare_channel_results.py``. Instead of
overlaying the three solvers on the same plot for a symmetric inter-solver
comparison, every simulation method is evaluated on its own: each method
gets its own output folder, its own CSV files, and its own plots. The only
comparison kept inside a method's evaluation is "with lens" vs "without
lens", since that is a property of the method's own simulation runs, not a
comparison against another solver.

Data loading (parse_complex, load_data_acq, load_realis, load_sionna,
load_all) and the core metric functions (common_summary,
add_normalized_magnitude, lens_gain, complex_at_common,
power_distribution_and_mimo) are reused unchanged from
compare_channel_results.py so that the underlying equations and the
canonical RX/TX antenna-equivalence mapping stay identical between both
programs.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from compare_channel_results import (
    RX_IDS,
    TX_IDS,
    SOURCE_STYLES,
    add_normalized_magnitude,
    common_summary,
    complex_at_common,
    lens_gain,
    load_all,
    power_distribution_and_mimo,
    write_mapping,
)

LENS_STYLES = {
    "with": dict(color="#d62728", marker="D", linestyle="-"),
    "without": dict(color="#1f77b4", marker="o", linestyle="--"),
}


def sanitize(name: str) -> str:
    """Turn a solver name into a filesystem-safe folder name."""
    return re.sub(r"[^\w+-]", "_", name.strip())


def plot_grid_per_method(data, source: str, metric: str, output: Path) -> None:
    """3x3 grid for one method: with-lens vs without-lens curves only."""
    ylabel = "Magnitude (dB)" if metric == "magnitude_db" else "Phase (degree)"
    fig, axes = plt.subplots(
        3, 3, figsize=(16, 12), sharex=True, sharey=(metric == "magnitude_db")
    )
    for rx in RX_IDS:
        for tx in TX_IDS:
            ax = axes[rx - 1, tx - 1]
            panel = data[(data["rx_index"] == rx) & (data["tx_index"] == tx)]
            for lens, style in LENS_STYLES.items():
                group = panel[panel["lens"] == lens].sort_values("freq_ghz")
                ax.plot(
                    group["freq_ghz"], group[metric],
                    color=style["color"], linestyle=style["linestyle"],
                    marker=style["marker"], markerfacecolor="none",
                    markeredgewidth=1.1, markevery=max(1, len(group) // 7),
                    linewidth=1.7, label=f"{lens} lens",
                )
            ax.set_title(f"H(rx{rx}, tx{tx})", fontweight="bold")
            ax.grid(True, alpha=.35)
            ax.set_xlim(36, 40)
            if rx == 3:
                ax.set_xlabel("Frequency (GHz)")
            if tx == 1:
                ax.set_ylabel(ylabel)
            if rx == 1 and tx == 3:
                ax.legend(fontsize=8)
    fig.suptitle(
        f"{source} — 3×3 Channel — With vs Without Lens — {ylabel}",
        fontweight="bold", fontsize=15,
    )
    fig.tight_layout(rect=[0, 0, 1, .97])
    fig.savefig(output / f"channel_3x3_{metric}.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_centered_grid_per_method(common, source: str, output: Path) -> None:
    """Frequency-shape comparison (with vs without lens) for one method."""
    fig, axes = plt.subplots(3, 3, figsize=(16, 12), sharex=True, sharey=True)
    for rx in RX_IDS:
        for tx in TX_IDS:
            ax = axes[rx - 1, tx - 1]
            panel = common[(common["rx_index"] == rx) & (common["tx_index"] == tx)]
            for lens, style in LENS_STYLES.items():
                group = panel[panel["lens"] == lens].sort_values("freq_ghz")
                ax.plot(
                    group["freq_ghz"], group["magnitude_centered_db"],
                    color=style["color"], linestyle=style["linestyle"],
                    marker=style["marker"], markerfacecolor="none",
                    linewidth=1.7, label=f"{lens} lens",
                )
            ax.axhline(0, color="#666666", linestyle=":", linewidth=.8)
            ax.set_title(f"H(rx{rx}, tx{tx})", fontweight="bold")
            ax.set_xticks([37, 38, 39])
            ax.grid(True, alpha=.3)
            if rx == 3:
                ax.set_xlabel("Frequency (GHz)")
            if tx == 1:
                ax.set_ylabel("Centered magnitude (dB)")
            if rx == 1 and tx == 3:
                ax.legend(fontsize=8)
    fig.suptitle(
        f"{source} — Normalized Channel Shape — With vs Without Lens",
        fontweight="bold", fontsize=14,
    )
    fig.tight_layout(rect=[0, 0, 1, .95])
    fig.savefig(
        output / "channel_3x3_normalized_shape.png", dpi=160, bbox_inches="tight"
    )
    plt.close(fig)


def plot_gain_grid_per_method(gain, source: str, output: Path) -> None:
    fig, axes = plt.subplots(3, 3, figsize=(16, 12), sharex=True, sharey=True)
    for rx in RX_IDS:
        for tx in TX_IDS:
            ax = axes[rx - 1, tx - 1]
            panel = gain[
                (gain["rx_index"] == rx) & (gain["tx_index"] == tx)
            ].sort_values("freq_ghz")
            ax.plot(
                panel["freq_ghz"], panel["lens_gain_db"],
                color="#d62728", marker="D", markerfacecolor="none",
                linewidth=1.8,
            )
            ax.axhline(0, color="black", linestyle=":", linewidth=.8)
            ax.set_title(f"H(rx{rx}, tx{tx})", fontweight="bold")
            ax.set_xticks([37, 38, 39])
            ax.grid(True, alpha=.35)
            if rx == 3:
                ax.set_xlabel("Frequency (GHz)")
            if tx == 1:
                ax.set_ylabel("Lens gain (dB)")
    fig.suptitle(
        f"{source} — Lens Gain (With minus Without)",
        fontweight="bold", fontsize=15,
    )
    fig.tight_layout(rect=[0, 0, 1, .96])
    fig.savefig(output / "channel_3x3_lens_gain.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_mimo_per_method(mimo, channel_form: str, source: str, output: Path) -> None:
    frequencies = [37.0, 38.0, 39.0]
    metrics = [
        ("condition_number", "Condition number κ\n(lower = more balanced)"),
        ("effective_rank", "Effective rank\n(higher = more spatial modes)"),
        ("capacity_20db_bps_hz", "Capacity at 20 dB (bps/Hz)"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    x = np.arange(len(frequencies))
    width = .32
    for col_idx, (metric, title) in enumerate(metrics):
        ax = axes[col_idx]
        for offset, lens in zip((-.18, .18), ("with", "without")):
            panel = (
                mimo[(mimo["channel_form"] == channel_form) & (mimo["lens"] == lens)]
                .set_index("freq_ghz").reindex(frequencies)
            )
            ax.bar(
                x + offset, panel[metric], width,
                color=LENS_STYLES[lens]["color"], label=f"{lens} lens",
            )
        ax.set_xticks(x, [f"{f:.0f} GHz" for f in frequencies])
        ax.set_title(title)
        ax.grid(axis="y", alpha=.3)
        if col_idx == 0:
            ax.legend()
    form_label = (
        "Raw Channel (absolute gain retained)"
        if channel_form == "raw"
        else "Frobenius-Normalized Channel (spatial structure only)"
    )
    fig.suptitle(
        f"{source} — MIMO Evaluation — {form_label}",
        fontweight="bold", fontsize=14,
    )
    fig.tight_layout(rect=[0, 0, 1, .93])
    fig.savefig(
        output / f"mimo_evaluation_{channel_form}.png", dpi=160, bbox_inches="tight"
    )
    plt.close(fig)


def plot_singular_values_per_method(mimo, source: str, output: Path) -> None:
    data = mimo[mimo["channel_form"] == "frobenius_normalized"]
    frequencies = [37.0, 38.0, 39.0]
    colors = ["#355c7d", "#6c9bcf", "#f28e2b"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    x = np.arange(len(frequencies))
    width = .24
    for col_idx, lens in enumerate(("with", "without")):
        ax = axes[col_idx]
        panel = data[data["lens"] == lens].set_index("freq_ghz").reindex(frequencies)
        for singular_idx, column in enumerate(("sv1", "sv2", "sv3")):
            ax.bar(
                x + (singular_idx - 1) * width, panel[column], width,
                color=colors[singular_idx], label=f"σ{singular_idx + 1}",
            )
        ax.set_xticks(x, [f"{f:.0f} GHz" for f in frequencies])
        ax.set_title("With lens" if lens == "with" else "Without lens")
        ax.grid(axis="y", alpha=.3)
        if col_idx == 0:
            ax.set_ylabel("Normalized singular value")
            ax.legend(title="Spatial mode")
    fig.suptitle(
        f"{source} — Frobenius-Normalized Singular Values",
        fontweight="bold", fontsize=14,
    )
    fig.tight_layout(rect=[0, 0, 1, .9])
    fig.savefig(output / "mimo_singular_values.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_spatial_correlation_per_method(correlation, source: str, output: Path) -> None:
    frequencies = [37.0, 38.0, 39.0]
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    x = np.arange(len(frequencies))
    for col_idx, side in enumerate(("rx", "tx")):
        ax = axes[col_idx]
        for offset, lens in zip((-.18, .18), ("with", "without")):
            panel = (
                correlation[
                    (correlation["side"] == side) & (correlation["lens"] == lens)
                ].set_index("freq_ghz").reindex(frequencies)
            )
            ax.bar(
                x + offset, panel["mean_off_diagonal_correlation"], .32,
                color=LENS_STYLES[lens]["color"], label=f"{lens} lens",
            )
        ax.set_xticks(x, [f"{f:.0f} GHz" for f in frequencies])
        ax.set_ylim(0, 1)
        ax.set_title(f"{side.upper()} correlation")
        ax.grid(axis="y", alpha=.3)
        if col_idx == 0:
            ax.set_ylabel("Mean off-diagonal |ρ| (lower = better)")
            ax.legend()
    fig.suptitle(f"{source} — Spatial Correlation", fontweight="bold", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, .9])
    fig.savefig(output / "spatial_correlation.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_power_heatmap_per_method(power, source: str, output: Path) -> None:
    frequencies = [37.0, 38.0, 39.0]
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.5))
    image = None
    for row_idx, lens in enumerate(("with", "without")):
        for col_idx, freq in enumerate(frequencies):
            ax = axes[row_idx, col_idx]
            panel = power[(power["lens"] == lens) & (power["freq_ghz"] == freq)]
            matrix = panel.pivot(
                index="rx_index", columns="tx_index",
                values="normalized_power_share",
            ).to_numpy()
            image = ax.imshow(matrix, vmin=0, vmax=1, cmap="Blues")
            for i in range(3):
                for j in range(3):
                    ax.text(
                        j, i, f"{100 * matrix[i, j]:.1f}%",
                        ha="center", va="center",
                        color="white" if matrix[i, j] > .45 else "black",
                    )
            ax.set_xticks(range(3), ["tx1", "tx2", "tx3"])
            ax.set_yticks(range(3), ["rx1", "rx2", "rx3"])
            ax.set_title(
                f"{'With' if lens == 'with' else 'Without'} lens\n{freq:.0f} GHz",
                fontsize=9,
            )
    fig.colorbar(image, ax=axes, shrink=.7, label="Normalized power share")
    fig.suptitle(f"{source} — Channel Power Distribution", fontweight="bold")
    fig.savefig(output / "power_distribution.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def evaluate_method(data, source: str, output_root: Path) -> Path:
    """Run the full single-method evaluation and write it to its own folder."""
    method_dir = output_root / sanitize(source)
    method_dir.mkdir(parents=True, exist_ok=True)

    sub = data[data["source"] == source].reset_index(drop=True)
    sub.to_csv(method_dir / "channel_results_long.csv", index=False)
    for metric in ("magnitude_db", "phase_deg"):
        plot_grid_per_method(sub, source, metric, method_dir)

    common = common_summary(sub)
    common = add_normalized_magnitude(common)
    common.to_csv(method_dir / "channel_37_38_39ghz.csv", index=False)
    plot_centered_grid_per_method(common, source, method_dir)

    gain = lens_gain(common)
    gain.to_csv(method_dir / "lens_gain.csv", index=False)
    plot_gain_grid_per_method(gain, source, method_dir)

    complex_common = complex_at_common(sub)
    power, mimo, correlation = power_distribution_and_mimo(complex_common)
    power.to_csv(method_dir / "power_distribution.csv", index=False)
    mimo.to_csv(method_dir / "mimo_metrics.csv", index=False)
    correlation.to_csv(method_dir / "spatial_correlation.csv", index=False)

    plot_power_heatmap_per_method(power, source, method_dir)
    plot_mimo_per_method(mimo, "raw", source, method_dir)
    plot_mimo_per_method(mimo, "frobenius_normalized", source, method_dir)
    plot_singular_values_per_method(mimo, source, method_dir)
    plot_spatial_correlation_per_method(correlation, source, method_dir)

    return method_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate each simulation method (HFSS Hybrid, HFSS SBR+, "
            "Sionna-RT) on its own, with no cross-solver comparison"
        )
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output", type=Path, default=Path("channel_evaluation_per_method")
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    data = load_all(args.root)
    write_mapping(args.output)

    for source in SOURCE_STYLES:
        method_dir = evaluate_method(data, source, args.output)
        count = int((data["source"] == source).sum())
        print(f"[{source}] samples={count} -> {method_dir.resolve()}")

    print("Per-method channel evaluation is complete.")
    print(f"Methods evaluated : {len(SOURCE_STYLES)}")
    print(f"Output root       : {args.output.resolve()}")


if __name__ == "__main__":
    main()
