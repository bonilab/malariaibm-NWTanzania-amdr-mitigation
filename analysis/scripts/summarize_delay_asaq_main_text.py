"""Export six-year treatment-failure medians and delay increases for the text."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "analysis" / "data" / "processed" / "scenarios"
OUTPUT = ROOT / "analysis" / "results" / "delay_asaq_percent_increase_from_medians.csv"
SCENARIOS = {
    "004": "47% Private Market - Normal 7686",
    "005": "10% Private Market - Normal 7686",
    "006": "47% Private Market - Lower 7686",
    "007": "10% Private Market - Lower 7686",
}
BASELINE = "001-basic-ASAQ"
DELAYS = {
    "098-Delay-ASAQ-1y": "1 year delay",
    "099-Delay-ASAQ-2y": "2 year delay",
    "100-Delay-ASAQ-3y": "3 year delay",
    "101-Delay-ASAQ-4y": "4 year delay",
}
START = pd.Timestamp("2026-01-01")
END = pd.Timestamp("2032-01-01")


def main() -> None:
    results = []
    for setting, description in SCENARIOS.items():
        path = DATA_DIR / setting / "all_monthly_data.csv.xz"
        data = pd.read_csv(path, usecols=["scenario", "run", "date", "total_treatmentfailures"], parse_dates=["date"])
        wanted = {BASELINE, *DELAYS}
        data["scenario"] = data["scenario"].str.split("/", n=1).str[-1]
        data = data.loc[
            data["scenario"].isin(wanted)
            & (data["date"] >= START)
            & (data["date"] < END)
        ]
        counts = data.groupby(["scenario", "run"])["date"].nunique()
        if counts.empty or not counts.eq(72).all():
            raise ValueError(f"Expected 72 intervention months for every selected run in scenario {setting}")

        cumulative = data.groupby(["scenario", "run"])["total_treatmentfailures"].sum()
        medians = cumulative.groupby(level="scenario").median()
        baseline_median = medians[BASELINE]
        for delay_scenario, label in DELAYS.items():
            delay_median = medians[delay_scenario]
            pct_increase = 100 * (delay_median - baseline_median) / baseline_median
            results.append({
                "scenario_set": setting,
                "description": description,
                "delay": label,
                "baseline_median_total_treatment_failures": baseline_median,
                "delay_median_total_treatment_failures": delay_median,
                "percent_increase_vs_immediate_asaq": pct_increase,
            })

    result_frame = pd.DataFrame(results)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result_frame.to_csv(OUTPUT, index=False, float_format="%.1f")
    print(result_frame.to_string(index=False, formatters={
        "baseline_median_total_treatment_failures": "{:,.0f}".format,
        "delay_median_total_treatment_failures": "{:,.0f}".format,
        "percent_increase_vs_immediate_asaq": "{:.1f}%".format,
    }))
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
