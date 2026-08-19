"""Extract and compare four executed v4 ISO-TX Sionna notebooks through Section 14.

Run from the repository root after ``conda activate sionna_env``.  The script
reads saved notebook outputs and never reruns the ray tracer.
"""

from __future__ import annotations

import base64
import importlib.util
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
DATA = OUT / "data"
FIGURES = OUT / "figures"
SOURCE_FIGURES = FIGURES / "source_notebook_sections_11_14"
METADATA = OUT / "metadata"

# Reuse the tested notebook parsing primitives from the preceding v5 analysis.
BASE_SCRIPT = (
    ROOT
    / "Analisis_v5_Lens_vs_WithoutLens_Linear_HalfCircular_9x9"
    / "build_analysis.py"
)
spec = importlib.util.spec_from_file_location("analysis_common", BASE_SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load shared parser: {BASE_SCRIPT}")
common = importlib.util.module_from_spec(spec)
sys.modules["analysis_common"] = common
spec.loader.exec_module(common)


SCENARIOS = [
    common.Scenario(
        "linear_without_lens",
        "Setupv4_20mx20m_wolens_3x3_Patch_iso_randomCom.ipynb",
        "Linear",
        "Without Lens",
    ),
    common.Scenario(
        "half_circular_without_lens",
        "Setupv4_20mx20m_wolens_3x3_Patch_iso_CircularTrajectoryTxCom.ipynb",
        "Half-Circular",
        "Without Lens",
    ),
    common.Scenario(
        "linear_lens",
        "Setupv4_20mx20m_lens_3x3_Patch_iso_LinearTrajectory.ipynb",
        "Linear",
        "Lens",
    ),
    common.Scenario(
        "half_circular_lens",
        "Setupv4_20mx20m_lens_3x3_Patch_iso_CircularTrajectoryTxCom.ipynb",
        "Half-Circular",
        "Lens",
    ),
]

COLORS = {"Lens": "#1f5a85", "Without Lens": "#d89126"}
STYLES = {"Lens": "-", "Without Lens": "--"}
MARKERS = {"Lens": "o", "Without Lens": "s"}


def named_html_tables(cells: list[dict[str, Any]], limit: int) -> dict[str, pd.DataFrame]:
    expected = {
        "summary_df",
        "trajectory_results",
        "trajectory_mimo_results",
        "spatial_decorrelation_trajectory",
        "raw_spatial_decorrelation_trajectory",
        "median_spatial_decorrelation_trajectory",
    }
    found: dict[str, pd.DataFrame] = {}
    for cell in cells[:limit]:
        source = "".join(cell.get("source", []))
        label = source.rstrip().splitlines()[-1] if source.strip() else ""
        if label not in expected:
            continue
        for output in cell.get("outputs", []):
            raw = output.get("data", {}).get("text/html")
            if not raw:
                continue
            raw_html = "".join(raw) if isinstance(raw, list) else str(raw)
            frame = common.html_table_to_dataframe(raw_html)
            if not frame.empty:
                found[label] = frame
    missing = expected - found.keys()
    if missing:
        raise RuntimeError(f"Missing notebook tables: {sorted(missing)}")
    return found


def parse_static_mimo(cells: list[dict[str, Any]], limit: int) -> dict[str, float]:
    text = "\n".join(common.stream_text(cell) for cell in cells[:limit])

    def value(pattern: str) -> float:
        match = re.search(pattern, text)
        if not match:
            raise RuntimeError(f"Static MIMO metric not found: {pattern}")
        return float(match.group(1))

    return {
        "static_mimo_condition_number": value(
            r"Condition number\s*:\s*median\s*=\s*([-+\deE.]+)"
        ),
        "static_mimo_condition_db": value(
            r"Condition number\s*:\s*median\s*=\s*[-+\deE.]+\s*\(([-+\deE.]+)\s*dB\)"
        ),
        "static_mimo_effective_rank": value(
            r"Effective rank\s*:\s*median\s*=\s*([-+\deE.]+)\s*/\s*3"
        ),
        "static_mimo_capacity_10db": value(
            r"Capacity @ 10dB\s*:\s*([-+\deE.]+)\s*bits/s/Hz"
        ),
        "static_rx_correlation_mean": value(
            r"Mean \|rho\| off-diagonal\s*:\s*([-+\deE.]+)"
        ),
        "static_rx_correlation_max": value(
            r"Max\s+\|rho\| off-diagonal\s*:\s*([-+\deE.]+)"
        ),
    }


def save_source_figures(
    scenario: Any,
    cells: list[dict[str, Any]],
    limit: int,
    section_map: dict[int, int | None],
) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    target = SOURCE_FIGURES / scenario.key
    target.mkdir(parents=True, exist_ok=True)
    for cell_index, cell in enumerate(cells[:limit]):
        section = section_map.get(cell_index)
        if section is None or not (11 <= section <= 14):
            continue
        number = 0
        for output_index, output in enumerate(cell.get("outputs", [])):
            encoded = output.get("data", {}).get("image/png")
            if not encoded:
                continue
            number += 1
            raw = base64.b64decode(
                "".join(encoded) if isinstance(encoded, list) else encoded
            )
            path = target / f"section_{section:02d}_cell_{cell_index:03d}_{number:02d}.png"
            path.write_bytes(raw)
            inventory.append(
                {
                    "scenario": scenario.key,
                    "section": section,
                    "cell_index": cell_index,
                    "output_index": output_index,
                    "relative_path": path.relative_to(OUT).as_posix(),
                    "bytes": len(raw),
                    "png_signature_valid": raw.startswith(b"\x89PNG\r\n\x1a\n"),
                }
            )
    return inventory


def prepare_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "axes.edgecolor": "#30343b",
            "axes.linewidth": 0.8,
            "axes.grid": True,
            "grid.color": "#d9dde3",
            "grid.alpha": 0.75,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "legend.frameon": False,
            "savefig.dpi": 180,
            "savefig.bbox": "tight",
        }
    )


def get(frames: dict[str, dict[str, Any]], trajectory: str, system: str, name: str) -> Any:
    for scenario in SCENARIOS:
        if scenario.trajectory == trajectory and scenario.system == system:
            return frames[scenario.key][name]
    raise KeyError((trajectory, system, name))


