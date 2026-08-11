"""Display the exported full-360-degree vertical-cut graph and numerical data.

Run from the project root after activating the required environment:

    conda activate sionna_env
    python AntennaLensRadiationPatternOutput/vertical_cut_360/show_vertical_cut_360.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "vertical_cut_360_all_patterns.csv"
FIGURE_DIR = BASE_DIR / "figures"
OUTPUT_FIGURE = FIGURE_DIR / "vertical_cut_360_all_patterns_from_script.png"


def main() -> None:
    if not DATA_FILE.is_file():
        raise FileNotFoundError(
            f"Exported data was not found at {DATA_FILE}. "
            "Run cell '6a. Export the full 360° vertical-cut graphs and data' "
            "in AntennaLensRadiationPattern.ipynb first."
        )

    vertical_cut_data = pd.read_csv(DATA_FILE)
    required_columns = {
        "scenario",
        "lens_angle_deg",
        "vertical_angle_deg",
        "theta_deg",
        "phi_deg",
        "gain_db",
    }
    missing_columns = required_columns.difference(vertical_cut_data.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    print("\nFull 360° vertical-cut data")
    print("=" * 90)
    print(vertical_cut_data.to_string(index=False))

    scenarios = (
        vertical_cut_data[["scenario", "lens_angle_deg"]]
        .drop_duplicates()
        .sort_values("lens_angle_deg")
    )
    colors = plt.cm.coolwarm(np.linspace(0.0, 1.0, len(scenarios)))

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"projection": "polar"})
    for (_, scenario_row), color in zip(scenarios.iterrows(), colors):
        scenario_name = scenario_row["scenario"]
        scenario_data = vertical_cut_data.loc[
            vertical_cut_data["scenario"] == scenario_name
        ].sort_values("vertical_angle_deg")
        ax.plot(
            np.deg2rad(scenario_data["vertical_angle_deg"]),
            scenario_data["gain_db"],
            color=color,
            linewidth=1.4,
            label=scenario_name,
        )

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_xticks(np.deg2rad(np.arange(0, 360, 45)))
    ax.set_xticklabels(
        ["+Z", "45°", "+X", "135°", "-Z", "225°", "-X", "315°"]
    )
    ax.set_title(
        "Full 360° Vertical Cut (X-Z Plane) — All Lens Angles",
        pad=20,
    )
    ax.grid(True, alpha=0.35)
    ax.legend(fontsize=8, loc="upper right", bbox_to_anchor=(1.35, 1.10))

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_FIGURE, dpi=220, bbox_inches="tight")
    print(f"\nGraph saved to: {OUTPUT_FIGURE}")
    plt.show()


if __name__ == "__main__":
    main()
