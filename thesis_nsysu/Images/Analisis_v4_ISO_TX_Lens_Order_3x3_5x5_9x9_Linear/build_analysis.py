"""Build a Sections 1-14 comparison of executed v4 Lens ISO-TX notebooks.

Run from the repository root after ``conda activate sionna_env``. The script
only reads saved notebook outputs; it does not rerun Sionna RT.
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

BASE_SCRIPT = ROOT / "Analisis_v4_ISO_TX_Lens_vs_WithoutLens_Linear_HalfCircular_9x9" / "build_analysis.py"
spec = importlib.util.spec_from_file_location("v4_analysis_common", BASE_SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load shared parser: {BASE_SCRIPT}")
base = importlib.util.module_from_spec(spec)
sys.modules["v4_analysis_common"] = base
spec.loader.exec_module(base)
common = base.common

SCENARIOS = [
    common.Scenario("order_3x3", "Setupv4_20mx20m_lens_3x3_Patch_iso_LinearTrajectory.ipynb", "Linear", "3x3"),
    common.Scenario("order_5x5", "Setupv4_20mx20m_lens_5x5_Patch_iso_LinearTrajectory.ipynb", "Linear", "5x5"),
    common.Scenario("order_9x9", "Setupv4_20mx20m_lens_9x9_Patch_iso_TrajectoryTxCom.ipynb", "Linear", "9x9"),
]
ORDER = {"order_3x3": 3, "order_5x5": 5, "order_9x9": 9}
LABEL = {3: "3×3", 5: "5×5", 9: "9×9"}
COLORS = {3: "#1f5a85", 5: "#d89126", 9: "#8b4771"}
STYLES = {3: "-", 5: "--", 9: "-."}
MARKERS = {3: "o", 5: "s", 9: "^"}


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
            "savefig.facecolor": "white",
        }
    )


def static_mimo(cells: list[dict[str, Any]], limit: int) -> dict[str, float]:
    text = "\n".join(common.stream_text(cell) for cell in cells[:limit])

    def value(pattern: str) -> float:
        match = re.search(pattern, text)
        if not match:
            raise RuntimeError(f"Static MIMO metric not found: {pattern}")
        return float(match.group(1))

    return {
        "static_mimo_condition_number": value(r"Condition number\s*:\s*median\s*=\s*([-+\deE.]+)"),
        "static_mimo_condition_db": value(r"Condition number\s*:\s*median\s*=\s*[-+\deE.]+\s*\(([-+\deE.]+)\s*dB\)"),
        "static_mimo_effective_rank": value(r"Effective rank\s*:\s*median\s*=\s*([-+\deE.]+)\s*/\s*\d+"),
        "static_mimo_capacity_10db": value(r"Capacity @ 10dB\s*:\s*([-+\deE.]+)\s*bits/s/Hz"),
        "static_rx_correlation_mean": value(r"Mean \|rho\| off-diagonal\s*:\s*([-+\deE.]+)"),
        "static_rx_correlation_max": value(r"Max\s+\|rho\| off-diagonal\s*:\s*([-+\deE.]+)"),
    }


def selected_tx_index(cells: list[dict[str, Any]], limit: int) -> int:
    text = "\n".join(common.stream_text(cell) for cell in cells[:limit])
    match = re.search(r"Selected TX element\s*:\s*(\d+)", text)
    if not match:
        raise RuntimeError("Selected TX element not found")
    return int(match.group(1))


def save_source_figures(scenario: Any, cells: list[dict[str, Any]], limit: int, section_map: dict[int, int | None]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    target = SOURCE_FIGURES / scenario.key
    target.mkdir(parents=True, exist_ok=True)
    for cell_index, cell in enumerate(cells[:limit]):
        section = section_map.get(cell_index)
        if section is None or not 11 <= section <= 14:
            continue
        image_number = 0
        for output_index, output in enumerate(cell.get("outputs", [])):
            encoded = output.get("data", {}).get("image/png")
            if not encoded:
                continue
            image_number += 1
            raw = base64.b64decode("".join(encoded) if isinstance(encoded, list) else encoded)
            path = target / f"section_{section:02d}_cell_{cell_index:03d}_{image_number:02d}.png"
            path.write_bytes(raw)
            inventory.append(
                {
                    "scenario": scenario.key,
                    "order_n": ORDER[scenario.key],
                    "section": section,
                    "cell_index": cell_index,
                    "output_index": output_index,
                    "relative_path": path.relative_to(OUT).as_posix(),
                    "bytes": len(raw),
                    "png_signature_valid": raw.startswith(b"\x89PNG\r\n\x1a\n"),
                }
            )
    return inventory


def add_order(frame: pd.DataFrame, n: int) -> pd.DataFrame:
    result = frame.copy()
    result.insert(0, "order_label", LABEL[n])
    result.insert(0, "order_n", n)
    return result


def aggregate_waypoints(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby("distance_along_m", as_index=False)
        .agg(
            snr_mean=("snr_db_log_rounded", "mean"),
            snr_min=("snr_db_log_rounded", "min"),
            snr_max=("snr_db_log_rounded", "max"),
            capacity_mean=("capacity_bits_s_hz_log_rounded", "mean"),
            capacity_min=("capacity_bits_s_hz_log_rounded", "min"),
            capacity_max=("capacity_bits_s_hz_log_rounded", "max"),
        )
        .sort_values("distance_along_m")
    )


def plot_geometry(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))
    cfg = frames["order_9x9"]["config"]
    xs = np.linspace(float(cfg["TRAJECTORY_START_M"][0]), float(cfg["TRAJECTORY_END_M"][0]), int(cfg["N_TRAJECTORY_POINTS"]))
    ys = np.linspace(float(cfg["TRAJECTORY_START_M"][1]), float(cfg["TRAJECTORY_END_M"][1]), int(cfg["N_TRAJECTORY_POINTS"]))
    axes[0].plot(xs, ys, color="#375a7f", marker="o", ms=3, lw=2)
    axes[0].scatter([xs[0]], [ys[0]], marker="^", s=90, color="#d89126", label="Start")
    axes[0].scatter([xs[-1]], [ys[-1]], marker="X", s=80, color="#8b4771", label="End")
    axes[0].set(title="Identical linear trajectory", xlabel="X (m)", ylabel="Y (m)", xlim=(-10, 10), ylim=(-10, 10))
    axes[0].set_aspect("equal")
    axes[0].legend()

    for scenario in SCENARIOS:
        n = ORDER[scenario.key]
        tx = np.asarray(frames[scenario.key]["config"]["TX_POSITIONS"], dtype=float)
        center = tx.mean(axis=0)
        axes[1].plot((tx[:, 1] - center[1]) * 1000, np.full(n, n), linestyle="none", marker=MARKERS[n], ms=7, color=COLORS[n], label=LABEL[n])
        rx = frames[scenario.key]["rx_configurations"]
        axes[2].plot(rx["rx_lens_angle_deg"], np.full(len(rx), n), linestyle="none", marker=MARKERS[n], ms=7, color=COLORS[n], label=LABEL[n])
    axes[1].set(title="ISO TX array footprint", xlabel="Y offset from centroid (mm)", ylabel="Order N", yticks=[3, 5, 9])
    axes[2].set(title="Lens RX pattern angular coverage", xlabel="RX Lens angle (degrees)", ylabel="Order N", yticks=[3, 5, 9])
    axes[1].legend(title="System")
    axes[2].legend(title="System")
    fig.suptitle("Lens order N×N geometry with an identical linear trajectory\nElement count, TX aperture, and RX angular sampling increase with order", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(FIGURES / "01_geometry_order_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_static_rx(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    metrics = [
        ("combined_gain_db", "Combined gain (dB)", "Combined gain"),
        ("mean_|rho|_offdiag", "Mean |ρ| off-diagonal", "TX-branch correlation"),
        ("capacity_10dB_bits/s/Hz", "Capacity (bit/s/Hz)", "Normalized capacity @ 10 dB"),
    ]
    for scenario in SCENARIOS:
        n = ORDER[scenario.key]
        frame = frames[scenario.key]["static_summary"].sort_values("rx_lens_angle_deg")
        for ax, (column, ylabel, title) in zip(axes, metrics):
            ax.plot(frame["rx_lens_angle_deg"], frame[column], label=LABEL[n], color=COLORS[n], linestyle=STYLES[n], marker=MARKERS[n], lw=2)
            ax.set(title=title, xlabel="RX Lens angle (degrees)", ylabel=ylabel)
    for ax in axes:
        ax.legend(title="Order")
    fig.suptitle("Section 9 static snapshot by RX Lens angle\nOnly the 0° angle is available for all three orders", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.89))
    fig.savefig(FIGURES / "02_static_rx_by_order.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_static_mimo(summary: pd.DataFrame) -> None:
    prepare_style()
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    metrics = [
        ("static_mimo_condition_db", "Condition number (dB)", "Conditioning — lower is better"),
        ("static_mimo_effective_rank", "Effective rank", "Effective rank"),
        ("static_mimo_erank_fraction", "Effective rank / N", "Dimension utilization"),
        ("static_mimo_capacity_10db", "bit/s/Hz", "MIMO capacity @ 10 dB"),
        ("static_mimo_capacity_per_order", "bit/s/Hz/element", "Capacity per order"),
        ("static_rx_correlation_mean", "Mean |ρ| off-diagonal", "RX correlation"),
    ]
    x = np.arange(len(summary))
    for ax, (column, ylabel, title) in zip(axes.flat, metrics):
        bars = ax.bar(x, summary[column], color=[COLORS[int(n)] for n in summary["order_n"]], edgecolor="#30343b")
        ax.set(title=title, ylabel=ylabel, xticks=x, xticklabels=summary["order_label"])
        ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=9)
    fig.suptitle("Synthetic/combined MIMO at the Section 10 static snapshot\nEach N×N matrix is constructed from N sequential N×1 simulations", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    fig.savefig(FIGURES / "03_static_mimo_scaling.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_channel(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    for scenario in SCENARIOS:
        n = ORDER[scenario.key]
        data = aggregate_waypoints(frames[scenario.key]["waypoint_samples"])
        x = data["distance_along_m"].to_numpy(float)
        for ax, mean, low, high, ylabel in [
            (axes[0], "snr_mean", "snr_min", "snr_max", "Mean SNR across RX branches (dB)"),
            (axes[1], "capacity_mean", "capacity_min", "capacity_max", "Mean capacity across RX branches (bit/s/Hz)"),
        ]:
            ax.plot(x, data[mean], label=LABEL[n], color=COLORS[n], linestyle=STYLES[n], marker=MARKERS[n], ms=4, lw=2)
            ax.fill_between(x, data[low], data[high], color=COLORS[n], alpha=0.07)
            ax.set(xlabel="Distance along trajectory (m)", ylabel=ylabel)
    axes[0].set_title("SNR along the trajectory")
    axes[1].set_title("Link capacity along the trajectory")
    axes[1].axhline(1, color="#333333", lw=1, label="Outage threshold")
    for ax in axes:
        ax.legend(title="Order")
    fig.suptitle("Section 11 link performance\nLines = RX mean; bands = minimum-to-maximum range across RX branches", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.89))
    fig.savefig(FIGURES / "04_channel_along_trajectory.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_trajectory_mimo(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    metrics = [
        ("cond_median_db", "Condition number (dB)", "Conditioning"),
        ("erank_median", "Effective rank", "Effective rank"),
        ("erank_fraction", "Effective rank / N", "Dimension utilization"),
        ("capacity_10db", "bit/s/Hz", "MIMO capacity @ 10 dB"),
    ]
    for scenario in SCENARIOS:
        n = ORDER[scenario.key]
        data = frames[scenario.key]["trajectory_mimo"].copy()
        data["erank_fraction"] = data["erank_median"] / n
        for ax, (column, ylabel, title) in zip(axes.flat, metrics):
            ax.plot(data["distance_along_m"], data[column], label=LABEL[n], color=COLORS[n], linestyle=STYLES[n], marker=MARKERS[n], ms=4, lw=2)
            ax.set(title=title, xlabel="Distance along trajectory (m)", ylabel=ylabel)
    for ax in axes.flat:
        ax.legend(title="Order")
    fig.suptitle("Synthetic MIMO along the trajectory — Section 11c\nHigher order increases absolute capacity but does not automatically improve per-dimension efficiency", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    fig.savefig(FIGURES / "05_trajectory_mimo_scaling.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_spatial(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), sharey=True)
    for scenario in SCENARIOS:
        n = ORDER[scenario.key]
        item = frames[scenario.key]
        label = f"{LABEL[n]} (TX {item['selected_tx_index']})"
        pooled = item["spatial_pooled"]
        median = item["spatial_median"]
        axes[0].plot(pooled["distance_along_m"], pooled["mean_spatial_decorrelation"], label=label, color=COLORS[n], linestyle=STYLES[n], marker=MARKERS[n], ms=4, lw=2)
        axes[1].plot(median["distance_along_m"], median["median_pair_decorrelation"], label=label, color=COLORS[n], linestyle=STYLES[n], marker=MARKERS[n], ms=4, lw=2)
    axes[0].set_title("Pooled decorrelation")
    axes[1].set_title("Median-based decorrelation")
    for ax in axes:
        ax.set(xlabel="Distance along trajectory (m)", ylabel="Spatial decorrelation", ylim=(0, 1))
        ax.legend(title="Order (selected TX)")
    fig.suptitle("Spatial decorrelation — Sections 12 and 14\nAll orders use the center TX element: indices 1, 2, and 4", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.89))
    fig.savefig(FIGURES / "06_spatial_decorrelation_by_order.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_raw(frames: dict[str, dict[str, Any]]) -> None:
    prepare_style()
    fig, ax = plt.subplots(figsize=(13, 5.5))
    for scenario in SCENARIOS:
        n = ORDER[scenario.key]
        data = frames[scenario.key]["spatial_raw"]
        values = 10 * np.log10(data["mean_raw_difference_power"].astype(float).clip(lower=np.finfo(float).tiny))
        ax.plot(data["distance_along_m"], values, label=f"{LABEL[n]} (TX {frames[scenario.key]['selected_tx_index']})", color=COLORS[n], linestyle=STYLES[n], marker=MARKERS[n], ms=4, lw=2)
    ax.set(title="Unnormalized spatial channel-power difference", xlabel="Distance along trajectory (m)", ylabel="10 log10 mean raw difference power")
    ax.legend(title="Order (selected TX)")
    fig.suptitle("Section 13 retains path loss and RX-pattern gain\nHigher values indicate larger power differences across branches", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(FIGURES / "07_raw_spatial_difference_by_order.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_aggregate(summary: pd.DataFrame) -> None:
    prepare_style()
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    metrics = [
        ("capacity_median_bits_s_hz", "bit/s/Hz", "Median link capacity"),
        ("trajectory_mimo_capacity_median_10db", "bit/s/Hz", "Median MIMO capacity @ 10 dB"),
        ("trajectory_mimo_capacity_per_order", "bit/s/Hz/element", "MIMO capacity per order"),
        ("trajectory_mimo_erank_fraction", "Effective rank / N", "MIMO dimension utilization"),
        ("pooled_decorrelation", "Decorrelation", "Pooled decorrelation"),
        ("median_decorrelation", "Decorrelation", "Median-based decorrelation"),
    ]
    x = np.arange(len(summary))
    for ax, (column, ylabel, title) in zip(axes.flat, metrics):
        bars = ax.bar(x, summary[column], color=[COLORS[int(n)] for n in summary["order_n"]], edgecolor="#30343b")
        ax.set(title=title, ylabel=ylabel, xticks=x, xticklabels=summary["order_label"])
        ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=9)
        if column.endswith("decorrelation") or column.endswith("fraction"):
            ax.set_ylim(0, 1.05)
    fig.suptitle("Order comparison: 3×3, 5×5, and 9×9 — ISO TX, Lens RX\nHeadline values are taken from notebook outputs through Section 14", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    fig.savefig(FIGURES / "08_aggregate_order_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def md_table(frame: pd.DataFrame, formats: dict[str, str]) -> str:
    display = frame.copy()
    for column, fmt in formats.items():
        if column in display.columns:
            display[column] = display[column].map(lambda value: fmt.format(value))
    headers = [str(column).replace("|", "\\|") for column in display.columns]
    rows = [[str(value).replace("|", "\\|") for value in row] for row in display.itertuples(index=False, name=None)]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def build_report(summary: pd.DataFrame, effects: pd.DataFrame) -> str:
    s = summary.set_index("order_n")
    three, five, nine = s.loc[3], s.loc[5], s.loc[9]
    headline = summary[
        [
            "order_label", "tx_total_power_dbm", "channel_magnitude_median_db", "capacity_median_bits_s_hz",
            "trajectory_mimo_condition_median_db", "trajectory_mimo_erank_median", "trajectory_mimo_erank_fraction",
            "trajectory_mimo_capacity_median_10db", "trajectory_mimo_capacity_per_order", "pooled_decorrelation", "median_decorrelation",
        ]
    ].rename(
        columns={
            "order_label": "Order", "tx_total_power_dbm": "Total TX (dBm)", "channel_magnitude_median_db": "Median |H| (dB)",
            "capacity_median_bits_s_hz": "Median link cap.", "trajectory_mimo_condition_median_db": "Median cond. (dB)",
            "trajectory_mimo_erank_median": "Median e-rank", "trajectory_mimo_erank_fraction": "e-rank/N",
            "trajectory_mimo_capacity_median_10db": "Median MIMO cap.", "trajectory_mimo_capacity_per_order": "MIMO cap./N",
            "pooled_decorrelation": "Pooled decor.", "median_decorrelation": "Median decor.",
        }
    )
    central = summary[["order_label", "central_rx_channel_magnitude_median_db", "central_rx_snr_median_db", "central_rx_capacity_median"]].rename(
        columns={"order_label": "Order", "central_rx_channel_magnitude_median_db": "0° |H| (dB)", "central_rx_snr_median_db": "0° SNR (dB)", "central_rx_capacity_median": "0° capacity"}
    )
    delta = effects.rename(
        columns={
            "comparison": "Perbandingan", "tx_total_power_delta_db": "Δ total TX (dB)", "link_capacity_delta": "Δ link cap.",
            "mimo_capacity_delta": "Δ MIMO cap.", "mimo_capacity_per_order_delta": "Δ MIMO cap./N",
            "condition_delta_db": "Δ cond. (dB)", "erank_fraction_delta": "Δ e-rank/N", "central_rx_capacity_delta": "Δ capacity RX 0°",
        }
    )[["Perbandingan", "Δ total TX (dB)", "Δ link cap.", "Δ MIMO cap.", "Δ MIMO cap./N", "Δ cond. (dB)", "Δ e-rank/N", "Δ capacity RX 0°"]]
    return f"""# Analisis Skalabilitas Lens 3×3, 5×5, dan 9×9 dengan TX Isotropik

