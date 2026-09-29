"""Generate Figure 2: MFT and two-year cycling strategy comparison."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "analysis" / "data" / "processed" / "scenarios"
OUTPUT = ROOT / "figures" / "main" / "figure-02.pdf"
YEAR = 2031
MONTHS = 72

# These are the MFT and two-year cycling strategies shown in the manuscript.
STRATEGIES = {
    "000-status-quo": ("Status quo", "#80b1d3"),
    "015-Cycling-2y-AL-ASAQ": ("Cycling 2y AL → ASAQ", "#8dd3c7"),
    "016-Cycling-2y-AL-DHAPPQ": ("Cycling 2y AL → DHA-PPQ", "#8dd3c7"),
    "017-Cycling-2y-ASAQ-AL": ("Cycling 2y ASAQ → AL", "#8dd3c7"),
    "018-Cycling-2y-ASAQ-DHAPPQ": ("Cycling 2y ASAQ → DHA-PPQ", "#8dd3c7"),
    "019-Cycling-2y-DHAPPQ-AL": ("Cycling 2y DHA-PPQ → AL", "#8dd3c7"),
    "020-Cycling-2y-DHAPPQ-ASAQ": ("Cycling 2y DHA-PPQ → ASAQ", "#8dd3c7"),
    "021-Cycling-2y-AL-ASAQ-DHAPPQ": ("Cycling 2y AL → ASAQ → DHA-PPQ", "#998ec3"),
    "051-mft-AL25-ASAQ75": ("MFT AL 25% / ASAQ 75%", "#fb8072"),
    "052-mft-AL25-DHAPPQ75": ("MFT AL 25% / DHA-PPQ 75%", "#fb8072"),
    "053-mft-ASAQ25-DHAPPQ75": ("MFT ASAQ 25% / DHA-PPQ 75%", "#fb8072"),
    "054-mft-AL75-ASAQ25": ("MFT AL 75% / ASAQ 25%", "#fb8072"),
    "055-mft-AL75-DHAPPQ25": ("MFT AL 75% / DHA-PPQ 25%", "#fb8072"),
    "056-mft-ASAQ75-DHAPPQ25": ("MFT ASAQ 75% / DHA-PPQ 25%", "#fb8072"),
    "057-mft-AL50-ASAQ50": ("MFT AL 50% / ASAQ 50%", "#fb8072"),
    "058-mft-AL50-DHAPPQ50": ("MFT AL 50% / DHA-PPQ 50%", "#fb8072"),
    "059-mft-ASAQ50-DHAPPQ50": ("MFT ASAQ 50% / DHA-PPQ 50%", "#fb8072"),
    "060-mft-AL-ASAQ-DHAPPQ": ("MFT AL 33% / ASAQ 33% / DHA-PPQ 33%", "#998ec3"),
}

THREE_DRUG_CYCLING = {
    f"{n:03d}-Cycling-2y-" for n in range(21, 27)
}


def read_scenario(folder: str) -> pd.DataFrame:
    path = DATA_DIR / folder / "ntfs_6y.csv"
    data = pd.read_csv(path)
    required = {"scenario", "total_treatmentfailures", "year"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {', '.join(sorted(missing))}")

    data = data.loc[data["year"] == YEAR].copy()
    data["scenario"] = data["scenario"].str.split("/").str[-1]
    data = data.loc[
        data["scenario"].isin(STRATEGIES)
        | data["scenario"].str.startswith(tuple(THREE_DRUG_CYCLING))
    ].copy()
    data.loc[data["scenario"].str.startswith(tuple(THREE_DRUG_CYCLING)), "scenario"] = (
        "021-Cycling-2y-AL-ASAQ-DHAPPQ"
    )
    data["monthly_failures"] = data["total_treatmentfailures"] / MONTHS
    return data


def main() -> None:
    primary = read_scenario("004")
    # Sort MFT policies from best to worst above status quo. Put two-year
    # rotations below it, ordered from worst to best to match the caption.
    mft_ids = [s for s in STRATEGIES if s.startswith(("05", "06"))]
    cycling_ids = [s for s in STRATEGIES if s.startswith("0") and "Cycling-2y" in s]
    mft_order = (
        primary.loc[primary.scenario.isin(mft_ids)]
        .groupby("scenario").monthly_failures.median().sort_values().index.tolist()
    )
    cycling_order = (
        primary.loc[primary.scenario.isin(cycling_ids)]
        .groupby("scenario").monthly_failures.median().sort_values(ascending=False).index.tolist()
    )
    scenario_order = mft_order + ["000-status-quo"] + cycling_order

    # Aggregate the six orderings of three-drug cycling into the plotted group.
    positions = {scenario: -i * 0.42 for i, scenario in enumerate(scenario_order)}
    fig, ax = plt.subplots(figsize=(16, 10))
    for scenario in scenario_order:
        values = primary.loc[primary.scenario == scenario, "monthly_failures"]
        if values.empty:
            continue
        label, color = STRATEGIES[scenario]
        ax.boxplot(
            values,
            positions=[positions[scenario]],
            widths=0.27,
            orientation="horizontal",
            patch_artist=True,
            boxprops={"facecolor": color, "edgecolor": "black", "linewidth": 1.5},
            whiskerprops={"color": "black", "linewidth": 1.5},
            capprops={"color": "black", "linewidth": 1.5},
            medianprops={"color": "black", "linewidth": 1.5},
            flierprops={
                "marker": "o", "markerfacecolor": "#fb6a4a",
                "markeredgecolor": "#de2d26", "alpha": 0.55, "markersize": 4,
            },
        )

    ax.set_yticks([positions[s] for s in scenario_order])
    ax.set_yticklabels([STRATEGIES[s][0] for s in scenario_order], fontsize=11)
    ax.set_xlabel("Average monthly treatment failures (2026–2031)", fontsize=14)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x / 1000:.0f}K"))
    ax.grid(axis="x", color="#d9d9d9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title("47% private-market scenario", fontsize=16, pad=14)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, bbox_inches="tight")
    print(f"Saved {OUTPUT}")
    plt.close(fig)


if __name__ == "__main__":
    main()