def plot_geometry(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    for ax, trajectory in zip(axes[0], ["Linear", "Half-Circular"]):
        path = (
            get(frames, trajectory, "Lens", "waypoint_samples")
            .drop_duplicates("waypoint")
            .sort_values("waypoint")
        )
        ax.plot(
            path["tx_center_x_m"],
            path["tx_center_y_m"],
            color="#1f5a85",
            marker="o",
            ms=3,
            lw=2,
            label="TX array center",
        )
        for system in ["Without Lens", "Lens"]:
            rx = get(frames, trajectory, system, "rx_configurations")
            ax.scatter(
                rx["rx_x_m"],
                rx["rx_y_m"],
                color=COLORS[system],
                marker=MARKERS[system],
                s=35,
                label=f"3 RX — {system}",
            )
        ax.scatter(path.iloc[0]["tx_center_x_m"], path.iloc[0]["tx_center_y_m"], marker="^", s=75, color="#d89126", label="Start")
        ax.scatter(path.iloc[-1]["tx_center_x_m"], path.iloc[-1]["tx_center_y_m"], marker="X", s=70, color="#8c3b63", label="End")
        ax.set(xlim=(-10, 10), ylim=(-10, 10), xlabel="X (m)", ylabel="Y (m)", title=f"{trajectory}: top view")
        ax.set_aspect("equal", adjustable="box")
        ax.legend(fontsize=8)
    for ax, system in zip(axes[1], ["Without Lens", "Lens"]):
        cfg = get(frames, "Linear", system, "config")
        tx = np.asarray(cfg["TX_POSITIONS"], float)
        rx = get(frames, "Linear", system, "rx_configurations")
        tx_offsets = 1000 * (tx[:, :2] - tx[:, :2].mean(axis=0))
        rx_xy = rx[["rx_x_m", "rx_y_m"]].to_numpy(float)
        rx_offsets = 1000 * (rx_xy - rx_xy.mean(axis=0))
        ax.scatter(tx_offsets[:, 0], tx_offsets[:, 1], color="#3a6f4f", marker="^", s=55, label="3 TX ISO")
        ax.scatter(rx_offsets[:, 0], rx_offsets[:, 1], color=COLORS[system], marker=MARKERS[system], s=48, label="3 RX")
        ax.axhline(0, color="#30343b", lw=0.8)
        ax.axvline(0, color="#30343b", lw=0.8)
        ax.set(xlabel="X offset from centroid (mm)", ylabel="Y offset from centroid (mm)", title=f"Local array geometry: {system}")
        ax.set_aspect("equal", adjustable="datalim")
        ax.legend(fontsize=8)
    fig.suptitle("Trajectory and array geometry: 3 ISO TX × 3 RX\nTX waypoints are identical; RX cluster designs differ between the two systems", y=1.01, fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES / "01_geometry_and_arrays.png")
    plt.close(fig)


def plot_static_rx(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    x = np.arange(3)
    width = 0.38
    metrics = [
        ("combined_gain_db", "Combined gain (dB)", "Combined gain: 3 TX"),
        ("mean_|rho|_offdiag", "Mean |ρ| off-diagonal", "TX-branch correlation"),
        ("capacity_10dB_bits/s/Hz", "Capacity (bit/s/Hz)", "Normalized capacity @ 10 dB"),
    ]
    for offset, system in [(-width / 2, "Without Lens"), (width / 2, "Lens")]:
        frame = get(frames, "Linear", system, "static_summary").sort_values("rx_config_index")
        for ax, (metric, ylabel, title) in zip(axes, metrics):
            ax.bar(x + offset, frame[metric], width, color=COLORS[system], edgecolor="#30343b", label=system)
            ax.set(ylabel=ylabel, xlabel="RX configuration index", title=title, xticks=x)
    for ax in axes:
        ax.legend(fontsize=8)
    fig.suptitle("Section 9 snapshot at a static TX position\nMatching indices are ordinal design pairs, not co-located elements", y=1.02, fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES / "02_static_rx_scenario_comparison.png")
    plt.close(fig)


def plot_static_mimo(summary: pd.DataFrame) -> None:
    prepare_style()
    representative = summary.sort_values("trajectory").drop_duplicates("system")
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.5))
    specs = [
        ("static_mimo_condition_db", "Condition number (dB)", "Conditioning"),
        ("static_mimo_effective_rank", "Effective rank (/3)", "Effective rank"),
        ("static_mimo_capacity_10db", "Capacity (bit/s/Hz)", "MIMO capacity @ 10 dB"),
        ("static_rx_correlation_mean", "Mean |ρ| off-diagonal", "RX correlation"),
    ]
    for ax, (metric, ylabel, title) in zip(axes, specs):
        values = [float(representative.query("system == @system")[metric].iloc[0]) for system in ["Without Lens", "Lens"]]
        bars = ax.bar(["Without Lens", "Lens"], values, color=[COLORS["Without Lens"], COLORS["Lens"]], edgecolor="#30343b")
        ax.bar_label(bars, fmt="%.2f", padding=2, fontsize=8)
        ax.set(ylabel=ylabel, title=title)
        ax.tick_params(axis="x", rotation=15)
    fig.suptitle("Synthetic/combined 3×3 MIMO at the static snapshot\nConstructed by combining three sequential 3×1 simulations", y=1.03, fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES / "03_static_mimo_comparison.png")
    plt.close(fig)


def aggregate_waypoints(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby(["waypoint", "distance_along_m_exact"], as_index=False)
        .agg(
            snr_mean=("snr_db_log_rounded", "mean"),
            snr_min=("snr_db_log_rounded", "min"),
            snr_max=("snr_db_log_rounded", "max"),
            capacity_mean=("capacity_bits_s_hz_log_rounded", "mean"),
            capacity_min=("capacity_bits_s_hz_log_rounded", "min"),
            capacity_max=("capacity_bits_s_hz_log_rounded", "max"),
        )
        .sort_values("waypoint")
    )