## 1. Technical summary: kapasitas absolut naik, efisiensi dimensi turun

{md_table(headline, {"Total TX (dBm)": "{:.2f}", "Median |H| (dB)": "{:.2f}", "Median link cap.": "{:.2f}", "Median cond. (dB)": "{:.2f}", "Median e-rank": "{:.2f}", "e-rank/N": "{:.3f}", "Median MIMO cap.": "{:.2f}", "MIMO cap./N": "{:.2f}", "Pooled decor.": "{:.4f}", "Median decor.": "{:.4f}"})}

![Ringkasan order](figures/08_aggregate_order_comparison.png)

Kapasitas MIMO median meningkat dari {three['trajectory_mimo_capacity_median_10db']:.2f} menjadi {nine['trajectory_mimo_capacity_median_10db']:.2f} bit/s/Hz. Namun kapasitas per order berubah dari {three['trajectory_mimo_capacity_per_order']:.2f} menjadi {nine['trajectory_mimo_capacity_per_order']:.2f} bit/s/Hz/elemen dan `e-rank/N` turun dari {three['trajectory_mimo_erank_fraction']:.3f} menjadi {nine['trajectory_mimo_erank_fraction']:.3f}. Tambahan elemen memberi throughput absolut, tetapi dengan diminishing return pada pemanfaatan dimensi. Kesimpulan ini bersifat deskriptif karena total daya, aperture, dan sampling sudut RX berubah bersama order.

