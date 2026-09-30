"""Export six-year treatment-failure count summaries for settings 004 and 005."""

from __future__ import annotations

import pandas as pd

from ntfs_table_utils import LABELS, RESULTS_DIR, SETTINGS, load_setting, six_year_runs


def main() -> None:
    parts = []
    for setting, market in SETTINGS.items():
        data = load_setting(setting)
        data = data.loc[data["scenario_clean"].isin(LABELS)]
        runs = six_year_runs(data)
        summary = runs.groupby("scenario_clean")["ntf_6y"].agg(
            median="median", p05=lambda values: values.quantile(.05),
            p95=lambda values: values.quantile(.95),
        ).reset_index()
        summary[["median", "p05", "p95"]] /= 72
        baseline = summary.loc[summary.scenario_clean.eq("000-status-quo"), "median"].iloc[0]
        summary["relative_change_pct"] = 100 * (summary["median"] - baseline) / baseline
        summary["private_market"] = market
        parts.append(summary)

    table = pd.concat(parts, ignore_index=True)
    table["Scenario ID"] = table.pop("scenario_clean")
    table["Private market (%)"] = table.pop("private_market")
    table["Monthly treatment failures, median"] = table.pop("median").round().map("{:,.0f}".format)
    table["Monthly treatment failures, 90% interval"] = (
        table.pop("p05").round().map("{:,.0f}".format)
        + "–"
        + table.pop("p95").round().map("{:,.0f}".format)
    )
    table["Relative change vs. status quo (%)"] = table.pop("relative_change_pct").round(1)
    table = table[[
        "Scenario ID", "Private market (%)", "Monthly treatment failures, median",
        "Monthly treatment failures, 90% interval", "Relative change vs. status quo (%)",
    ]]
    output = RESULTS_DIR / "ntfs_6y_count_table.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output, index=False)
    print(table.to_string(index=False))
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