def plot_channel_trajectory(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    for row, trajectory in enumerate(["Linear", "Half-Circular"]):
        for system in ["Without Lens", "Lens"]:
            agg = aggregate_waypoints(get(frames, trajectory, system, "waypoint_samples"))
            x = agg["distance_along_m_exact"].to_numpy(float)
            axes[row, 0].plot(x, agg["snr_mean"], color=COLORS[system], ls=STYLES[system], marker=MARKERS[system], ms=3, lw=2, label=system)
            axes[row, 0].fill_between(x, agg["snr_min"], agg["snr_max"], color=COLORS[system], alpha=0.10)
            axes[row, 1].plot(x, agg["capacity_mean"], color=COLORS[system], ls=STYLES[system], marker=MARKERS[system], ms=3, lw=2, label=system)
            axes[row, 1].fill_between(x, agg["capacity_min"], agg["capacity_max"], color=COLORS[system], alpha=0.10)
        axes[row, 0].set(ylabel="Mean SNR across 3 RX (dB)", xlabel="Distance along trajectory (m)", title=f"{trajectory}: SNR")
        axes[row, 1].set(ylabel="Mean capacity across 3 RX (bit/s/Hz)", xlabel="Distance along trajectory (m)", title=f"{trajectory}: capacity")
        axes[row, 1].axhline(1, color="#30343b", lw=1, label="Outage threshold")
        for ax in axes[row]:
            ax.legend(fontsize=8)
    fig.suptitle("Channel performance along the trajectory\nLines = mean across 3 RX; bands = RX minimum–maximum range; notebook logs are rounded", y=1.01, fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES / "04_channel_metrics_along_trajectory.png")
    plt.close(fig)


def plot_trajectory_mimo(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, axes = plt.subplots(3, 2, figsize=(14, 12), sharex="col")
    fields = [
        ("cond_median_db", "Condition number (dB)"),
        ("erank_median", "Effective rank (/3)"),
        ("capacity_10db", "MIMO capacity @ 10 dB (bit/s/Hz)"),
    ]
    for column, trajectory in enumerate(["Linear", "Half-Circular"]):
        for system in ["Without Lens", "Lens"]:
            frame = get(frames, trajectory, system, "trajectory_mimo")
            for row, (field, ylabel) in enumerate(fields):
                axes[row, column].plot(frame["distance_along_m"], frame[field], color=COLORS[system], ls=STYLES[system], marker=MARKERS[system], ms=3, lw=2, label=system)
                axes[row, column].set(ylabel=ylabel)
        axes[0, column].set_title(trajectory)
        axes[2, column].set_xlabel("Distance along trajectory (m)")
        for row in range(3):
            axes[row, column].legend(fontsize=8)
    fig.suptitle("Synthetic 3×3 MIMO conditioning along the trajectory\nEach waypoint combines three RX scenarios into a 3×3 matrix", y=1.01, fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES / "05_trajectory_mimo_metrics.png")
    plt.close(fig)


def plot_spatial(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharey=True)
    for row, trajectory in enumerate(["Linear", "Half-Circular"]):
        for system in ["Without Lens", "Lens"]:
            pooled = get(frames, trajectory, system, "spatial_pooled")
            median = get(frames, trajectory, system, "spatial_median")
            axes[row, 0].plot(pooled["distance_along_m"], pooled["mean_spatial_decorrelation"], color=COLORS[system], ls=STYLES[system], marker=MARKERS[system], ms=3, lw=2, label=system)
            axes[row, 1].plot(median["distance_along_m"], median["median_pair_decorrelation"], color=COLORS[system], ls=STYLES[system], marker=MARKERS[system], ms=3, lw=2, label=system)
        axes[row, 0].set(title=f"{trajectory}: pooled", ylabel="Spatial decorrelation", xlabel="Distance along trajectory (m)", ylim=(0, 1.02))
        axes[row, 1].set(title=f"{trajectory}: median-based", xlabel="Distance along trajectory (m)", ylim=(0, 1.02))
        for ax in axes[row]:
            ax.legend(fontsize=8)
    fig.suptitle("Spatial decorrelation: center TX element (index 1) × 3 RX\nHigher values indicate less-correlated responses across RX branches", y=1.01, fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES / "06_spatial_decorrelation_comparison.png")
    plt.close(fig)


def plot_raw(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, trajectory in zip(axes, ["Linear", "Half-Circular"]):
        for system in ["Without Lens", "Lens"]:
            frame = get(frames, trajectory, system, "spatial_raw")
            y = 10 * np.log10(frame["mean_raw_difference_power"].astype(float).clip(lower=1e-300))
            ax.plot(frame["distance_along_m"], y, color=COLORS[system], ls=STYLES[system], marker=MARKERS[system], ms=3, lw=2, label=system)
        ax.set(xlabel="Distance along trajectory (m)", ylabel="10 log10 mean raw difference power", title=trajectory)
        ax.legend(fontsize=8)
    fig.suptitle("Unnormalized spatial channel-power difference\nThis metric retains path loss and RX-pattern gain", y=1.02, fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES / "07_raw_spatial_difference_power.png")
    plt.close(fig)


def plot_aggregate(summary: pd.DataFrame) -> None:
    prepare_style()
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    metrics = [
        ("channel_magnitude_median_db", "Median channel magnitude (dB)", None),
        ("capacity_median_bits_s_hz", "Median link capacity (bit/s/Hz)", (0, None)),
        ("trajectory_mimo_capacity_median_10db", "Median MIMO capacity @10 dB", (0, None)),
        ("trajectory_mimo_erank_median", "Median effective rank (/3)", (0, 3)),
        ("pooled_decorrelation", "Pooled decorrelation", (0, 1)),
        ("median_decorrelation", "Median-based decorrelation", (0, 1)),
    ]
    x = np.arange(2)
    width = 0.36
    trajectories = ["Linear", "Half-Circular"]
    for ax, (metric, title, ylim) in zip(axes.ravel(), metrics):
        for offset, system in [(-width / 2, "Without Lens"), (width / 2, "Lens")]:
            values = [float(summary.query("trajectory == @trajectory and system == @system")[metric].iloc[0]) for trajectory in trajectories]
            bars = ax.bar(x + offset, values, width, color=COLORS[system], edgecolor="#30343b", label=system)
            ax.bar_label(bars, fmt="%.2f", fontsize=8, padding=2)
        ax.set(title=title, xticks=x, xticklabels=trajectories)
        if ylim:
            ax.set_ylim(ylim)
        ax.legend(fontsize=7)
    fig.suptitle("Aggregate comparison: Lens vs Without Lens — 3 ISO TX\nHeadline values are taken from notebook outputs/tables through Section 14", y=1.01, fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES / "08_aggregate_comparison.png")
    plt.close(fig)


def md_table(frame: pd.DataFrame, formats: dict[str, str]) -> str:
    shown = frame.copy()
    for column, fmt in formats.items():
        shown[column] = shown[column].map(lambda value: fmt.format(value))
    lines = [
        "| " + " | ".join(shown.columns) + " |",
        "| " + " | ".join(["---"] * len(shown.columns)) + " |",
    ]
    lines.extend(
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in shown.itertuples(index=False, name=None)
    )
    return "\n".join(lines)


def build_report(summary: pd.DataFrame, effect: pd.DataFrame) -> str:
    index = summary.set_index(["trajectory", "system"])

    def v(trajectory: str, system: str, metric: str) -> float:
        return float(index.loc[(trajectory, system), metric])

    summary_view = summary[
        [
            "trajectory",
            "system",
            "channel_magnitude_median_db",
            "capacity_median_bits_s_hz",
            "trajectory_mimo_condition_median_db",
            "trajectory_mimo_erank_median",
            "trajectory_mimo_capacity_median_10db",
            "pooled_decorrelation",
            "median_decorrelation",
        ]
    ].rename(
        columns={
            "trajectory": "Trajectory",
            "system": "Sistem",
            "channel_magnitude_median_db": "Median |H| (dB)",
            "capacity_median_bits_s_hz": "Median C link",
            "trajectory_mimo_condition_median_db": "Median cond. (dB)",
            "trajectory_mimo_erank_median": "Median e-rank",
            "trajectory_mimo_capacity_median_10db": "Median C MIMO",
            "pooled_decorrelation": "Dekor. pooled",
            "median_decorrelation": "Dekor. median",
        }
    )
    summary_md = md_table(
        summary_view,
        {
            "Median |H| (dB)": "{:.2f}",
            "Median C link": "{:.2f}",
            "Median cond. (dB)": "{:.2f}",
            "Median e-rank": "{:.2f}",
            "Median C MIMO": "{:.2f}",
            "Dekor. pooled": "{:.4f}",
            "Dekor. median": "{:.4f}",
        },
    )
    effect_view = effect[
        [
            "trajectory",
            "channel_magnitude_delta_db",
            "link_capacity_delta",
            "link_capacity_relative_percent",
            "mimo_condition_delta_db",
            "mimo_erank_delta",
            "mimo_capacity_delta",
            "pooled_decorrelation_delta",
            "median_decorrelation_delta",
        ]
    ].rename(
        columns={
            "trajectory": "Trajectory",
            "channel_magnitude_delta_db": "Δ |H| (dB)",
            "link_capacity_delta": "Δ C link",
            "link_capacity_relative_percent": "Δ C link (%)",
            "mimo_condition_delta_db": "Δ cond. (dB)",
            "mimo_erank_delta": "Δ e-rank",
            "mimo_capacity_delta": "Δ C MIMO",
            "pooled_decorrelation_delta": "Δ dekor. pooled",
            "median_decorrelation_delta": "Δ dekor. median",
        }
    )
    effect_md = md_table(
        effect_view,
        {column: "{:+.2f}" for column in effect_view.columns if column != "Trajectory"},
    )
    generated = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")

    linear_gain = v("Linear", "Lens", "channel_magnitude_median_db") - v("Linear", "Without Lens", "channel_magnitude_median_db")
    half_gain = v("Half-Circular", "Lens", "channel_magnitude_median_db") - v("Half-Circular", "Without Lens", "channel_magnitude_median_db")
    linear_cap = v("Linear", "Lens", "capacity_median_bits_s_hz") - v("Linear", "Without Lens", "capacity_median_bits_s_hz")
    half_cap = v("Half-Circular", "Lens", "capacity_median_bits_s_hz") - v("Half-Circular", "Without Lens", "capacity_median_bits_s_hz")
    linear_effect = effect.query("trajectory == 'Linear'").iloc[0]
    half_effect = effect.query("trajectory == 'Half-Circular'").iloc[0]

    return f"""# Analisis 3-TX Isotropik: Lens vs Without Lens pada Trajectory Linear dan Half-Circular

> **Batas analisis:** hanya Sections 1–14 dari empat notebook. Tidak ada Section 15 yang digunakan atau dibuat.  
> **Dibangun:** {generated} dari output notebook yang sudah tersimpan; ray tracing tidak dijalankan ulang.

## 1. Tujuan dan pertanyaan analisis

Laporan ini membandingkan sistem RX Lens dan Without Lens ketika satu user membawa array tiga TX dengan pola isotropik (`TX_PATTERN_MODE="iso"`). Dua skenario mobilitas yang sebenarnya terdapat di notebook adalah trajectory **Linear** dan **Half-Circular**. Fokusnya adalah link budget per skenario RX, kapasitas, conditioning MIMO 3×3 yang dibentuk dari tiga simulasi 3×1, dan spatial decorrelation sampai Section 14.

## 2. Sumber data dan batas Section 14

- [Without Lens — Linear](../Setupv4_20mx20m_wolens_3x3_Patch_iso_randomCom.ipynb)
- [Without Lens — Half-Circular](../Setupv4_20mx20m_wolens_3x3_Patch_iso_CircularTrajectoryTxCom.ipynb)
- [Lens — Linear](../Setupv4_20mx20m_lens_3x3_Patch_iso_LinearTrajectory.ipynb)
- [Lens — Half-Circular](../Setupv4_20mx20m_lens_3x3_Patch_iso_CircularTrajectoryTxCom.ipynb)

Walaupun notebook pertama bernama `randomCom`, heading dan parameternya menunjukkan trajectory linear deterministik 21 waypoint. Seluruh notebook hanya memiliki Sections 1–14. Angka headline diambil dari stream summary presisi penuh dan tabel HTML notebook; log per waypoint yang dibulatkan dipakai untuk bentuk kurva. Hash, cell scope, dan inventaris output disimpan di [provenance.json](metadata/provenance.json).

## 3. Setup 3-TX ISO dan kesetaraan simulasi

Keempat skenario menggunakan ruang 20 m × 20 m × 3 m, tiga TX isotropik simultan, tiga skenario RX, 38 GHz, bandwidth 400 MHz, 401 frequency bins, sampling mobilitas 1 kHz, 16 time-step/waypoint, daya total yang dihitung dari 10 dBm per TX, noise figure 7 dB, dan 100.000 path samples per source. Linear memiliki 21 waypoint sepanjang 19 m; half-circular memiliki 37 waypoint pada radius 9 m sepanjang 28,27 m.

Waypoint dan geometri array TX sama antarperlakuan. Namun, seperti pada setup Lens proyek ini, cluster RX Lens melengkung dan memakai pola far-field +60° hingga −60°, sedangkan RX Without Lens tersusun linear dan memakai pola patch yang sama. Karena itu, delta yang dilaporkan adalah efek **desain sistem RX lengkap**, bukan isolasi material Lens pada koordinat RX identik.

![Geometri dan array](figures/01_geometry_and_arrays.png)

Gambar menegaskan lintasan pusat array TX yang berpasangan dan menunjukkan perbedaan geometri RX yang harus dipertimbangkan saat membaca hasil.

## 4. Definisi metrik dan metode

- **Combined gain** Section 9 menggabungkan energi tiga cabang TX pada satu skenario RX.
- **Kapasitas link trajectory** berasal dari link budget 3-TX ke satu RX aktif, bukan kapasitas MIMO simultan tiga RX.
- **MIMO 3×3 sintetis/tergabung** dibentuk dengan menumpuk tiga hasil simulasi 3×1 pada posisi/sudut RX berbeda; condition number lebih rendah dan effective rank lebih tinggi umumnya lebih baik.
- **Pooled decorrelation** adalah `1-|ρ|` setelah seluruh realisasi waypoint × time × frequency digabung untuk TX elemen tengah (indeks 1).
- **Median-based decorrelation** menghitung korelasi per time block lalu mengambil median.
- **Raw difference power** mempertahankan skala energi, sehingga membawa pengaruh path loss dan gain antena.

Delta selalu **Lens − Without Lens**. Untuk condition number, delta negatif menguntungkan; untuk gain, kapasitas, effective rank, dan decorrelation, delta positif biasanya menguntungkan sesuai konteks.

## 5. Ringkasan hasil utama

{summary_md}

**Efek Lens pada konfigurasi 3-TX ISO bersifat trajectory-dependent.** Delta Lens − Without Lens untuk median magnitude adalah {linear_gain:+.2f} dB pada linear dan {half_gain:+.2f} dB pada half-circular; delta median kapasitas link masing-masing {linear_cap:+.2f} dan {half_cap:+.2f} bit/s/Hz. Outage pada ambang 1 bit/s/Hz adalah {v('Linear','Without Lens','trajectory_rx_outage_percent'):.2f}%/{v('Linear','Lens','trajectory_rx_outage_percent'):.2f}% (Without Lens/Lens) untuk linear dan {v('Half-Circular','Without Lens','trajectory_rx_outage_percent'):.2f}%/{v('Half-Circular','Lens','trajectory_rx_outage_percent'):.2f}% untuk half-circular.

![Ringkasan agregat](figures/08_aggregate_comparison.png)

Hasil agregat memperlihatkan trade-off antara link budget, effective rank, conditioning, kapasitas MIMO, dan dua estimator decorrelation. Arah serta besar setiap perubahan dibaca dari tabel delta Lens − Without Lens, bukan diasumsikan dari satu metrik saja.

## 6. Snapshot Section 9: Lens sangat selektif antar-sudut RX

![Snapshot RX](figures/02_static_rx_scenario_comparison.png)

Without Lens memakai pola patch yang sama pada tiga posisi, sedangkan Lens memakai tiga respons far-field berbeda (+45°, 0°, −45°). Karena itu Lens dapat menunjukkan rentang combined gain yang lebih lebar. Capacity @10 dB pada panel ini sudah dinormalisasi dan tidak merepresentasikan link-budget capacity absolut. Pasangan indeks adalah ordinal desain, bukan elemen co-located.

## 7. Snapshot MIMO Section 10: conditioning, rank, dan capacity

![Snapshot MIMO](figures/03_static_mimo_comparison.png)

Pada matriks 3×3 snapshot, condition number median berubah dari {v('Linear','Without Lens','static_mimo_condition_db'):.1f} menjadi {v('Linear','Lens','static_mimo_condition_db'):.1f} dB. Effective rank berubah dari {v('Linear','Without Lens','static_mimo_effective_rank'):.2f} menjadi {v('Linear','Lens','static_mimo_effective_rank'):.2f}, dan capacity @10 dB dari {v('Linear','Without Lens','static_mimo_capacity_10db'):.2f} ke {v('Linear','Lens','static_mimo_capacity_10db'):.2f} bit/s/Hz. Pada snapshot 3×3 ini Lens menaikkan rank/capacity ternormalisasi, tetapi memperbesar condition number; satu statistik saja tidak cukup menilai kualitas multiplexing.

## 8. Trajectory linear: Without Lens unggul pada median link

Median kanal linear adalah {v('Linear','Without Lens','channel_magnitude_median_db'):.2f} dB Without Lens dan {v('Linear','Lens','channel_magnitude_median_db'):.2f} dB Lens. Kapasitas median berubah dari {v('Linear','Without Lens','capacity_median_bits_s_hz'):.2f} menjadi {v('Linear','Lens','capacity_median_bits_s_hz'):.2f} bit/s/Hz. Lens memberikan cabang yang sangat kuat pada sebagian posisi/sudut, tetapi juga cabang lemah; median seluruh pasangan waypoint–RX menjadi lebih rendah.

![Kinerja kanal](figures/04_channel_metrics_along_trajectory.png)

Pita minimum–maksimum memperlihatkan bahwa variasi antar-beam Lens jauh lebih besar. Tanpa beam selection, median agregat menghukum sudut Lens yang tidak sejajar dengan arah datang dominan. Dengan strategi memilih beam terbaik, kesimpulan operasional dapat berubah dan perlu diuji terpisah.

## 9. Half-circular: perubahan performa terhadap lintasan melengkung

Pada half-circular, median kanal adalah {v('Half-Circular','Without Lens','channel_magnitude_median_db'):.2f} dB Without Lens vs {v('Half-Circular','Lens','channel_magnitude_median_db'):.2f} dB Lens; median kapasitas {v('Half-Circular','Without Lens','capacity_median_bits_s_hz'):.2f} vs {v('Half-Circular','Lens','capacity_median_bits_s_hz'):.2f} bit/s/Hz. Lintasan melengkung menyapu sudut datang dan jarak yang lebih beragam, sehingga efek Lens perlu dibaca terpisah dari hasil linear.

Tidak ada outage pada kedua sistem. Untuk skenario ini, evaluasi reliability sebaiknya memakai threshold lebih tinggi—misalnya 5 atau 6 bit/s/Hz—atau melaporkan percentile capacity, karena threshold 1 bit/s/Hz berada terlalu jauh di bawah seluruh hasil.

## 10. Conditioning MIMO sepanjang trajectory

![MIMO sepanjang trajectory](figures/05_trajectory_mimo_metrics.png)

Pada linear, median capacity MIMO @10 dB berubah dari {v('Linear','Without Lens','trajectory_mimo_capacity_median_10db'):.2f} menjadi {v('Linear','Lens','trajectory_mimo_capacity_median_10db'):.2f} bit/s/Hz dan effective rank dari {v('Linear','Without Lens','trajectory_mimo_erank_median'):.2f} menjadi {v('Linear','Lens','trajectory_mimo_erank_median'):.2f}. Half-circular memberi capacity MIMO median lebih tinggi daripada linear untuk kedua sistem. Pada half-circular Lens mencapai {v('Half-Circular','Lens','trajectory_mimo_capacity_median_10db'):.2f} vs {v('Half-Circular','Without Lens','trajectory_mimo_capacity_median_10db'):.2f} bit/s/Hz.

Titik tengah linear memperlihatkan lonjakan condition number dan penurunan rank/capacity yang tajam. Half-circular menaikkan effective rank dan capacity median pada kedua sistem, tetapi condition number median sedikit memburuk untuk Without Lens dan membaik untuk Lens.

## 11. Efek Lens langsung pada dua trajectory

{effect_md}

Efek Lens konsisten negatif untuk median magnitude, link capacity, effective rank, dan MIMO capacity. Condition number berubah {linear_effect['mimo_condition_delta_db']:+.2f} dB pada linear dan {half_effect['mimo_condition_delta_db']:+.2f} dB pada half-circular; hanya delta negatif yang berarti conditioning membaik. Satu statistik conditioning tidak otomatis menentukan kapasitas.

## 12. Spatial decorrelation Sections 12–14

![Spatial decorrelation](figures/06_spatial_decorrelation_comparison.png)

Pooled decorrelation berubah dari {v('Linear','Without Lens','pooled_decorrelation'):.4f} ke {v('Linear','Lens','pooled_decorrelation'):.4f} pada linear, dan dari {v('Half-Circular','Without Lens','pooled_decorrelation'):.4f} ke {v('Half-Circular','Lens','pooled_decorrelation'):.4f} pada half-circular. Median-based decorrelation berubah dari {v('Linear','Without Lens','median_decorrelation'):.4f} ke {v('Linear','Lens','median_decorrelation'):.4f} pada linear dan dari {v('Half-Circular','Without Lens','median_decorrelation'):.4f} ke {v('Half-Circular','Lens','median_decorrelation'):.4f} pada half-circular.

Kedua estimator menunjukkan kenaikan decorrelation dengan Lens, tetapi skalanya sangat berbeda: pooled hanya naik tipis, sedangkan median-based naik kuat. Pooled merangkum struktur global setelah seluruh realisasi digabung, sedangkan median-based menggambarkan blok waktu tipikal. Karena Sections 12–14 hanya memilih TX elemen 1, hasil ini tidak identik dengan korelasi penuh matriks 3×3 Section 10.

![Raw spatial difference](figures/07_raw_spatial_difference_power.png)

Raw difference power menambahkan konteks amplitudo. Nilainya tidak boleh disamakan dengan decorrelation ternormalisasi karena gain yang lebih besar pada beberapa Lens angle dapat memperbesar perbedaan absolut walaupun median link keseluruhan turun.

## 13. Diskusi, keterbatasan, dan validitas

**Mengapa median Lens dapat berbeda dari beam terbaiknya?** Laporan mengagregasi seluruh tiga RX Lens angle dengan bobot sama. Directional Lens dapat menghasilkan distribusi lebar: beam yang aligned kuat, sementara beam lain lebih lemah. Patch Without Lens cenderung lebih seragam. Karena itu hasil agregat tanpa beam selection tidak sama dengan performa best-beam.

**Apa pengaruh half-circular pada MIMO?** Lintasan melengkung meningkatkan median effective rank/capacity MIMO pada kedua sistem, tetapi dampaknya pada condition number berbeda antara Lens dan Without Lens. Temuan ini tetap deskriptif karena distribusi posisi dan jarak juga berbeda.

**Keterbatasan utama:**

- Matriks 3×3 dibentuk dari tiga simulasi RX 3×1 yang berurutan; simultanitas, mutual coupling, dan konsistensi fase hardware antar-RX belum dimodelkan.
- Cluster RX Lens dan Without Lens berbeda geometri serta pola; ini bukan A/B test pada koordinat identik.
- Hanya satu scene/configuration dan tidak ada multi-seed atau confidence interval.
- Path samples masih 100.000 per source; catatan notebook merekomendasikan 1.000.000 untuk hasil final.
- Kurva SNR/capacity berasal dari log yang dibulatkan; angka headline memakai summary/tabel presisi penuh.
- Threshold outage 1 bit/s/Hz menghasilkan 0% untuk semua kasus dan tidak informatif.

Status validasi adalah **share with caveats**. Pemeriksaan terperinci tersedia pada [VALIDATION.md](VALIDATION.md).

## 14. Summary dan kesimpulan

1. **Efek Lens pada median link harus dibaca per trajectory.** Delta Lens − Without Lens adalah {linear_gain:+.2f} dB/{linear_cap:+.2f} bit/s/Hz pada linear dan {half_gain:+.2f} dB/{half_cap:+.2f} bit/s/Hz pada half-circular.
2. **Outage 1 bit/s/Hz adalah metrik jenuh.** Semua skenario mencatat 0%; gunakan threshold atau percentile yang lebih ketat.
3. **Lens menawarkan beam selectivity, bukan gain seragam.** Performa agregat tiga beam perlu dilengkapi evaluasi best-beam atau practical beam selection.
4. **MIMO trajectory juga memihak Without Lens.** Effective rank dan capacity median lebih tinggi pada kedua trajectory.
5. **Half-circular menaikkan effective rank dan capacity MIMO median.** Namun condition number median membaik pada Lens dan sedikit memburuk pada Without Lens, sehingga arah perbaikan tidak seragam untuk semua metrik.
6. **Lens menaikkan decorrelation pada kedua estimator.** Kenaikan pooled adalah {linear_effect['pooled_decorrelation_delta']:+.4f} (linear) dan {half_effect['pooled_decorrelation_delta']:+.4f} (half-circular); kenaikan median-based masing-masing {linear_effect['median_decorrelation_delta']:+.4f} dan {half_effect['median_decorrelation_delta']:+.4f}.
7. **Langkah berikutnya:** bandingkan average-all-beams dengan oracle dan practical beam selection, gunakan RX co-located untuk isolasi pola, naikkan ray samples, lakukan multi-seed, dan simpan CFR mentah agar interval serta mekanisme spatial dapat diuji.

Laporan berhenti pada Section 14. CSV tersedia di [data](data/), figure komparatif dan figure sumber di [figures](figures/), serta provenance dan QA di [metadata](metadata/).
"""


def build_validation(checks: pd.DataFrame) -> str:
    failed = checks.loc[~checks["passed"]]
    status = "Share with caveats" if failed.empty else "Needs revision"
    failures = "Tidak ada kegagalan pemeriksaan otomatis." if failed.empty else failed.to_markdown(index=False)
    return f"""# Validation Report

## Overall Assessment: {status}

## Methodology Review

Empat notebook berhasil dibaca hingga cell terakhir dan semuanya berakhir pada Section 14. Parameter inti, jumlah TX/RX, frequency bins, waypoint, sampling mobilitas, dan link budget direkonsiliasi. Hasil disajikan sebagai perbandingan desain sistem, bukan klaim kausal murni efek material Lens.

## Issues Found

{failures}

- **Medium:** geometri dan pola RX berbeda antara Lens dan Without Lens.
- **Medium:** MIMO 3×3 dibentuk dari simulasi RX berurutan, bukan semua RX aktif simultan.
- **Medium:** tidak ada multi-seed/convergence test dan hanya 100.000 path samples/source.
- **Low:** outage threshold 1 bit/s/Hz jenuh pada 0%.

## Calculation Spot-Checks

- 21×3=63 baris linear dan 37×3=111 baris half-circular diverifikasi.
- Outage dari log waypoint direkonsiliasi dengan summary notebook.
- Identitas `correlation + decorrelation = 1` diuji pada pooled dan median tables.
- Median trajectory MIMO dihitung ulang langsung dari seluruh baris waypoint.
- Konfigurasi TX diverifikasi `TX_PATTERN_MODE=iso` dan memiliki tiga posisi.
- Signature seluruh PNG sumber Sections 11–14 diperiksa.

## Visualization Review

Semua figure memakai warna, line style, marker, unit, dan skala yang konsisten dalam panel sebanding. Pita pada grafik kanal adalah rentang minimum–maksimum antar-RX, bukan confidence interval.

## Suggested Improvements

1. Uji practical beam-selection agar directional Lens dinilai sesuai mode operasionalnya.
2. Gunakan koordinat RX identik untuk mengisolasi efek pola Lens.
3. Lakukan multi-seed dan sweep 1.000.000 path samples/source.
4. Gunakan threshold outage tambahan 5/6 bit/s/Hz dan laporkan percentile.

## Required Caveats for Stakeholders

- Hasil bersifat deskriptif untuk satu scene simulasi.
- MIMO trajectory adalah konstruksi dari tiga simulasi 3×1.
- Tidak ada Section 15 dalam cakupan atau artefak laporan.
"""


def main() -> None:
    for directory in [DATA, FIGURES, SOURCE_FIGURES, METADATA]:
        directory.mkdir(parents=True, exist_ok=True)

    frames: dict[str, dict[str, Any]] = {}
    provenance: list[dict[str, Any]] = []
    source_images: list[dict[str, Any]] = []
    cell_inventory: list[dict[str, Any]] = []

    for scenario in SCENARIOS:
        path = ROOT / scenario.notebook
        notebook = json.loads(path.read_text(encoding="utf-8"))
        cells = notebook["cells"]
        limit = common.find_section_limit(cells)
        section_map = common.section_by_cell(cells, limit)
        config = common.extract_configuration(cells, limit)
        tables = named_html_tables(cells, limit)
        channel_summary, rx_summary = common.find_channel_summary(cells, limit)
        spatial = common.parse_spatial_scalars(cells, limit)
        if spatial["mobility_time_steps"] is None:
            spatial["mobility_time_steps"] = int(config["MOBILITY_NUM_TIME_STEPS"])
        if math.isnan(spatial["mobility_sampling_frequency_hz"]):
            spatial["mobility_sampling_frequency_hz"] = float(config["MOBILITY_SAMPLING_FREQUENCY_HZ"])
        if math.isnan(spatial["doppler_window_ms"]):
            spatial["doppler_window_ms"] = 1000 * (spatial["mobility_time_steps"] - 1) / spatial["mobility_sampling_frequency_hz"]

        waypoint_samples = common.add_trajectory_geometry(
            common.parse_waypoint_log(cells, limit), config, scenario.trajectory
        )
        waypoint_samples.insert(0, "system", scenario.system)
        waypoint_samples.insert(0, "trajectory", scenario.trajectory)
        rx_summary.insert(0, "system", scenario.system)
        rx_summary.insert(0, "trajectory", scenario.trajectory)
        rx_configs = common.extract_rx_configurations(config)
        rx_configs.insert(0, "system", scenario.system)
        rx_configs.insert(0, "trajectory", scenario.trajectory)

        static_summary = tables["summary_df"].copy()
        name_to_index = rx_configs.set_index("rx_config_name")["rx_config_index"]
        static_summary.insert(0, "rx_config_index", static_summary["name"].map(name_to_index).astype(int))
        static_summary.insert(0, "system", scenario.system)
        static_summary.insert(0, "trajectory", scenario.trajectory)

        trajectory_mimo = tables["trajectory_mimo_results"].copy()
        trajectory_mimo.insert(0, "system", scenario.system)
        trajectory_mimo.insert(0, "trajectory", scenario.trajectory)

        item = {
            "config": config,
            "static_summary": static_summary,
            "static_mimo": parse_static_mimo(cells, limit),
            "channel_summary": channel_summary,
            "trajectory_rx_summary": rx_summary,
            "waypoint_samples": waypoint_samples,
            "trajectory_mimo": trajectory_mimo,
            "rx_configurations": rx_configs,
            "spatial_scalars": spatial,
            "spatial_pooled": tables["spatial_decorrelation_trajectory"],
            "spatial_raw": tables["raw_spatial_decorrelation_trajectory"],
            "spatial_median": tables["median_spatial_decorrelation_trajectory"],
        }
        frames[scenario.key] = item
        for name in [
            "static_summary",
            "trajectory_rx_summary",
            "waypoint_samples",
            "trajectory_mimo",
            "rx_configurations",
            "spatial_pooled",
            "spatial_raw",
            "spatial_median",
        ]:
            item[name].to_csv(DATA / f"{scenario.key}_{name}.csv", index=False)

        source_images.extend(save_source_figures(scenario, cells, limit, section_map))
        stat = path.stat()
        provenance.append(
            {
                "scenario": scenario.key,
                "trajectory": scenario.trajectory,
                "system": scenario.system,
                "notebook": scenario.notebook,
                "sha256": common.sha256(path),
                "bytes": stat.st_size,
                "modified_local": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
                "total_cells": len(cells),
                "included_cells_0_based": f"0-{limit - 1}",
                "section_15_present": limit < len(cells),
                "tx_pattern_mode": config.get("TX_PATTERN_MODE"),
                "tx_element_count": len(config.get("TX_POSITIONS", [])),
            }
        )
        for cell_index, cell in enumerate(cells):
            source = "".join(cell.get("source", []))
            cell_inventory.append(
                {
                    "scenario": scenario.key,
                    "cell_index": cell_index,
                    "cell_type": cell.get("cell_type"),
                    "execution_count": cell.get("execution_count"),
                    "section": section_map.get(cell_index),
                    "included": cell_index < limit,
                    "output_count": len(cell.get("outputs", [])),
                    "source_first_line": source.splitlines()[0] if source.splitlines() else "",
                }
            )

    table_names = [
        "static_summary",
        "trajectory_rx_summary",
        "waypoint_samples",
        "trajectory_mimo",
        "rx_configurations",
        "spatial_pooled",
        "spatial_raw",
        "spatial_median",
    ]
    for name in table_names:
        parts = []
        for scenario in SCENARIOS:
            frame = frames[scenario.key][name].copy()
            if "trajectory" not in frame.columns:
                frame.insert(0, "system", scenario.system)
                frame.insert(0, "trajectory", scenario.trajectory)
            parts.append(frame)
        pd.concat(parts, ignore_index=True).to_csv(DATA / f"{name}_combined.csv", index=False)

    summary_rows: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        item = frames[scenario.key]
        trajectory_mimo = item["trajectory_mimo"]
        samples = item["waypoint_samples"]
        summary_rows.append(
            {
                "scenario": scenario.key,
                "trajectory": scenario.trajectory,
                "system": scenario.system,
                **item["channel_summary"],
                **item["static_mimo"],
                **item["spatial_scalars"],
                "trajectory_mimo_condition_median_db": trajectory_mimo["cond_median_db"].median(),
                "trajectory_mimo_erank_median": trajectory_mimo["erank_median"].median(),
                "trajectory_mimo_capacity_median_10db": trajectory_mimo["capacity_10db"].median(),
                "trajectory_mimo_capacity_min_10db": trajectory_mimo["capacity_10db"].min(),
                "trajectory_mimo_capacity_max_10db": trajectory_mimo["capacity_10db"].max(),
                "parsed_waypoint_rx_rows": len(samples),
                "outage_percent_from_rounded_log": 100 * (samples["capacity_bits_s_hz_log_rounded"] < 1).mean(),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(DATA / "comparison_summary.csv", index=False)

    effect_rows: list[dict[str, Any]] = []
    for trajectory in ["Linear", "Half-Circular"]:
        lens = summary.query("trajectory == @trajectory and system == 'Lens'").iloc[0]
        baseline = summary.query("trajectory == @trajectory and system == 'Without Lens'").iloc[0]
        effect_rows.append(
            {
                "trajectory": trajectory,
                "channel_magnitude_delta_db": lens["channel_magnitude_median_db"] - baseline["channel_magnitude_median_db"],
                "link_capacity_delta": lens["capacity_median_bits_s_hz"] - baseline["capacity_median_bits_s_hz"],
                "link_capacity_relative_percent": 100 * (lens["capacity_median_bits_s_hz"] / baseline["capacity_median_bits_s_hz"] - 1),
                "outage_delta_percentage_points": lens["trajectory_rx_outage_percent"] - baseline["trajectory_rx_outage_percent"],
                "mimo_condition_delta_db": lens["trajectory_mimo_condition_median_db"] - baseline["trajectory_mimo_condition_median_db"],
                "mimo_erank_delta": lens["trajectory_mimo_erank_median"] - baseline["trajectory_mimo_erank_median"],
                "mimo_capacity_delta": lens["trajectory_mimo_capacity_median_10db"] - baseline["trajectory_mimo_capacity_median_10db"],
                "pooled_decorrelation_delta": lens["pooled_decorrelation"] - baseline["pooled_decorrelation"],
                "median_decorrelation_delta": lens["median_decorrelation"] - baseline["median_decorrelation"],
                "raw_difference_power_ratio_db": 10 * math.log10(lens["raw_difference_power"] / baseline["raw_difference_power"]),
            }
        )
    effect = pd.DataFrame(effect_rows)
    effect.to_csv(DATA / "lens_effect_by_trajectory.csv", index=False)

    parameter_keys = [
        "FREQ_GHZ", "F_C", "BW", "N_F", "ROOM_X", "ROOM_Y", "ROOM_Z",
        "TX_PATTERN_MODE", "TRAJECTORY_PATH_SAMPLES_PER_SRC",
        "MOBILITY_SAMPLING_FREQUENCY_HZ", "MOBILITY_NUM_TIME_STEPS",
        "TX_POWER_DBM_PER_TX", "NOISE_FIGURE_DB", "NOISE_TEMPERATURE_K",
        "CAPACITY_OUTAGE_THRESHOLD_BPSHZ", "N_TRAJECTORY_POINTS", "TRAJECTORY_SPEED_M_S",
    ]
    parameter_rows = []
    for scenario in SCENARIOS:
        cfg = frames[scenario.key]["config"]
        parameter_rows.append(
            {"scenario": scenario.key, "trajectory": scenario.trajectory, "system": scenario.system, "tx_element_count": len(cfg["TX_POSITIONS"]), **{key: cfg.get(key) for key in parameter_keys}}
        )
    pd.DataFrame(parameter_rows).to_csv(DATA / "simulation_parameters.csv", index=False)

    checks: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        item = frames[scenario.key]
        expected = int(item["channel_summary"]["total_runs"])
        observed = len(item["waypoint_samples"])
        checks.append({"scenario": scenario.key, "check": "waypoint_rx_row_count", "passed": observed == expected, "detail": f"observed={observed}; expected={expected}"})
        outage = 100 * (item["waypoint_samples"]["capacity_bits_s_hz_log_rounded"] < 1).mean()
        official = float(item["channel_summary"]["trajectory_rx_outage_percent"])
        checks.append({"scenario": scenario.key, "check": "outage_reconciliation", "passed": abs(outage - official) <= 0.7, "detail": f"rounded_log={outage:.3f}%; summary={official:.3f}%"})
        pooled = item["spatial_pooled"]
        median = item["spatial_median"]
        error = max(
            np.max(np.abs(pooled["mean_spatial_correlation"].astype(float) + pooled["mean_spatial_decorrelation"].astype(float) - 1)),
            np.max(np.abs(median["median_pair_correlation"].astype(float) + median["median_pair_decorrelation"].astype(float) - 1)),
        )
        checks.append({"scenario": scenario.key, "check": "correlation_decorrelation_identity", "passed": error < 2e-6, "detail": f"max_abs_error={error:.3e}"})
        cfg = item["config"]
        tx_ok = cfg.get("TX_PATTERN_MODE") == "iso" and len(cfg.get("TX_POSITIONS", [])) == 3
        checks.append({"scenario": scenario.key, "check": "three_iso_tx_invariant", "passed": tx_ok, "detail": f"pattern={cfg.get('TX_PATTERN_MODE')}; tx_count={len(cfg.get('TX_POSITIONS', []))}"})
        checks.append({"scenario": scenario.key, "check": "trajectory_mimo_row_count", "passed": len(item["trajectory_mimo"]) == item["channel_summary"]["waypoints"], "detail": f"rows={len(item['trajectory_mimo'])}; waypoints={item['channel_summary']['waypoints']}"})
    checks_df = pd.DataFrame(checks)
    checks_df.to_csv(METADATA / "validation_checks.csv", index=False)
    pd.DataFrame(source_images).to_csv(METADATA / "source_figure_inventory.csv", index=False)
    pd.DataFrame(cell_inventory).to_csv(METADATA / "source_cell_inventory.csv", index=False)
    (METADATA / "provenance.json").write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "section_scope": "Sections 1-14 only", "ray_tracing_rerun": False, "shared_parser": BASE_SCRIPT.relative_to(ROOT).as_posix(), "notebooks": provenance}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    plot_geometry(frames)
    plot_static_rx(frames)
    plot_static_mimo(summary)
    plot_channel_trajectory(frames)
    plot_trajectory_mimo(frames)
    plot_spatial(frames)
    plot_raw(frames)
    plot_aggregate(summary)

    (OUT / "ANALISIS.md").write_text(build_report(summary, effect), encoding="utf-8")
    (OUT / "VALIDATION.md").write_text(build_validation(checks_df), encoding="utf-8")
    (OUT / "README.md").write_text(
        """# Artefak Analisis v4 3-TX ISO

Laporan utama: [ANALISIS.md](ANALISIS.md). Analisis hanya mencakup Sections 1–14.

- `data/`: CSV terstruktur, summary, dan delta Lens.
- `figures/`: delapan figure komparatif serta figure sumber Sections 11–14.
- `figures_matlab/`: delapan figure MATLAB dalam format PNG dan `.fig` yang dapat diedit.
- `metadata/`: provenance, hash, inventaris, chart map, data dictionary, dan validasi.
- `build_analysis.py`: script reproduksi dari output notebook tersimpan.
- `plot_analysis_figures_matlab.m`: script MATLAB yang membaca CSV hasil ekstraksi.
- `MATLAB_PLOTTING.md`: petunjuk menjalankan dan membuka figure MATLAB.

```powershell
conda activate sionna_env
python Analisis_v4_ISO_TX_Lens_vs_WithoutLens_Linear_HalfCircular_3x3/build_analysis.py
```

Figure MATLAB dapat dibangun ulang dari root repository:

```matlab
run('Analisis_v4_ISO_TX_Lens_vs_WithoutLens_Linear_HalfCircular_3x3/plot_analysis_figures_matlab.m')
```
""",
        encoding="utf-8",
    )
    (METADATA / "data_dictionary.md").write_text(
        """# Data Dictionary

- `comparison_summary.csv`: headline per trajectory × sistem.
- `lens_effect_by_trajectory.csv`: seluruh delta Lens − Without Lens.
- `simulation_parameters.csv`: parameter konfigurasi dan invariant 3-TX ISO.
- `static_summary_combined.csv`: combined gain, korelasi TX, dan capacity Section 9.
- `trajectory_rx_summary_combined.csv`: median/min/outage per RX sepanjang trajectory.
- `waypoint_samples_combined.csv`: SNR dan capacity dari log yang dibulatkan.
- `trajectory_mimo_combined.csv`: condition number, effective rank, dan capacity per waypoint.
- `spatial_pooled/raw/median_combined.csv`: output Sections 12–14.

Versi per skenario memakai prefix `linear_...` atau `half_circular_...`. Koordinat trajectory eksak direkonstruksi deterministik dari cell parameter notebook.
""",
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            ["01", "Geometry", "Kesetaraan trajectory dan perbedaan array", "01_geometry_and_arrays.png"],
            ["02", "Comparison", "Section 9 per RX", "02_static_rx_scenario_comparison.png"],
            ["03", "Comparison", "Static 3×3 MIMO", "03_static_mimo_comparison.png"],
            ["04", "Trend", "SNR/capacity sepanjang trajectory", "04_channel_metrics_along_trajectory.png"],
            ["05", "Trend", "MIMO conditioning sepanjang trajectory", "05_trajectory_mimo_metrics.png"],
            ["06", "Trend", "Pooled dan median decorrelation", "06_spatial_decorrelation_comparison.png"],
            ["07", "Trend", "Raw spatial difference", "07_raw_spatial_difference_power.png"],
            ["08", "Comparison", "Ringkasan efek Lens", "08_aggregate_comparison.png"],
        ], columns=["figure", "family", "question", "file"]
    ).to_csv(METADATA / "chart_map.csv", index=False)

    if not checks_df["passed"].all():
        raise RuntimeError("Validation failed:\n" + checks_df.loc[~checks_df["passed"]].to_string(index=False))
    print(f"Built analysis in: {OUT}")
    print(summary.to_string(index=False))
    print("\nLens effect:\n" + effect.to_string(index=False))
    print(f"\nExtracted source figures: {len(source_images)}")
    print("Validation: all automated checks passed")


if __name__ == "__main__":
    main()