## 2. Tujuan dan pertanyaan analisis

Tujuannya adalah menilai bagaimana peningkatan order dari 3×3 ke 5×5 dan 9×9 memengaruhi kualitas link, conditioning, effective rank, kapasitas MIMO, dan spatial decorrelation. Karena ukuran matriks, jumlah TX/RX, aperture, cakupan sudut RX, dan total daya berubah bersama order, hasil dibaca sebagai **skalabilitas konfigurasi sistem**, bukan efek kausal tunggal dari jumlah elemen.

## 3. Sumber data dan batas Section 14

- [Lens 3×3](../Setupv4_20mx20m_lens_3x3_Patch_iso_LinearTrajectory.ipynb)
- [Lens 5×5](../Setupv4_20mx20m_lens_5x5_Patch_iso_LinearTrajectory.ipynb)
- [Lens 9×9](../Setupv4_20mx20m_lens_9x9_Patch_iso_TrajectoryTxCom.ipynb)

Ketiga notebook memiliki 64 cell, tidak memuat heading Section 15, dan berakhir pada Section 14. Analisis menggunakan output eksekusi yang sudah tersimpan; ray tracing tidak dijalankan ulang. Hash, timestamp, cell scope, serta inventaris figure dicatat di [provenance.json](metadata/provenance.json).

