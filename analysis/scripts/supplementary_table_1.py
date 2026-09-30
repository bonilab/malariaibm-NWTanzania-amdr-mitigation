"""Build the publication-ready Supplementary Table 1 NTFS summary."""

from __future__ import annotations

import pandas as pd

from ntfs_table_utils import LABELS, RESULTS_DIR, SETTINGS, load_setting, six_year_runs


def summarize_setting(setting: str, private_market: str) -> pd.DataFrame:
    data = load_setting(setting)
    data = data.loc[data["scenario_clean"].isin(LABELS)]
    runs = six_year_runs(data)
    runs["monthly_tf"] = runs["ntf_6y"] / 72
    status_quo = runs.loc[runs["scenario_clean"].eq("000-status-quo"), "monthly_tf"]
    if status_quo.empty:
        raise ValueError(f"No status quo results found for setting {setting}")
    baseline = status_quo.median()

    rows = []
    for scenario, group in runs.groupby("scenario_clean"):
        median = group["monthly_tf"].median()
        low = group["monthly_tf"].quantile(0.05)
        high = group["monthly_tf"].quantile(0.95)
        reduction = 100 * (baseline - median) / baseline
        reduction_low = 100 * (baseline - high) / baseline
        reduction_high = 100 * (baseline - low) / baseline
        rows.append({
            "Scenario ID": scenario,
            "Private-market share (%)": private_market,
            "monthly_tf_median": median,
            "monthly_tf_p05": low,
            "monthly_tf_p95": high,
            "reduction_median_pct": reduction,
            "reduction_p05_pct": reduction_low,
            "reduction_p95_pct": reduction_high,
        })
    return pd.DataFrame(rows)


def build_table() -> pd.DataFrame:
    table = pd.concat(
        [summarize_setting(setting, share) for setting, share in SETTINGS.items()],
        ignore_index=True,
    )
    ordering = (
        table.loc[table["Private-market share (%)"].eq("10%")]
        .sort_values("reduction_median_pct", ascending=False)["Scenario ID"]
        .tolist()
    )
    table["Scenario ID"] = pd.Categorical(table["Scenario ID"], categories=ordering, ordered=True)
    table["Private-market share (%)"] = pd.Categorical(
        table["Private-market share (%)"], categories=["47%", "10%"], ordered=True
    )
    table = table.sort_values(["Scenario ID", "Private-market share (%)"]).reset_index(drop=True)

    table["Monthly treatment failures, median (90% interval)"] = table.apply(
        lambda row: (
            f"{row['monthly_tf_median']:,.0f} "
            f"({row['monthly_tf_p05']:,.0f}–{row['monthly_tf_p95']:,.0f})"
        ), axis=1,
    )
    table["Reduction vs. status quo, median (90% interval), %"] = table.apply(
        lambda row: (
            f"{row['reduction_median_pct']:.1f} "
            f"({row['reduction_p05_pct']:.1f}–{row['reduction_p95_pct']:.1f})"
        ), axis=1,
    )
    return table[[
        "Scenario ID",
        "Private-market share (%)",
        "Monthly treatment failures, median (90% interval)",
        "Reduction vs. status quo, median (90% interval), %",
    ]]


def main() -> None:
    table = build_table()
    output = RESULTS_DIR / "supplementary_table_1.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output, index=False)
    print(table.to_string(index=False))
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
