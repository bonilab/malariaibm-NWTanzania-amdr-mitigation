"""Summarize annual status-quo treatment failures and their annual growth."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "analysis" / "data" / "processed" / "scenarios"
OUTPUT = ROOT / "analysis" / "results" / "status_quo_annual_failure_growth.csv"
SETTINGS = {
    "004": "47% Private Market - Normal 7686",
    "005": "10% Private Market - Normal 7686",
    "006": "47% Private Market - Lower 7686",
    "007": "10% Private Market - Lower 7686",
}
STATUS_QUO = "000-status-quo"
START_YEAR = 2026
END_YEAR = 2031


def summarize_setting(setting: str, description: str) -> dict[str, object]:
    path = DATA_DIR / setting / "all_monthly_data.csv.xz"
    data = pd.read_csv(
        path,
        usecols=["scenario", "run", "date", "total_treatmentfailures"],
        parse_dates=["date"],
    )
    data["scenario"] = data["scenario"].str.split("/", n=1).str[-1]
    data = data.loc[
        data["scenario"].eq(STATUS_QUO)
        & data["date"].dt.year.between(START_YEAR, END_YEAR)
    ].copy()
    data["year"] = data["date"].dt.year

    month_counts = data.groupby(["run", "year"])["date"].nunique()
    expected = pd.MultiIndex.from_product(
        [data["run"].unique(), range(START_YEAR, END_YEAR + 1)],
        names=["run", "year"],
    )
    if not month_counts.reindex(expected).eq(12).all():
        raise ValueError(
            f"Expected 12 status-quo months per run and year ({START_YEAR}–{END_YEAR}) "
            f"for setting {setting}"
        )

    annual_by_run = data.groupby(["run", "year"])["total_treatmentfailures"].sum()
    annual_medians = annual_by_run.groupby(level="year").median()
    years = annual_medians.index.to_numpy(dtype=float)
    counts = annual_medians.to_numpy(dtype=float)
    annual_growth = (annual_medians.iloc[-1] / annual_medians.iloc[0]) ** (
        1 / (END_YEAR - START_YEAR)
    ) - 1

    result: dict[str, object] = {
        "scenario_set": setting,
        "description": description,
        "annual_increase_pct": 100 * annual_growth,
    }
    # Include the full annual trajectory so the endpoints and CAGR are auditable.
    result.update({f"median_failures_{int(year)}": count for year, count in zip(years, counts)})
    return result


def main() -> None:
    results = pd.DataFrame(
        summarize_setting(setting, description)
        for setting, description in SETTINGS.items()
    )
    # Keep columns in a predictable order.
    results = results[
        [
            "scenario_set",
            "description",
            *[f"median_failures_{year}" for year in range(START_YEAR, END_YEAR + 1)],
            "annual_increase_pct",
        ]
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT, index=False, float_format="%.2f")
    print(results.to_string(index=False, formatters={
        **{f"median_failures_{year}": "{:,.0f}".format for year in range(START_YEAR, END_YEAR + 1)},
        "annual_increase_pct": "{:.2f}%".format,
    }))
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