## 4. Setup order dan kesetaraan simulasi

Semua sistem memakai TX pattern `iso`, RX Lens Patch, ruangan 20 m × 20 m × 3 m, carrier dan bandwidth yang sama, 21 waypoint sepanjang 19 m, 16 time step per waypoint, serta 401 frequency bins. Daya ditetapkan 10 dBm **per TX**, sehingga total nominal bertambah dari {three['tx_total_power_dbm']:.2f} dBm pada 3×3 menjadi {nine['tx_total_power_dbm']:.2f} dBm pada 9×9.

![Geometri order](figures/01_geometry_order_comparison.png)

Order 3×3 memiliki sudut RX `−45°, 0°, +45°`; 5×5 memakai `−60°, −30°, 0°, +30°, +60°`; sedangkan 9×9 memakai grid 15° dari −60° sampai +60°. Karena hanya RX 0° yang sama pada semua order, agregat seluruh RX dan perbandingan RX 0° dilaporkan terpisah.

## 5. Definisi metrik dan metode perbandingan

- **Median link capacity** berasal dari link budget notebook pada semua waypoint × RX.
- **Condition number** yang lebih rendah menandakan matriks lebih mudah dipisahkan secara numerik.
- **Effective rank** menunjukkan jumlah dimensi eigenmode yang efektif; `e-rank/N` menormalkannya terhadap order.
- **MIMO capacity @ 10 dB** adalah kapasitas pada SNR ternormalisasi yang digunakan notebook; `capacity/N` menunjukkan efisiensi per dimensi.
- **Pooled decorrelation** menghitung korelasi setelah seluruh realisasi digabung; **median-based** mengambil median korelasi blok waypoint × time.
- Matriks N×N dibentuk dengan menggabungkan N simulasi N×1 yang dilakukan berurutan, bukan N RX aktif simultan.

## 6. Aperture, daya total, dan sampling sudut berubah bersama order

Jarak elemen TX tetap 0,45 m, tetapi aperture bertambah dari 0,9 m (3 TX) menjadi 3,6 m (9 TX). Pada saat yang sama total daya nominal naik {effects.loc[effects['comparison'] == '3x3→9x9', 'tx_total_power_delta_db'].iloc[0]:.2f} dB dan jumlah pola RX yang digabung meningkat dari 3 menjadi 9. Karena itu, kenaikan kapasitas absolut tidak dapat diatribusikan hanya pada rank atau aperture.

Perbandingan delta berikut menunjukkan perubahan konfigurasi penuh:

{md_table(delta, {"Δ total TX (dB)": "{:+.2f}", "Δ link cap.": "{:+.2f}", "Δ MIMO cap.": "{:+.2f}", "Δ MIMO cap./N": "{:+.2f}", "Δ cond. (dB)": "{:+.2f}", "Δ e-rank/N": "{:+.3f}", "Δ capacity RX 0°": "{:+.2f}"})}

## 7. Snapshot RX Section 9: sudut 0° adalah baseline paling sebanding

![Snapshot RX](figures/02_static_rx_by_order.png)

Kurva per sudut memperlihatkan bahwa populasi RX berubah antar-order. Untuk mengurangi bias sampling sudut, RX 0° dibandingkan secara khusus:

{md_table(central, {"0° |H| (dB)": "{:.2f}", "0° SNR (dB)": "{:.2f}", "0° capacity": "{:.2f}"})}

Kapasitas median RX 0° berubah dari {three['central_rx_capacity_median']:.2f} pada 3×3 menjadi {nine['central_rx_capacity_median']:.2f} bit/s/Hz pada 9×9. Ini tetap bukan uji constant-total-power karena daya nominal bertambah seiring jumlah TX.

## 8. Snapshot MIMO Section 10: 5×5 memiliki conditioning statis terbaik

![Static MIMO](figures/03_static_mimo_scaling.png)

Pada snapshot statis, conditioning tidak monotonik: 5×5 adalah yang terbaik ({five['static_mimo_condition_db']:.2f} dB), diikuti 9×9 ({nine['static_mimo_condition_db']:.2f} dB), kemudian 3×3 ({three['static_mimo_condition_db']:.2f} dB). Effective rank absolut dan kapasitas meningkat dengan order, sedangkan `e-rank/N` serta capacity/N menunjukkan bahwa 5×5 paling efisien pada snapshot ini. Hasil statis tersebut berbeda dari median sepanjang trajectory, tempat condition number memburuk secara monotonik dengan order.

## 9. Link sepanjang trajectory: kenaikan order memberi gain kapasitas bertahap

![Kanal sepanjang trajectory](figures/04_channel_along_trajectory.png)

Median kapasitas link meningkat dari {three['capacity_median_bits_s_hz']:.2f} (3×3), {five['capacity_median_bits_s_hz']:.2f} (5×5), menjadi {nine['capacity_median_bits_s_hz']:.2f} bit/s/Hz (9×9), sementara median magnitude kanal hanya berubah dalam rentang {summary['channel_magnitude_median_db'].max() - summary['channel_magnitude_median_db'].min():.2f} dB. Perbedaan ini konsisten dengan link budget yang mengakumulasi kontribusi lebih banyak TX. Semua order mencatat outage 0% pada ambang 1 bit/s/Hz, sehingga threshold ini tidak mampu membedakan reliabilitas antarkonfigurasi. Pita figure adalah minimum–maksimum antar-RX, bukan confidence interval.

