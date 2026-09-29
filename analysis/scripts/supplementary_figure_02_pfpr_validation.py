"""Generate Supplementary Figure 2: pixel- and district-level PfPR validation."""

from pathlib import Path
import re

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "analysis" / "data" / "processed" / "supplementary_figure_02"
CALIBRATION_FILE = DATA_DIR / "calibration_data.csv"
DISTRICT_FILE = DATA_DIR / "district_pfpr_comparison.csv"
OUTPUT_FILE = ROOT / "figures" / "supplementary" / "supplementary-figure-02.png"

DISTRICT_NAMES = {1: "Kagera", 2: "Kigoma", 3: "Geita", 4: "Mwanza"}


def main() -> None:
    for path in (CALIBRATION_FILE, DISTRICT_FILE):
        if not path.exists():
            raise FileNotFoundError(f"Missing Supplementary Figure 2 input: {path}")

    calibration = pd.read_csv(CALIBRATION_FILE)
    district = pd.read_csv(DISTRICT_FILE)
    required_calibration = {"true_pfpr2to10", "population"}
    required_district = {"districtid", "pfpr2to10_db", "pfpr2to10_atlas"}
    missing_calibration = required_calibration - set(calibration.columns)
    missing_district = required_district - set(district.columns)
    if missing_calibration:
        raise ValueError(f"{CALIBRATION_FILE} is missing columns: {', '.join(sorted(missing_calibration))}")
    if missing_district:
        raise ValueError(f"{DISTRICT_FILE} is missing columns: {', '.join(sorted(missing_district))}")

    model_columns = [c for c in calibration if re.fullmatch(r"pfpr2to10_run\d+", c)]
    population_columns = [c for c in calibration if c == "population" or re.fullmatch(r"population_run\d+", c)]
    if not model_columns or not population_columns:
        raise ValueError("Calibration data must contain pfpr2to10_run* and population[_run*] columns")
    pixel_data = pd.DataFrame(
        {
            "atlas_pfpr": calibration["true_pfpr2to10"],
            "model_pfpr": calibration[model_columns].mean(axis=1),
            "population": calibration[population_columns].mean(axis=1),
        }
    )

    district["difference_pp"] = (district["pfpr2to10_db"] - district["pfpr2to10_atlas"]) * 100
    district["district_name"] = district["districtid"].map(DISTRICT_NAMES)
    if district["district_name"].isna().any():
        unknown = sorted(district.loc[district["district_name"].isna(), "districtid"].unique())
        raise ValueError(f"District data contains unmapped district IDs: {unknown}")

    sns.set_theme(style="whitegrid", context="talk")
    fig, (ax_a, ax_b) = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(18, 8),
        gridspec_kw={"width_ratios": [1.1, 1]},
    )
    sns.scatterplot(
        data=pixel_data, x="atlas_pfpr", y="model_pfpr", size="population",
        sizes=(30, 350), alpha=0.55, legend=False, ax=ax_a,
    )
    sns.regplot(data=pixel_data, x="atlas_pfpr", y="model_pfpr", scatter=False, ax=ax_a,
                line_kws={"linewidth": 2})
    ax_a.axline((0, 0), slope=1, linestyle="--", linewidth=1.5, color="black")
    ax_a.set(xlim=(-1, 32), ylim=(-1, 32), xlabel="Atlas PfPR 2–10 in 2022 (%)",
             ylabel="Mean simulated PfPR 2–10 in 2022 (%)", title="Pixel-level PfPR comparison")
    ax_a.text(0.02, 0.96, "A", transform=ax_a.transAxes, fontsize=18, fontweight="bold", va="top")

    district_order = sorted(DISTRICT_NAMES.values())
    sns.boxplot(
        data=district, x="district_name", y="difference_pp", hue="district_name",
        order=district_order, hue_order=district_order, palette="tab20", legend=False, ax=ax_b,
    )
    ax_b.axhline(0, linestyle="--", linewidth=1.5, color="black")
    ax_b.tick_params(axis="x", rotation=30)
    ax_b.set(xlabel="District", ylabel="Model − Atlas PfPR 2–10\npercentage-point difference",
             title="District-level model bias")
    ax_b.text(0.02, 0.96, "B", transform=ax_b.transAxes, fontsize=18, fontweight="bold", va="top")

    fig.suptitle("Comparison of simulated PfPR 2–10 against Atlas estimates, 2022", fontsize=20, y=0.98)
    fig.tight_layout()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
