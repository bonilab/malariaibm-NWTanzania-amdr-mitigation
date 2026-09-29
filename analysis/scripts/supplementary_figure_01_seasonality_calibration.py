"""Generate Supplementary Figure 1: seasonal incidence calibration."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "analysis" / "data" / "raw" / "supplementary_figure_01" / "kagera_case_reporting_2017_2023"
PROCESSED_DIR = ROOT / "analysis" / "data" / "processed" / "supplementary_figure_01"
SIMULATION_FILE = PROCESSED_DIR / "simulation_output_monthly_incidence.csv"
UNDER5_FILE = RAW_DIR / "kagera_monthly_incidence_under5s.csv"
OVER5_FILE = RAW_DIR / "kagera_monthly_incidence_over5s.csv"
OUTPUT_FILE = ROOT / "figures" / "supplementary" / "supplementary-figure-01.png"

GROUPS = ["under_5_incidence", "over_5_incidence", "combined_incidence"]
TITLES = ["Under 5 Incidence", "Over 5 Incidence", "Combined Incidence"]


def build_observed_seasonality() -> pd.DataFrame:
    under5 = pd.read_csv(UNDER5_FILE).rename(
        columns={"Positive_U5": "Positive", "mRDT_Tests_U5": "mRDT_Tests"}
    )
    over5 = pd.read_csv(OVER5_FILE).rename(
        columns={"Positive_G5": "Positive", "mRDT_Tests_G5": "mRDT_Tests"}
    )
    under5 = under5[["Year", "Month", "Positive", "mRDT_Tests"]].copy()
    over5 = over5[["Year", "Month", "Positive", "mRDT_Tests"]].copy()
    under5["type"] = "under_5_incidence"
    over5["type"] = "over_5_incidence"

    combined = (
        pd.concat([under5, over5], ignore_index=True)
        .groupby(["Year", "Month"], as_index=False)[["Positive", "mRDT_Tests"]]
        .sum()
    )
    combined["type"] = "combined_incidence"
    observed = pd.concat([under5, over5, combined], ignore_index=True)
    observed["positivity"] = observed["Positive"] / observed["mRDT_Tests"]
    observed["positivity"] = observed["positivity"].replace([float("inf"), -float("inf")], pd.NA)
    observed = observed.dropna(subset=["positivity"])

    overall_median = observed.groupby("type")["positivity"].median().rename("overall_median_positivity")
    monthly = (
        observed.groupby(["type", "Month"])["positivity"]
        .median()
        .rename("median_positivity")
        .reset_index()
        .merge(overall_median, on="type", how="left")
    )
    monthly["median_based_weight"] = monthly["median_positivity"] / monthly["overall_median_positivity"]
    return monthly


def main() -> None:
    missing = [path for path in [SIMULATION_FILE, UNDER5_FILE, OVER5_FILE] if not path.exists()]
    if missing:
        raise FileNotFoundError("Required Figure S1 input file(s) are missing:\n" + "\n".join(f"  - {p}" for p in missing))

    incidence_summary = pd.read_csv(SIMULATION_FILE)
    required = {"group", "Month", "incidence"}
    missing_columns = required - set(incidence_summary.columns)
    if missing_columns:
        raise ValueError(f"{SIMULATION_FILE} is missing columns: {', '.join(sorted(missing_columns))}")
    seasonal_weights = build_observed_seasonality()

    sns.set_context("paper")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    for ax, group, title in zip(axes, GROUPS, TITLES):
        sns.boxplot(
            data=incidence_summary.loc[incidence_summary["group"] == group],
            x="Month", y="incidence", order=list(range(1, 13)), ax=ax,
        )
        sns.pointplot(
            data=seasonal_weights.loc[seasonal_weights["type"] == group],
            x="Month", y="median_based_weight", order=list(range(1, 13)),
            markers="o", color="red", ax=ax,
        )
        ax.axhline(1.0, linestyle="--", color="gray", linewidth=1)
        ax.set_title(f"{title} for Tanzania 47% Private Market")
        ax.set_xlabel("Month")
        ax.set_ylabel("Incidence / seasonal weight")

    fig.tight_layout()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
