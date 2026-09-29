"""Generate Figure 3 and Supplementary Figures 7–9 from processed scenario data."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "analysis" / "data" / "processed" / "scenarios"
CONFIG_DIR = ROOT / "analysis" / "config"
LABELS = json.loads((CONFIG_DIR / "figure_03_scenario_labels.json").read_text())
LABEL_POSITIONS = json.loads((CONFIG_DIR / "figure_03_label_positions.json").read_text())

SETTINGS = {
    "004": (47, "figure-03.png"),
    "005": (10, "supplementary-figure-07.png"),
    "006": (47, "supplementary-figure-08.png"),
    "007": (10, "supplementary-figure-09.png"),
}
REQUIRED_COLUMNS = {"scenario", "total_treatmentfailures", "al_used"}


def population_al_use(data: pd.DataFrame, setting: str, private_share: int) -> pd.DataFrame:
    path = DATA_DIR / setting / "al_used.csv"
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {', '.join(sorted(missing))}")
    result = data.copy()
    private_al_use = private_share * 0.78
    public_al_use = (100 - private_share) * result["al_used"] / 100
    result["al_used"] = (private_al_use + public_al_use).round(1)
    return result


def darken(color: str, factor: float = 0.85) -> tuple[float, float, float]:
    return tuple(channel * factor for channel in mcolors.to_rgb(color))


def add_extreme_labels(ax, data: pd.DataFrame, setting: str, palette: dict[str, tuple]) -> None:
    medians = data.groupby(["al_used", "scenario"], observed=True)["total_treatmentfailures"].median().reset_index()
    mins = data.groupby("al_used", observed=True)["total_treatmentfailures"].min()
    maxs = data.groupby("al_used", observed=True)["total_treatmentfailures"].max()
    levels = sorted(data["al_used"].unique())
    x_index = {value: index for index, value in enumerate(levels)}

    for al_value, group in medians.groupby("al_used", observed=True):
        low = group.loc[group["total_treatmentfailures"].idxmin()]
        high = group.loc[group["total_treatmentfailures"].idxmax()]
        for row, extreme in ((low, "min"), (high, "max")):
            scenario = row["scenario"]
            label = LABELS.get(scenario, {}).get("label", scenario)
            label = label.replace("\\n", "\n")
            override = LABEL_POSITIONS.get(setting, {}).get(scenario)
            if override:
                x, y = override["x_pos"], override["y_pos"]
            else:
                x = x_index[al_value]
                y = mins.loc[al_value] if extreme == "min" else maxs.loc[al_value]
            ax.text(
                x, y, label,
                ha="center", va="center", fontsize=9,
                color=darken(palette.get(scenario, "black")),
                bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.6},
                clip_on=True,
            )


def make_plot(setting: str, private_share: int, filename: str) -> Path:
    source = DATA_DIR / setting / "al_used.csv"
    raw = pd.read_csv(source)
    data = population_al_use(raw, setting, private_share)
    if "scenario" not in data:
        raise ValueError(f"{source} has no scenario column")
    data["al_used_label"] = data["al_used"].map(lambda value: f"{value:.1f}%")
    ordered_labels = sorted(data["al_used_label"].unique(), key=lambda x: float(x.rstrip("%")))
    data["al_used_label"] = pd.Categorical(data["al_used_label"], categories=ordered_labels, ordered=True)

    scenario_order = (
        data[["scenario", "al_used"]].drop_duplicates()
        .sort_values(["al_used", "scenario"])["scenario"].tolist()
    )
    colors = sns.color_palette("colorblind", n_colors=len(scenario_order))
    palette = dict(zip(scenario_order, colors))

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.boxenplot(data=data, x="al_used_label", y="total_treatmentfailures", order=ordered_labels, ax=ax)
    sns.stripplot(
        data=data, x="al_used_label", y="total_treatmentfailures",
        order=ordered_labels, hue="scenario", hue_order=scenario_order,
        palette=palette, dodge=False, alpha=0.35, size=4, jitter=True, ax=ax,
    )
    add_extreme_labels(ax, data, setting, palette)
    ax.set_xlabel("Percentage of malaria cases treated with artemether–lumefantrine", fontsize=11)
    ax.set_ylabel("Projected average monthly treatment failures from 2026 to 2032", fontsize=11)
    legend = ax.get_legend()
    if legend is not None:
        legend.remove()
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)

    destination_dir = ROOT / "figures" / ("main" if setting == "004" else "supplementary")
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / filename
    fig.savefig(destination, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return destination


def main() -> None:
    for setting, (private_share, filename) in SETTINGS.items():
        destination = make_plot(setting, private_share, filename)
        print(f"Saved {destination}")


if __name__ == "__main__":
    main()