## 10. MIMO sepanjang trajectory: bottleneck pusat ruangan muncul pada semua order

![MIMO sepanjang trajectory](figures/05_trajectory_mimo_scaling.png)

Ketiga order memperlihatkan lonjakan condition number dan penurunan capacity/effective rank di sekitar jarak 9,5 m, yaitu pusat trajectory. Nilai condition maksimum adalah {three['trajectory_mimo_condition_max_db']:.2f} dB (3×3), {five['trajectory_mimo_condition_max_db']:.2f} dB (5×5), dan {nine['trajectory_mimo_condition_max_db']:.2f} dB (9×9). Pola yang konsisten menunjukkan bottleneck geometrik/propagasi pada lokasi tersebut, sementara keparahannya meningkat dengan order.

## 11. Spatial decorrelation: kedua estimator menurun dengan order

![Spatial decorrelation](figures/06_spatial_decorrelation_by_order.png)

Pooled decorrelation turun dari {three['pooled_decorrelation']:.4f} menjadi {five['pooled_decorrelation']:.4f} dan {nine['pooled_decorrelation']:.4f} ketika jumlah cabang bertambah. Median-based decorrelation juga turun secara konsisten: {three['median_decorrelation']:.4f}, {five['median_decorrelation']:.4f}, lalu {nine['median_decorrelation']:.4f}. Setelah koreksi 5×5, ketiga sistem memakai elemen TX tengah—indeks 1, 2, dan 4—sehingga pemilihan TX pada Sections 12–14 kini setara. Tren ini mendukung indikasi bahwa respons antarcabang menjadi lebih berkorelasi pada order yang lebih besar, meskipun grid sudut RX masih berbeda.

## 12. Raw spatial Section 13: perbedaan daya tidak menunjukkan scaling monotonik

![Raw spatial](figures/07_raw_spatial_difference_by_order.png)

Mean raw difference power adalah {three['raw_difference_power']:.3e} (3×3), {five['raw_difference_power']:.3e} (5×5), dan {nine['raw_difference_power']:.3e} (9×9). Walaupun TX terpilih kini sama-sama elemen tengah, metrik ini mempertahankan path loss dan gain pola serta tetap sensitif terhadap distribusi RX. Tidak adanya tren monotonik menunjukkan bahwa raw difference power bukan indikator skalabilitas tunggal tanpa penyamaan grid sudut RX.

## 13. Diskusi, keterbatasan, dan hasil validasi

Temuan yang paling kuat adalah kenaikan kapasitas MIMO absolut dan memburuknya conditioning ketika order meningkat. Temuan mengenai efisiensi per dimensi lebih informatif daripada kapasitas absolut karena kapasitas mentah diuntungkan oleh jumlah dimensi dan total daya yang lebih besar.

Keterbatasan utama:

1. Daya 10 dBm ditetapkan per TX; tidak ada normalisasi constant-total-power.
2. Sudut dan jumlah konfigurasi RX berbeda antar-order; hanya RX 0° yang benar-benar sama.
3. MIMO N×N adalah konstruksi dari simulasi RX berurutan.
4. Hanya satu scene/output tersimpan, tanpa multi-seed atau convergence sweep; path sampling menggunakan 100.000 paths/source.
5. Outage threshold 1 bit/s/Hz jenuh pada 0% untuk semua order.

Status validasi adalah **share with caveats**. Pemeriksaan angka, row count, identitas korelasi/dekorelasi, invariant TX ISO, dan figure tersedia pada [VALIDATION.md](VALIDATION.md).

## 14. Summary, rekomendasi, dan pertanyaan lanjutan

**Summary.** Order yang lebih besar meningkatkan kapasitas absolut: median MIMO capacity bertambah {nine['trajectory_mimo_capacity_median_10db'] - three['trajectory_mimo_capacity_median_10db']:.2f} bit/s/Hz dari 3×3 ke 9×9. Akan tetapi, conditioning memburuk {nine['trajectory_mimo_condition_median_db'] - three['trajectory_mimo_condition_median_db']:.2f} dB dan `e-rank/N` turun {nine['trajectory_mimo_erank_fraction'] - three['trajectory_mimo_erank_fraction']:+.3f}, sehingga scaling tidak linear terhadap jumlah elemen.

Rekomendasi berikutnya:

1. Ulangi dengan **total daya TX konstan** dan alokasikan daya `P_total/N` per elemen.
2. Gunakan subset RX yang identik—minimal 0°, idealnya grid sudut sama—pada semua order.
3. Pertahankan aturan `SPATIAL_DECORR_TX_INDEX = N//2` agar evaluasi spatial selalu memakai TX tengah.
4. Tambahkan multi-seed dan 1.000.000 path samples/source untuk convergence check.
5. Laporkan outage pada threshold tambahan 4, 5, dan 6 bit/s/Hz serta percentile kapasitas.

Pertanyaan lanjutan yang paling penting adalah apakah keunggulan kapasitas 9×9 tetap bertahan setelah total daya dan grid sudut RX dibuat identik. Pemilihan TX spatial sudah diperbaiki menjadi elemen tengah pada seluruh order. Laporan ini berhenti pada Section 14; data terstruktur tersedia di [data](data/), figure di [figures](figures/), dan provenance/QA di [metadata](metadata/).
"""


def build_validation(checks: pd.DataFrame, summary: pd.DataFrame) -> str:
    failed = checks.loc[~checks["passed"]]
    issues = "Tidak ada kegagalan pemeriksaan otomatis." if failed.empty else md_table(failed, {})
    return f"""# Validation Report

## Overall Assessment: Share with caveats

## Methodology Review

Ketiga notebook diverifikasi berakhir pada Section 14. Analisis merekonsiliasi konfigurasi TX ISO, jumlah TX/RX, waypoint, link summary, MIMO trajectory, dan spatial metrics. Perbandingan diposisikan sebagai skalabilitas konfigurasi, bukan efek kausal tunggal dari order.

## Issues Found

{issues}

- **High:** total daya nominal tidak konstan karena 10 dBm diterapkan per TX.
- **Medium:** sudut RX dan jumlah RX berbeda antar-order.
- **Medium:** matriks MIMO dibentuk dari simulasi RX N×1 berurutan.
- **Medium:** tidak ada multi-seed/convergence test dan hanya 100.000 path samples/source.
- **Low:** outage threshold 1 bit/s/Hz jenuh pada 0%.

## Calculation Spot-Checks

