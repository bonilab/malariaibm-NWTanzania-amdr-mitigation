"""Generate Figure 4 and Supplementary Figure 10."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "analysis" / "data" / "processed" / "scenarios"
LABELS = json.loads((ROOT / "analysis/config/figure_04_strategy_labels.json").read_text())
HIGH_DHAPPQ_SCENARIOS = {
    "002-basic-DHAPPQ",
    "019-Cycling-2y-DHAPPQ-AL",
    "020-Cycling-2y-DHAPPQ-ASAQ",
    "043-Cycling-4y-DHAPPQ-AL",
    "044-Cycling-4y-DHAPPQ-ASAQ",
    "049-Cycling-4y-DHAPPQ-AL-ASAQ",
    "050-Cycling-4y-DHAPPQ-ASAQ-AL",
    "052-mft-AL25-DHAPPQ75",
    "053-mft-ASAQ25-DHAPPQ75",
    "063-tact-DHAPPQ4y-ALAQ",
    "095-region-specific-Kagera-DHAPPQ-Others-ASAQ-Delay-0y",
    "096-region-specific-Kagera-DHAPPQ-Others-ASAQ-Delay-1y",
    "097-region-specific-Kagera-DHAPPQ-Others-ASAQ-Delay-2y",
}


def format_labels(rows: list[list[str]]) -> list[str]:
    nonempty = [row for row in rows if row]
    if not nonempty:
        return []
    first_col_width = max(len(row[0]) for row in nonempty) + 1
    cell_width = 15
    formatted = []
    for row in rows:
        if not row:
            formatted.append("")
            continue
        line = f"{row[0]:<{first_col_width}} "
        rest_cells = [f"{item:<{cell_width}}" for item in row[1:5]]
        rest_cells.extend([" " * cell_width] * (4 - len(rest_cells)))
        line += "".join(rest_cells)
        if line.startswith("Kagera"):
            line = line[:-7]
        formatted.append(line)
    return formatted


def load_scenario_csv(setting: str, filename: str, value_column: str) -> pd.DataFrame:
    path = DATA_DIR / setting / filename
    data = pd.read_csv(path)
    required = {"scenario", value_column}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {', '.join(sorted(missing))}")
    data["scenario_clean"] = data["scenario"].str.replace(r"^\d+/", "", regex=True)
    return data.loc[data["scenario_clean"].isin(LABELS)].copy()


def treatment_failure_summary(data: pd.DataFrame) -> pd.DataFrame:
    summary = (
        data.groupby(["scenario_clean", "year"])["total_treatmentfailures"]
        .agg(
            median="median",
            q1=lambda values: np.percentile(values, 25),
            q3=lambda values: np.percentile(values, 75),
        )
        .reset_index()
    )
    baseline = summary.loc[
        summary["scenario_clean"] == "000-status-quo", ["year", "median"]
    ].rename(columns={"median": "baseline_median"})
    summary = summary.merge(baseline, on="year", how="left", validate="many_to_one")
    if summary["baseline_median"].isna().any():
        raise ValueError("Status quo baseline is missing for one or more years")
    summary["relative_change_pct"] = (
        100 * (summary["median"] - summary["baseline_median"]) / summary["baseline_median"]
    )
    return summary


def build_comparison(setting_47: str, setting_10: str) -> tuple[pd.DataFrame, list[str]]:
    data_47 = load_scenario_csv(setting_47, "ntfs_6y.csv", "total_treatmentfailures")
    data_10 = load_scenario_csv(setting_10, "ntfs_6y.csv", "total_treatmentfailures")
    summary_47 = treatment_failure_summary(data_47)
    summary_10 = treatment_failure_summary(data_10)

    rel_47 = summary_47.groupby("scenario_clean")["relative_change_pct"].mean().rename("rel_47")
    rel_10 = summary_10.groupby("scenario_clean")["relative_change_pct"].mean().rename("rel_10")
    med_47 = summary_47.groupby("scenario_clean")["median"].mean().rename("median_47")
    med_10 = summary_10.groupby("scenario_clean")["median"].mean().rename("median_10")
    joined = pd.concat([rel_47, rel_10, med_47, med_10], axis=1).dropna()
    order = joined["rel_10"].sort_values(ascending=True).index[::-1].tolist()
    return joined.loc[order], order


def make_figure(setting_47: str, setting_10: str, output_relative: str) -> Path:
    comparison, order = build_comparison(setting_47, setting_10)
    k13_47 = load_scenario_csv(setting_47, "k13_frequency_at_2031.csv", "k13_frequency")
    k13_10 = load_scenario_csv(setting_10, "k13_frequency_at_2031.csv", "k13_frequency")
    median_k13_47 = k13_47.groupby("scenario_clean")["k13_frequency"].median()
    median_k13_10 = k13_10.groupby("scenario_clean")["k13_frequency"].median()
    missing = set(order) - set(median_k13_47.index) | (set(order) - set(median_k13_10.index))
    if missing:
        raise ValueError(f"K13 data are missing strategies: {', '.join(sorted(missing))}")

    y = np.arange(len(order))
    colors_47 = ["#3182bd"] * len(order)
    for index, scenario in enumerate(order):
        if scenario in HIGH_DHAPPQ_SCENARIOS:
            colors_47[index] = "black"

    fig, (ax1, ax2) = plt.subplots(figsize=(16, 24), ncols=2, sharey=True)
    ax1.barh(y, comparison["rel_10"].to_numpy(), color="#9ecae1", label="10% Private Market")
    ax1.barh(y, comparison["rel_47"].to_numpy(), color=colors_47, label="47% Private Market (reference)")
    ax1.axvline(0, color="black", linewidth=1)
    label_parts = [LABELS[scenario].split(" | ") for scenario in order]
    ax1.set_yticks(y)
    ax1.set_yticklabels(format_labels(label_parts), fontfamily="monospace", fontsize=12, ha="right")
    ax1.tick_params(axis="y", pad=0)
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}%"))
    ax1.set_xlabel("Reduction in treatment failures\ncompared to status quo AL use", fontsize=18)
    ax1.grid(axis="both", linestyle="--", alpha=0.6)
    xmin = min(comparison["rel_47"].min(), comparison["rel_10"].min())
    xmax = max(comparison["rel_47"].max(), comparison["rel_10"].max())
    ax1.set_xlim(xmin - 12, xmax + 10)
    ax1.set_ylim(-0.5, len(order) - 0.5)
    ax1.tick_params(axis="x", labelsize=14)
    ax1.legend(
        handles=[
            mpatches.Patch(color="#3182bd", label="47% Private Market (reference)"),
            mpatches.Patch(color="#9ecae1", label="10% Private Market"),
            mpatches.Patch(color="black", label="47% Private Market (high DHA-PPQ use)"),
        ],
        loc="upper center", bbox_to_anchor=(0.6, -0.05), ncol=1, frameon=False, fontsize=18,
    )

    ax2.barh(y, median_k13_47.loc[order].to_numpy(), color="#fdae6b", label="47% Private Market (k13)")
    ax2.barh(y, median_k13_10.loc[order].to_numpy(), color="#e6550d", label="10% Private Market (k13)")
    ax2.set_xlabel("Median 561H frequency in 2031", fontsize=18)
    ax2.set_yticks(y)
    ax2.tick_params(axis="y", length=0, labelleft=False)
    ax2.grid(axis="both", linestyle="--", alpha=0.6)
    ax2.set_xlim(0, 1)
    ax2.tick_params(axis="x", labelsize=14)
    ax2.xaxis.set_major_formatter(FuncFormatter(lambda value, _: "" if value == 0 else f"{value:.1f}"))
    ax2.legend(
        handles=[
            mpatches.Patch(color="#fdae6b", label="47% Private Market (k13)"),
            mpatches.Patch(color="#e6550d", label="10% Private Market (k13)"),
        ],
        loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=1, frameon=False, fontsize=18,
    )

    fig.subplots_adjust(left=0.3, wspace=0.01)
    ax1.text(0.02, 0.987, "A", transform=ax1.transAxes, fontsize=14, fontweight="bold", ha="left", va="bottom")
    ax2.text(0.98, 0.987, "B", transform=ax2.transAxes, fontsize=14, fontweight="bold", ha="right", va="bottom")
    destination = ROOT / output_relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return destination


def main() -> None:
    for setting_47, setting_10, output in [
        ("004", "005", "figures/main/figure-04.png"),
        ("006", "007", "figures/supplementary/supplementary-figure-10.png"),
    ]:
        saved = make_figure(setting_47, setting_10, output)
        print(f"Saved {saved}")


if __name__ == "__main__":
    main()
