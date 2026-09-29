"""Generate Supplementary Figures 11 and 12 from processed ASPY trajectories."""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "analysis" / "data" / "processed" / "aspy"
OUTPUT_DIR = ROOT / "figures" / "supplementary"

SCENARIO_GROUPS = {
    "004": "supplementary-figure-11.png",
    "005": "supplementary-figure-12.png",
}
STRATEGY_GROUPS = {
    "MFT AL 75% - ASPY 25%": [
        "071-mft-AL_75-ASPY85_25", "072-mft-AL_75-ASPY75_25", "073-mft-AL_75-ASPY65_25",
    ],
    "MFT AL 50% - ASPY 50%": [
        "074-mft-AL_50-ASPY85_50", "075-mft-AL_50-ASPY75_50", "076-mft-AL_50-ASPY65_50",
    ],
    "MFT ASAQ 75% - ASPY 25%": [
        "077-mft-ASAQ_75-ASPY85_25", "078-mft-ASAQ_75-ASPY75_25", "079-mft-ASAQ_75-ASPY65_25",
    ],
    "MFT ASAQ 50% - ASPY 50%": [
        "080-mft-ASAQ_50-ASPY85_50", "081-mft-ASAQ_50-ASPY75_50", "082-mft-ASAQ_50-ASPY65_50",
    ],
    "MFT AL - DHA-PPQ - ASPY": [
        "083-mft-AL-DHAPPQ-ASPY85", "084-mft-AL-DHAPPQ-ASPY75", "085-mft-AL-DHAPPQ-ASPY65",
    ],
    "MFT ASAQ - DHA-PPQ - ASPY": [
        "086-mft-ASAQ-DHAPPQ-ASPY85", "087-mft-ASAQ-DHAPPQ-ASPY75", "088-mft-ASAQ-DHAPPQ-ASPY65",
    ],
    "MFT AL - ASAQ - DHA-PPQ - ASPY": [
        "089-mft-AL-ASAQ-DHAPPQ-ASPY85", "090-mft-AL-ASAQ-DHAPPQ-ASPY75", "091-mft-AL-ASAQ-DHAPPQ-ASPY65",
    ],
}
ALL_STRATEGIES = [strategy for strategies in STRATEGY_GROUPS.values() for strategy in strategies]
REQUIRED_COLUMNS = {"date", "monthlydataid", "scenario", "run", "hypothetical_mutant_frequency"}


def plot_scenario(data: pd.DataFrame, scenario: str, output_name: str) -> Path:
    scenario_data = data.loc[data["scenario"].str.startswith(f"{scenario}/")].copy()
    scenario_data["scenario"] = scenario_data["scenario"].str.split("/", n=1).str[-1]
    scenario_data = scenario_data.loc[scenario_data["scenario"].isin(ALL_STRATEGIES)].copy()
    if scenario_data.empty:
        raise ValueError(f"No ASPY strategy trajectories found for scenario {scenario}")

    scenario_order = [item for item in ALL_STRATEGIES if item in set(scenario_data["scenario"])]
    colors = sns.color_palette("husl", n_colors=len(scenario_order))
    palette = dict(zip(scenario_order, colors))
    scenario_data["group"] = scenario_data["scenario"].map(
        {strategy: group for group, strategies in STRATEGY_GROUPS.items() for strategy in strategies}
    )
    scenario_data["group"] = pd.Categorical(
        scenario_data["group"], categories=list(STRATEGY_GROUPS), ordered=True
    )

    grid = sns.relplot(
        data=scenario_data,
        x="date",
        y="hypothetical_mutant_frequency",
        hue="scenario",
        hue_order=scenario_order,
        palette=palette,
        col="group",
        col_order=list(STRATEGY_GROUPS),
        kind="line",
        col_wrap=3,
        height=4,
        aspect=1.5,
        errorbar=("pi", 90),
        facet_kws={"sharey": True, "sharex": True},
    )
    grid.set_axis_labels("Year", "Hypothetical Pyronaridine Mutant Frequency")
    grid.set(xlim=(pd.Timestamp("2025-01-01"), pd.Timestamp("2032-01-01")), ylim=(0, 0.1))

    for ax, group_name in zip(grid.axes.flat, STRATEGY_GROUPS):
        ax.set_title(group_name)
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)

        for strategy_index, strategy in enumerate(STRATEGY_GROUPS[group_name]):
            strategy_data = scenario_data.loc[scenario_data["scenario"] == strategy]
            if strategy_data.empty:
                continue
            by_date = strategy_data.groupby("date")["hypothetical_mutant_frequency"].median()
            nearest_date = by_date.index[(by_date.index - pd.Timestamp("2031-01-01")).to_series().abs().argmin()]
            y = float(by_date.loc[nearest_date]) + (strategy_index - 1) * 0.003
            aspy_label = next(part for part in strategy.split("-") if part.startswith("ASPY")).split("_")[0]
            color = tuple(max(0, channel - 0.2) for channel in palette[strategy])
            ax.text(pd.Timestamp("2031-01-01"), y, aspy_label, fontsize=8, ha="left", va="center", color=color)

    if grid._legend is not None:
        grid._legend.remove()
    destination = OUTPUT_DIR / output_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    grid.figure.savefig(destination, dpi=200, bbox_inches="tight")
    plt.close(grid.figure)
    return destination


def main() -> None:
    input_parts = sorted(DATA_DIR.glob("all_aspy_monthly_data.part-*.csv.xz"))
    if not input_parts:
        raise FileNotFoundError(
            f"Missing ASPY trajectory parts in {DATA_DIR}. Expected files named "
            "all_aspy_monthly_data.part-*.csv.xz containing hypothetical_mutant_frequency "
            "trajectories for scenarios 004 and 005."
        )
    data = pd.concat(
        [pd.read_csv(path, parse_dates=["date"]) for path in input_parts],
        ignore_index=True,
    )
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"{INPUT} is missing columns: {', '.join(sorted(missing))}")
    for scenario, output_name in SCENARIO_GROUPS.items():
        print(f"Saved {plot_scenario(data, scenario, output_name)}")


if __name__ == "__main__":
    main()