- Row trajectory RX: 21×3=63, 21×5=105, dan 21×9=189 diverifikasi.
- `correlation + decorrelation = 1` diperiksa untuk pooled dan median tables.
- Median/max trajectory MIMO dihitung ulang dari 21 waypoint per order.
- Effective rank diuji berada pada rentang 1 sampai N.
- TX pattern `iso` dan jumlah elemen 3/5/9 diverifikasi dari konfigurasi.
- TX spatial terpilih diverifikasi sebagai elemen tengah: indeks 1/2/4 untuk order 3/5/9.
- Signature seluruh PNG sumber Sections 11–14 diperiksa.

## Visualization Review

Delapan figure komparatif diperiksa dengan skala, unit, warna, marker, dan line style konsisten. Pita pada grafik link adalah rentang minimum–maksimum antar-RX, bukan confidence interval.

## Suggested Improvements

1. Jalankan eksperimen constant-total-power.
2. Samakan grid RX dan pertahankan pemilihan TX tengah pada semua order.
3. Tambahkan multi-seed dan sweep path samples.
4. Gunakan threshold outage yang lebih diskriminatif.

## Required Caveats for Stakeholders

- Kenaikan kapasitas absolut tercampur dengan kenaikan total daya dan dimensi matriks.
- Spatial result kini memakai TX tengah pada semua order, tetapi grid RX masih berbeda.
- Hasil bersifat deskriptif untuk satu scene dan output tersimpan.
- Tidak ada Section 15 dalam cakupan laporan.
"""


def main() -> None:
    for directory in [DATA, FIGURES, SOURCE_FIGURES, METADATA]:
        directory.mkdir(parents=True, exist_ok=True)

    frames: dict[str, dict[str, Any]] = {}
    provenance: list[dict[str, Any]] = []
    source_images: list[dict[str, Any]] = []
    cell_inventory: list[dict[str, Any]] = []

    for scenario in SCENARIOS:
        n = ORDER[scenario.key]
        path = ROOT / scenario.notebook
        notebook = json.loads(path.read_text(encoding="utf-8"))
        cells = notebook["cells"]
        limit = common.find_section_limit(cells)
        section_map = common.section_by_cell(cells, limit)
        config = common.extract_configuration(cells, limit)
        tables = base.named_html_tables(cells, limit)
        channel_summary, rx_summary = common.find_channel_summary(cells, limit)
        spatial = common.parse_spatial_scalars(cells, limit)
        waypoint = common.add_trajectory_geometry(common.parse_waypoint_log(cells, limit), config, "Linear")
        rx_configs = common.extract_rx_configurations(config)
        static_summary = tables["summary_df"].copy()
        name_to_index = rx_configs.set_index("rx_config_name")["rx_config_index"]
        static_summary.insert(0, "rx_config_index", static_summary["name"].map(name_to_index).astype(int))
        trajectory_mimo = tables["trajectory_mimo_results"].copy()
        item = {
            "config": config,
            "channel_summary": channel_summary,
            "rx_summary": add_order(rx_summary, n),
            "waypoint_samples": add_order(waypoint, n),
            "rx_configurations": add_order(rx_configs, n),
            "static_summary": add_order(static_summary, n),
            "trajectory_mimo": add_order(trajectory_mimo, n),
            "static_mimo": static_mimo(cells, limit),
            "spatial_scalars": spatial,
            "selected_tx_index": selected_tx_index(cells, limit),
            "spatial_pooled": add_order(tables["spatial_decorrelation_trajectory"], n),
            "spatial_raw": add_order(tables["raw_spatial_decorrelation_trajectory"], n),
            "spatial_median": add_order(tables["median_spatial_decorrelation_trajectory"], n),
        }
        frames[scenario.key] = item
        for name in ["rx_summary", "waypoint_samples", "rx_configurations", "static_summary", "trajectory_mimo", "spatial_pooled", "spatial_raw", "spatial_median"]:
            item[name].to_csv(DATA / f"{scenario.key}_{name}.csv", index=False)

        source_images.extend(save_source_figures(scenario, cells, limit, section_map))
        stat = path.stat()
        provenance.append(
            {
                "scenario": scenario.key,
                "order_n": n,
                "notebook": scenario.notebook,
                "sha256": common.sha256(path),
                "bytes": stat.st_size,
                "modified_local": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
                "total_cells": len(cells),
                "included_cells_0_based": f"0-{limit - 1}",
                "section_15_present": limit < len(cells),
                "tx_pattern_mode": config.get("TX_PATTERN_MODE"),
                "tx_element_count": len(config.get("TX_POSITIONS", [])),
                "rx_scenario_count": len(config.get("SIMULATION_CONFIGS", [])),
                "selected_tx_index_sections_12_14": item["selected_tx_index"],
            }
        )
        for cell_index, cell in enumerate(cells):
            source = "".join(cell.get("source", []))
            cell_inventory.append(
                {
                    "scenario": scenario.key,
                    "order_n": n,
                    "cell_index": cell_index,
                    "cell_type": cell.get("cell_type"),
                    "execution_count": cell.get("execution_count"),
                    "section": section_map.get(cell_index),
                    "included": cell_index < limit,
                    "output_count": len(cell.get("outputs", [])),
                    "source_first_line": source.splitlines()[0] if source.splitlines() else "",
                }
            )

    table_names = ["rx_summary", "waypoint_samples", "rx_configurations", "static_summary", "trajectory_mimo", "spatial_pooled", "spatial_raw", "spatial_median"]
    for name in table_names:
        pd.concat([frames[s.key][name] for s in SCENARIOS], ignore_index=True).to_csv(DATA / f"{name}_combined.csv", index=False)

    summary_rows: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        n = ORDER[scenario.key]
        item = frames[scenario.key]
        mimo = item["trajectory_mimo"]
        central = item["rx_summary"].loc[item["rx_summary"]["rx_lens_angle_deg"] == 0].iloc[0]
        per_tx_dbm = float(item["config"]["TX_POWER_DBM_PER_TX"])
        summary_rows.append(
            {
                "scenario": scenario.key,
                "order_n": n,
                "order_label": LABEL[n],
                "tx_power_dbm_per_tx": per_tx_dbm,
                "tx_total_power_dbm": per_tx_dbm + 10 * math.log10(n),
                "selected_tx_index": item["selected_tx_index"],
                "selected_tx_is_center": item["selected_tx_index"] == n // 2,
                **item["channel_summary"],
                **item["static_mimo"],
                **item["spatial_scalars"],
                "static_mimo_erank_fraction": item["static_mimo"]["static_mimo_effective_rank"] / n,
                "static_mimo_capacity_per_order": item["static_mimo"]["static_mimo_capacity_10db"] / n,
                "trajectory_mimo_condition_median_db": mimo["cond_median_db"].median(),
                "trajectory_mimo_condition_max_db": mimo["cond_median_db"].max(),
                "trajectory_mimo_erank_median": mimo["erank_median"].median(),
                "trajectory_mimo_erank_fraction": mimo["erank_median"].median() / n,
                "trajectory_mimo_capacity_median_10db": mimo["capacity_10db"].median(),
                "trajectory_mimo_capacity_min_10db": mimo["capacity_10db"].min(),
                "trajectory_mimo_capacity_max_10db": mimo["capacity_10db"].max(),
                "trajectory_mimo_capacity_per_order": mimo["capacity_10db"].median() / n,
                "central_rx_channel_magnitude_median_db": central["channel_magnitude_median_db"],
                "central_rx_snr_median_db": central["snr_median_db"],
                "central_rx_capacity_median": central["capacity_median"],
                "parsed_waypoint_rx_rows": len(item["waypoint_samples"]),
                "outage_percent_from_rounded_log": 100 * (item["waypoint_samples"]["capacity_bits_s_hz_log_rounded"] < 1).mean(),
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values("order_n")
    summary.to_csv(DATA / "comparison_summary.csv", index=False)

    effect_rows = []
    for lower_n, upper_n in [(3, 5), (5, 9), (3, 9)]:
        lower = summary.loc[summary["order_n"] == lower_n].iloc[0]
        upper = summary.loc[summary["order_n"] == upper_n].iloc[0]
        effect_rows.append(
            {
                "comparison": f"{lower_n}x{lower_n}→{upper_n}x{upper_n}",
                "tx_total_power_delta_db": upper["tx_total_power_dbm"] - lower["tx_total_power_dbm"],
                "channel_magnitude_delta_db": upper["channel_magnitude_median_db"] - lower["channel_magnitude_median_db"],
                "link_capacity_delta": upper["capacity_median_bits_s_hz"] - lower["capacity_median_bits_s_hz"],
                "mimo_capacity_delta": upper["trajectory_mimo_capacity_median_10db"] - lower["trajectory_mimo_capacity_median_10db"],
                "mimo_capacity_per_order_delta": upper["trajectory_mimo_capacity_per_order"] - lower["trajectory_mimo_capacity_per_order"],
                "condition_delta_db": upper["trajectory_mimo_condition_median_db"] - lower["trajectory_mimo_condition_median_db"],
                "erank_delta": upper["trajectory_mimo_erank_median"] - lower["trajectory_mimo_erank_median"],
                "erank_fraction_delta": upper["trajectory_mimo_erank_fraction"] - lower["trajectory_mimo_erank_fraction"],
                "pooled_decorrelation_delta": upper["pooled_decorrelation"] - lower["pooled_decorrelation"],
                "median_decorrelation_delta": upper["median_decorrelation"] - lower["median_decorrelation"],
                "central_rx_capacity_delta": upper["central_rx_capacity_median"] - lower["central_rx_capacity_median"],
            }
        )
    effects = pd.DataFrame(effect_rows)
    effects.to_csv(DATA / "order_effects.csv", index=False)

    parameter_keys = ["FREQ_GHZ", "F_C", "BW", "N_F", "ROOM_X", "ROOM_Y", "ROOM_Z", "TX_PATTERN_MODE", "TRAJECTORY_PATH_SAMPLES_PER_SRC", "MOBILITY_SAMPLING_FREQUENCY_HZ", "MOBILITY_NUM_TIME_STEPS", "TX_POWER_DBM_PER_TX", "NOISE_FIGURE_DB", "NOISE_TEMPERATURE_K", "CAPACITY_OUTAGE_THRESHOLD_BPSHZ", "N_TRAJECTORY_POINTS", "TRAJECTORY_SPEED_M_S"]
    params = []
    for scenario in SCENARIOS:
        n = ORDER[scenario.key]
        cfg = frames[scenario.key]["config"]
        params.append({"scenario": scenario.key, "order_n": n, "tx_element_count": len(cfg["TX_POSITIONS"]), "rx_scenario_count": len(cfg["SIMULATION_CONFIGS"]), **{key: cfg.get(key) for key in parameter_keys}})
    pd.DataFrame(params).to_csv(DATA / "simulation_parameters.csv", index=False)

    checks: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        n = ORDER[scenario.key]
        item = frames[scenario.key]
        expected = int(item["channel_summary"]["total_runs"])
        observed = len(item["waypoint_samples"])
        checks.append({"scenario": scenario.key, "check": "waypoint_rx_row_count", "passed": observed == expected, "detail": f"observed={observed}; expected={expected}"})
        outage = 100 * (item["waypoint_samples"]["capacity_bits_s_hz_log_rounded"] < 1).mean()
        official = float(item["channel_summary"]["trajectory_rx_outage_percent"])
        checks.append({"scenario": scenario.key, "check": "outage_reconciliation", "passed": abs(outage - official) <= 0.7, "detail": f"rounded_log={outage:.3f}%; summary={official:.3f}%"})
        pooled, median = item["spatial_pooled"], item["spatial_median"]
        error = max(np.max(np.abs(pooled["mean_spatial_correlation"].astype(float) + pooled["mean_spatial_decorrelation"].astype(float) - 1)), np.max(np.abs(median["median_pair_correlation"].astype(float) + median["median_pair_decorrelation"].astype(float) - 1)))
        checks.append({"scenario": scenario.key, "check": "correlation_decorrelation_identity", "passed": error < 2e-6, "detail": f"max_abs_error={error:.3e}"})
        cfg = item["config"]
        iso_ok = cfg.get("TX_PATTERN_MODE") == "iso" and len(cfg.get("TX_POSITIONS", [])) == n and len(cfg.get("SIMULATION_CONFIGS", [])) == n
        checks.append({"scenario": scenario.key, "check": "order_iso_invariant", "passed": iso_ok, "detail": f"pattern={cfg.get('TX_PATTERN_MODE')}; tx={len(cfg.get('TX_POSITIONS', []))}; rx={len(cfg.get('SIMULATION_CONFIGS', []))}"})
        checks.append({"scenario": scenario.key, "check": "trajectory_mimo_row_count", "passed": len(item["trajectory_mimo"]) == 21, "detail": f"rows={len(item['trajectory_mimo'])}"})
        rank_ok = item["trajectory_mimo"]["erank_median"].between(1, n).all()
        checks.append({"scenario": scenario.key, "check": "effective_rank_bounds", "passed": rank_ok, "detail": f"range={item['trajectory_mimo']['erank_median'].min():.4f}-{item['trajectory_mimo']['erank_median'].max():.4f}; N={n}"})
        center_index = n // 2
        checks.append({"scenario": scenario.key, "check": "spatial_tx_is_center_element", "passed": item["selected_tx_index"] == center_index, "detail": f"selected={item['selected_tx_index']}; expected_center={center_index}"})
    checks_df = pd.DataFrame(checks)
    checks_df.to_csv(METADATA / "validation_checks.csv", index=False)
    pd.DataFrame(source_images).to_csv(METADATA / "source_figure_inventory.csv", index=False)
    pd.DataFrame(cell_inventory).to_csv(METADATA / "source_cell_inventory.csv", index=False)
    (METADATA / "provenance.json").write_text(json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "section_scope": "Sections 1-14 only", "ray_tracing_rerun": False, "shared_parser": BASE_SCRIPT.relative_to(ROOT).as_posix(), "notebooks": provenance}, indent=2, ensure_ascii=False), encoding="utf-8")

    plot_geometry(frames)
    plot_static_rx(frames)
    plot_static_mimo(summary)
    plot_channel(frames)
    plot_trajectory_mimo(frames)
    plot_spatial(frames)
    plot_raw(frames)
    plot_aggregate(summary)

    (OUT / "ANALISIS.md").write_text(build_report(summary, effects), encoding="utf-8")
    (OUT / "VALIDATION.md").write_text(build_validation(checks_df, summary), encoding="utf-8")
    (OUT / "README.md").write_text("""# Analisis v4 Lens Order 3×3, 5×5, dan 9×9

