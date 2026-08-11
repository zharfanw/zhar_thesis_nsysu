"""Display and save the exported 3D transmitarray acquisition geometry."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FIGURE_DIR = BASE_DIR / "figures"
ELEMENT_FILE = DATA_DIR / "transmitarray_elements.csv"
REFERENCE_FILE = DATA_DIR / "geometry_references.csv"
OUTPUT_FIGURE = FIGURE_DIR / "transmitarray_acquisition_geometry_3d_from_script.png"

X_LIMITS = (-5.0, 5.0)
Y_LIMITS = (-30.0, 20.0)
Z_LIMITS = (0.0, 55.0)


def reference_vector(reference_data: pd.DataFrame, name: str) -> np.ndarray:
    row = reference_data.loc[reference_data["name"] == name]
    if len(row) != 1:
        raise ValueError(f"Expected one geometry reference named {name!r}")
    return row[["x", "y", "z"]].iloc[0].to_numpy(dtype=float)


def direction_vector(reference_data: pd.DataFrame, name: str) -> np.ndarray:
    row = reference_data.loc[reference_data["name"] == name]
    if len(row) != 1:
        raise ValueError(f"Expected one geometry vector named {name!r}")
    return row[["dx", "dy", "dz"]].iloc[0].to_numpy(dtype=float)


def main() -> None:
    if not ELEMENT_FILE.is_file() or not REFERENCE_FILE.is_file():
        raise FileNotFoundError(
            "3D geometry data is missing. Run the 3D visualization cell in "
            "AntennaLensRadiationPattern.ipynb first."
        )

    elements = pd.read_csv(ELEMENT_FILE)
    references = pd.read_csv(REFERENCE_FILE)
    array_center = reference_vector(references, "array_center")
    feed_position = reference_vector(references, "feed")
    selected_element = reference_vector(references, "selected_element")
    main_beam = direction_vector(references, "main_beam")
    observation = direction_vector(references, "observation")

    print("\nTransmitarray elements")
    print("=" * 72)
    print(elements.to_string(index=False))
    print("\nGeometry references")
    print("=" * 72)
    print(references.to_string(index=False))

    x_values = np.sort(elements["x"].unique())
    y_values = np.sort(elements["y"].unique())
    x_grid, y_grid = np.meshgrid(x_values, y_values)
    z_grid = np.full_like(x_grid, elements["z"].iloc[0], dtype=float)

    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(
        x_grid,
        y_grid,
        z_grid,
        color="lightsteelblue",
        alpha=0.22,
        edgecolor="steelblue",
        linewidth=0.35,
    )
    ax.scatter(
        elements["x"],
        elements["y"],
        elements["z"],
        s=18,
        color="navy",
        alpha=0.85,
        label=f"Transmitarray elements ({len(y_values)} x {len(x_values)})",
    )
    ax.scatter(*feed_position, s=150, marker="D", color="tab:red", label="Feed")
    ax.scatter(
        *selected_element,
        s=95,
        marker="s",
        color="black",
        label="Selected (m,n) element",
    )
    ax.plot(
        [feed_position[0], selected_element[0]],
        [feed_position[1], selected_element[1]],
        [feed_position[2], selected_element[2]],
        color="tab:red",
        linewidth=1.8,
        label="Feed path",
    )
    ax.quiver(
        *array_center,
        *main_beam,
        color="tab:orange",
        linewidth=2.8,
        arrow_length_ratio=0.08,
        label="Main beam",
    )
    ax.quiver(
        *array_center,
        *observation,
        color="tab:green",
        linewidth=2.3,
        arrow_length_ratio=0.09,
        label="Observation direction",
    )

    beam_length = np.linalg.norm(main_beam)
    beam_axis = main_beam / beam_length
    beam_basis_1 = np.array([1.0, 0.0, 0.0])
    beam_basis_2 = np.cross(beam_axis, beam_basis_1)
    beam_basis_2 /= np.linalg.norm(beam_basis_2)
    beam_distance = np.linspace(0.0, 0.82 * beam_length, 36)
    beam_azimuth = np.linspace(0.0, 2.0 * np.pi, 48)
    beam_radius = 0.14 * beam_distance
    beam_points = (
        array_center[:, None, None]
        + beam_axis[:, None, None] * beam_distance[None, :, None]
        + beam_radius[None, :, None]
        * (
            beam_basis_1[:, None, None]
            * np.cos(beam_azimuth)[None, None, :]
            + beam_basis_2[:, None, None]
            * np.sin(beam_azimuth)[None, None, :]
        )
    )
    ax.plot_surface(
        beam_points[0],
        beam_points[1],
        beam_points[2],
        color="tab:orange",
        alpha=0.16,
        linewidth=0,
        shade=True,
    )

    ax.set_xlim(*X_LIMITS)
    ax.set_ylim(*Y_LIMITS)
    ax.set_zlim(*Z_LIMITS)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_box_aspect(
        (
            X_LIMITS[1] - X_LIMITS[0],
            Y_LIMITS[1] - Y_LIMITS[0],
            Z_LIMITS[1] - Z_LIMITS[0],
        )
    )
    ax.set_title("3D Transmitarray Radiation-Pattern Acquisition Geometry", pad=16)
    ax.view_init(elev=23, azim=-58)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_FIGURE, dpi=220, bbox_inches="tight")
    print(f"\nGraph saved to: {OUTPUT_FIGURE}")
    plt.show()


if __name__ == "__main__":
    main()
