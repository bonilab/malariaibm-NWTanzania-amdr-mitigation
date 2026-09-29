"""Generate Figure 5 and Supplementary Figures 13–15."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "analysis" / "data" / "processed" / "scenarios"
SCENARIO_LABELS = [
    "Immediate ASAQ",
    "1 year delay",
    "2 year delay",
    "3 year delay",
    "4 year delay",
]
SCENARIO_IDS = [
    "001-basic-ASAQ",
    "098-Delay-ASAQ-1y",
    "099-Delay-ASAQ-2y",
    "100-Delay-ASAQ-3y",
    "101-Delay-ASAQ-4y",
]
DESCRIPTION = {
    "004": "47% Private Market - Normal 7686",
    "005": "10% Private Market - Normal 7686",
    "006": "47% Private Market - Lower 7686",
    "007": "10% Private Market - Lower 7686",
}
OUTPUT = {
    "004": "figures/main/figure-05.png",
    "005": "figures/supplementary/supplementary-figure-13.png",
    "006": "figures/supplementary/supplementary-figure-14.png",
    "007": "figures/supplementary/supplementary-figure-15.png",
}


def load_monthly_data(setting: str) -> pd.DataFrame:
    path = DATA_DIR / setting / "all_monthly_data.csv.xz"
    columns = ["scenario", "run", "date", "total_treatmentfailures", "k13_frequency"]
    data = pd.read_csv(path, usecols=columns, parse_dates=["date"])
    data["scenario"] = data["scenario"].str.split("/", n=1).str[-1]
    data = data.loc[data["scenario"].isin(SCENARIO_IDS)].copy()
    if data.empty:
        raise ValueError(f"No delayed-ASAQ scenarios found in {path}")
    return data.sort_values(["scenario", "run", "date"])


def add_rolling_failure_panel(ax, data: pd.DataFrame, colors: dict[str, tuple]) -> None:
    data = data.copy()
    data["rolling_failure"] = data.groupby(["scenario", "run"])["total_treatmentfailures"].transform(
        lambda values: values.rolling(window=12, min_periods=12).mean()
    )
    data = data.loc[
        (data["date"] >= "2020-01-01") & (data["date"] <= "2032-01-01")
    ]
    summary = (
        data.groupby(["scenario", "date"], observed=True)["rolling_failure"]
        .agg(mean="mean", low=lambda values: values.quantile(0.05), high=lambda values: values.quantile(0.95))
        .reset_index()
    )
    for scenario in SCENARIO_IDS:
        values = summary.loc[summary["scenario"] == scenario]
        color = colors[scenario]
        ax.plot(values["date"], values["mean"], color=color, linewidth=1.8)
        ax.fill_between(values["date"], values["low"], values["high"], color=color, alpha=0.16, linewidth=0)
    ax.set_xlabel("Year")
    ax.set_ylabel("12-Month Rolling Mean of\nTreatment Failures")
    ax.set_xlim(pd.Timestamp("2020-01-01"), pd.Timestamp("2032-01-01"))


def add_frequency_panel(ax, data: pd.DataFrame, colors: dict[str, tuple]) -> None:
    data = data.loc[(data["date"] >= "2020-01-01") & (data["date"] <= "2032-01-01")]
    summary = (
        data.groupby(["scenario", "date"], observed=True)["k13_frequency"]
        .agg(mean="mean", low=lambda values: values.quantile(0.05), high=lambda values: values.quantile(0.95))
        .reset_index()
    )
    for scenario in SCENARIO_IDS:
        values = summary.loc[summary["scenario"] == scenario]
        color = colors[scenario]
        ax.plot(values["date"], values["mean"], color=color, linewidth=1.8)
        ax.fill_between(values["date"], values["low"], values["high"], color=color, alpha=0.16, linewidth=0)
    ax.set_xlabel("Year")
    ax.set_ylabel("K13 Frequency")
    ax.set_xlim(pd.Timestamp("2020-01-01"), pd.Timestamp("2032-01-01"))
    ax.set_ylim(0, 1)


def add_boxplot_panel(ax, data: pd.DataFrame, colors: dict[str, tuple], value_column: str, xlabel: str) -> None:
    grouped = [data.loc[data["scenario"] == scenario, value_column].dropna().to_numpy() for scenario in SCENARIO_IDS]
    artists = ax.boxplot(
        grouped,
        orientation="horizontal",
        patch_artist=True,
        tick_labels=SCENARIO_LABELS,
        medianprops={"color": "black", "linewidth": 1.5},
    )
    # Match seaborn's categorical orientation in the source notebook: the first
    # scenario is shown at the top, followed by the four delays in order.
    ax.invert_yaxis()
    for box, scenario in zip(artists["boxes"], SCENARIO_IDS):
        box.set_facecolor(colors[scenario])
        box.set_alpha(0.9)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")


def make_figure(setting: str) -> Path:
    data = load_monthly_data(setting)
    palette = sns.color_palette("tab10", n_colors=len(SCENARIO_IDS))
    colors = dict(zip(SCENARIO_IDS, palette))

    fig, axes = plt.subplots(2, 2, figsize=(12, 6))
    ax1, ax2 = axes[0, 0], axes[0, 1]
    add_rolling_failure_panel(ax1, data, colors)
    add_frequency_panel(ax2, data, colors)

    evaluation = data.loc[
        (data["date"] >= "2026-01-01") & (data["date"] < "2032-01-01")
    ]
    monthly = evaluation.groupby(["scenario", "run"], as_index=False)["total_treatmentfailures"].sum()
    month_counts = evaluation.groupby(["scenario", "run"])["date"].nunique()
    if not month_counts.eq(72).all():
        raise ValueError(f"Expected 72 intervention months per run in scenario {setting}")
    monthly["monthly_failures"] = monthly["total_treatmentfailures"] / 72
    ax3, ax4 = axes[1, 0], axes[1, 1]
    add_boxplot_panel(
        ax3, monthly, colors, "monthly_failures",
        "Average Monthly Treatment Failures\n(Over 6 Years)",
    )
    add_boxplot_panel(
        ax4, data.loc[data["date"] == "2032-01-01"], colors, "k13_frequency", "K13 Frequency in 2031"
    )
    ax3.set_xlim(
        max(0, monthly["monthly_failures"].min() - 1000),
        monthly["monthly_failures"].max() + 1000,
    )
    ax4.set_xlim((0.5, 1) if setting in {"004", "006"} else (0.2, 1))

    handles = [Patch(facecolor=colors[scenario], label=label) for scenario, label in zip(SCENARIO_IDS, SCENARIO_LABELS)]
    fig.legend(handles=handles, title="Scenario", loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=5)
    for ax, label in zip(axes.flatten(), "ABCD"):
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        ax.text(0.98, 0.98, label, transform=ax.transAxes, ha="right", va="top", fontsize=10, fontweight="bold")

    fig.suptitle(f"Impact of Delaying ASAQ Deployment in Tanzania - {DESCRIPTION[setting]}", fontsize=16)
    fig.tight_layout()
    destination = ROOT / OUTPUT[setting]
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, bbox_inches="tight", dpi=200)
    plt.close(fig)
    return destination


def main() -> None:
    for setting in OUTPUT:
        print(f"Saved {make_figure(setting)}")


if __name__ == "__main__":
    main()