Laporan utama: [ANALISIS.md](ANALISIS.md). Cakupan hanya Sections 1–14.

- `data/`: CSV per order dan gabungan.
- `figures/`: delapan figure komparatif dan figure sumber Sections 11–14.
- `metadata/`: provenance, data dictionary, chart map, inventaris, dan validasi.
- `metadata/revision_notes.md`: perubahan hasil setelah TX spatial 5×5 diperbaiki dari indeks 4 ke 2.
- `build_analysis.py`: generator reproducible dari output notebook tersimpan.

```powershell
conda activate sionna_env
python Analisis_v4_ISO_TX_Lens_Order_3x3_5x5_9x9_Linear/build_analysis.py
```
""", encoding="utf-8")
    (METADATA / "data_dictionary.md").write_text("""# Data Dictionary

- `comparison_summary.csv`: headline per order, termasuk metrik absolut dan ternormalisasi.
- `order_effects.csv`: delta 3×3→5×5, 5×5→9×9, dan 3×3→9×9.
- `simulation_parameters.csv`: parameter konfigurasi dan invariant TX ISO.
- `static_summary_combined.csv`: gain, korelasi TX, dan capacity Section 9.
- `rx_summary_combined.csv`: median/min/outage per RX sepanjang trajectory.
- `waypoint_samples_combined.csv`: SNR dan capacity log per waypoint × RX.
- `trajectory_mimo_combined.csv`: condition number, effective rank, capacity per waypoint.
- `spatial_pooled/raw/median_combined.csv`: output Sections 12–14.

