"""Generate Supplementary Figure 16: treatment-failure trajectories."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "analysis" / "data" / "processed" / "scenarios" / "004" / "all_monthly_data.csv.xz"
OUTPUT = ROOT / "figures" / "supplementary" / "supplementary-figure-16.png"

LOWER_QUANTILE = 0.05
UPPER_QUANTILE = 0.95
SMOOTH_MONTHS = 12

PUBLICATION_LABELS = {
    "000-status-quo": "Status quo: AL",
    "001-basic-ASAQ": "Immediate switch to ASAQ",
    "099-Delay-ASAQ-2y": "Switch to ASAQ after 2 years",
    "101-Delay-ASAQ-4y": "Switch to ASAQ after 4 years",
    "006-Cycling-1y-ASAQ-DHAPPQ": "ASAQ–DHA-PPQ cycling\n1-year intervals",
    "018-Cycling-2y-ASAQ-DHAPPQ": "ASAQ–DHA-PPQ cycling\n2-year intervals",
    "030-Cycling-3y-ASAQ-DHAPPQ": "ASAQ–DHA-PPQ cycling\n3-year intervals",
    "042-Cycling-4y-ASAQ-DHAPPQ": "ASAQ–DHA-PPQ cycling\n4-year intervals",
    "054-mft-AL75-ASAQ25": "MFT: AL 75%, ASAQ 25%",
    "057-mft-AL50-ASAQ50": "MFT: AL 50%, ASAQ 50%",
    "060-mft-AL-ASAQ-DHAPPQ": "MFT: AL 33%, ASAQ 33%, DHA-PPQ 33%",
    "051-mft-AL25-ASAQ75": "MFT: AL 25%, ASAQ 75%",
    "070-tact-ALAQ-immediate": "Immediate switch to ALAQ",
    "062-tact-ASAQ4y-ALAQ": "ASAQ for 4 years, then ALAQ",
    "064-tact-AL2y-ASAQ2y-ALAQ": "AL 2 years → ASAQ 2 years → ALAQ",
    "061-tact-AL4y-ALAQ": "AL for 4 years, then ALAQ",
}

TRAJECTORY_GROUPS = {
    "A. Switch timing": [
        "000-status-quo", "001-basic-ASAQ", "099-Delay-ASAQ-2y", "101-Delay-ASAQ-4y",
    ],
    "B. Cycling duration": [
        "006-Cycling-1y-ASAQ-DHAPPQ", "018-Cycling-2y-ASAQ-DHAPPQ",
        "030-Cycling-3y-ASAQ-DHAPPQ", "042-Cycling-4y-ASAQ-DHAPPQ",
    ],
    "C. Multiple first-line therapies": [
        "054-mft-AL75-ASAQ25", "057-mft-AL50-ASAQ50",
        "060-mft-AL-ASAQ-DHAPPQ", "051-mft-AL25-ASAQ75",
    ],
    "D. Triple ACT deployment": [
        "070-tact-ALAQ-immediate", "062-tact-ASAQ4y-ALAQ",
        "064-tact-AL2y-ASAQ2y-ALAQ", "061-tact-AL4y-ALAQ",
    ],
}
SCENARIOS = {scenario for group in TRAJECTORY_GROUPS.values() for scenario in group}


def summarize_trajectory(data: pd.DataFrame) -> pd.DataFrame:
    grouped = data.groupby("date")["treatment_failure_rate"]
    summary = pd.DataFrame(
        {
            "low": grouped.quantile(LOWER_QUANTILE),
            "median": grouped.median(),
            "high": grouped.quantile(UPPER_QUANTILE),
        }
    )
    return summary.rolling(window=SMOOTH_MONTHS, min_periods=1).mean()


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing input data: {INPUT}")

    data = pd.read_csv(INPUT, parse_dates=["date"])
    required = {"scenario", "date", "treatment_failure_rate"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"{INPUT} is missing columns: {', '.join(sorted(missing))}")

    data["scenario"] = data["scenario"].astype(str).str.replace("004/", "", regex=False)
    data["treatment_failure_rate"] = pd.to_numeric(
        data["treatment_failure_rate"], errors="coerce"
    )
    data = data.loc[data["scenario"].isin(SCENARIOS)].copy()
    present = set(data["scenario"].unique())
    missing_scenarios = SCENARIOS - present
    if missing_scenarios:
        raise ValueError(f"Input is missing scenarios: {', '.join(sorted(missing_scenarios))}")

    reference = summarize_trajectory(data.loc[data["scenario"] == "000-status-quo"])
    with plt.rc_context(
        {
            "font.size": 11,
            "axes.titlesize": 11,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    ):
        fig, axes = plt.subplots(4, 4, figsize=(12, 12), sharex=True, sharey=True, squeeze=False)

        for row, (group_name, scenarios) in enumerate(TRAJECTORY_GROUPS.items()):
            for col, scenario in enumerate(scenarios):
                ax = axes[row, col]
                scenario_data = data.loc[data["scenario"] == scenario]
                summary = summarize_trajectory(scenario_data)

                ax.plot(reference.index, reference["median"], color="grey", linewidth=1.3, alpha=0.9)
                ax.fill_between(
                    reference.index, reference["low"].to_numpy(), reference["high"].to_numpy(),
                    color="grey", alpha=0.12,
                )
                ax.plot(summary.index, summary["median"], linewidth=1.8)
                ax.fill_between(
                    summary.index, summary["low"].to_numpy(), summary["high"].to_numpy(),
                    alpha=0.20,
                )
                ax.set_title(PUBLICATION_LABELS[scenario], fontsize=10)
                ax.set_xlim(pd.Timestamp("2024-01-01"), pd.Timestamp("2032-01-01"))
                ax.axvline(pd.Timestamp("2026-01-01"), color="black", linestyle="--", linewidth=1.0, alpha=0.7)
                ax.grid(True, which="major", axis="both", linewidth=0.5, alpha=0.5)
                ax.tick_params(axis="x", rotation=45)
                if col == 0:
                    ax.set_ylabel(f"{group_name}\nTreatment Failure Rate (%)", fontsize=11)
                else:
                    ax.set_ylabel("")
                ax.set_xlabel("")

        fig.tight_layout()
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