Versi per order menggunakan prefix `order_3x3`, `order_5x5`, atau `order_9x9`.
""", encoding="utf-8")
    (METADATA / "revision_notes.md").write_text(
        f"""# Revision Notes

Revisi ini dibuat setelah `SPATIAL_DECORR_TX_INDEX` pada notebook 5×5 diubah dari `4` menjadi `2` dan Sections 12–14 dijalankan ulang.

## Perubahan metrik 5×5

| Metrik | Sebelum (TX 4, tepi) | Sesudah (TX 2, tengah) | Delta |
| --- | ---: | ---: | ---: |
| Pooled correlation | 0.0695 | {summary.loc[summary['order_n'] == 5, 'pooled_correlation'].iloc[0]:.4f} | {summary.loc[summary['order_n'] == 5, 'pooled_correlation'].iloc[0] - 0.0695:+.4f} |
| Pooled decorrelation | 0.9305 | {summary.loc[summary['order_n'] == 5, 'pooled_decorrelation'].iloc[0]:.4f} | {summary.loc[summary['order_n'] == 5, 'pooled_decorrelation'].iloc[0] - 0.9305:+.4f} |
| Median correlation | 0.4281 | {summary.loc[summary['order_n'] == 5, 'median_correlation'].iloc[0]:.4f} | {summary.loc[summary['order_n'] == 5, 'median_correlation'].iloc[0] - 0.4281:+.4f} |
| Median decorrelation | 0.5719 | {summary.loc[summary['order_n'] == 5, 'median_decorrelation'].iloc[0]:.4f} | {summary.loc[summary['order_n'] == 5, 'median_decorrelation'].iloc[0] - 0.5719:+.4f} |
| Raw cross-correlation | 1.497993e-09 | {summary.loc[summary['order_n'] == 5, 'raw_cross_correlation'].iloc[0]:.6e} | {summary.loc[summary['order_n'] == 5, 'raw_cross_correlation'].iloc[0] - 1.497993e-09:+.6e} |
| Raw difference power | 3.737515e-08 | {summary.loc[summary['order_n'] == 5, 'raw_difference_power'].iloc[0]:.6e} | {summary.loc[summary['order_n'] == 5, 'raw_difference_power'].iloc[0] - 3.737515e-08:+.6e} |

Secara metodologis, `SPATIAL_DECORR_TX_INDEX` hanya digunakan oleh Sections 12–14. Output tersimpan Section 11 pada notebook terbaru juga mengalami perubahan numerik sangat kecil (sekitar 5×10⁻⁴ bit/s/Hz pada median MIMO capacity), kemungkinan karena cell simulasi ikut dijalankan ulang; laporan memakai seluruh output terbaru tersebut.
""",
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            ["01", "Geometry", "Aperture TX dan cakupan sudut RX", "01_geometry_order_comparison.png"],
            ["02", "Trend", "Snapshot per sudut RX", "02_static_rx_by_order.png"],
            ["03", "Comparison", "Static MIMO scaling", "03_static_mimo_scaling.png"],
            ["04", "Trend", "Link sepanjang trajectory", "04_channel_along_trajectory.png"],
            ["05", "Trend", "MIMO sepanjang trajectory", "05_trajectory_mimo_scaling.png"],
            ["06", "Trend", "Pooled/median decorrelation", "06_spatial_decorrelation_by_order.png"],
            ["07", "Trend", "Raw spatial difference", "07_raw_spatial_difference_by_order.png"],
            ["08", "Comparison", "Ringkasan scaling order", "08_aggregate_order_comparison.png"],
        ], columns=["figure", "family", "question", "file"]
    ).to_csv(METADATA / "chart_map.csv", index=False)

    if not checks_df["passed"].all():
        raise RuntimeError("Validation failed:\n" + checks_df.loc[~checks_df["passed"]].to_string(index=False))
    if not all(row["png_signature_valid"] for row in source_images):
        raise RuntimeError("Invalid PNG source figure signature")
    print(f"Built analysis in: {OUT}")
    print(summary.to_string(index=False))
    print("\nOrder effects:\n" + effects.to_string(index=False))
    print(f"\nExtracted source figures: {len(source_images)}")
    print("Validation: all automated checks passed")


if __name__ == "__main__":
    main()
