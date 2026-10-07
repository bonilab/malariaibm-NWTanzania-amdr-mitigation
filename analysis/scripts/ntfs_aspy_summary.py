"""Summarize treatment failures for ASAQ-based MFT policies with ASPY."""

from __future__ import annotations

import pandas as pd

from ntfs_table_utils import DATA_DIR, RESULTS_DIR, SETTINGS, six_year_runs


TARGETS = {
    "077-mft-ASAQ_75-ASPY85_25": "MFT | ASAQ 75% | ASPY85 25%",
    "078-mft-ASAQ_75-ASPY75_25": "MFT | ASAQ 75% | ASPY75 25%",
    "079-mft-ASAQ_75-ASPY65_25": "MFT | ASAQ 75% | ASPY65 25%",
    "080-mft-ASAQ_50-ASPY85_50": "MFT | ASAQ 50% | ASPY85 50%",
    "081-mft-ASAQ_50-ASPY75_50": "MFT | ASAQ 50% | ASPY75 50%",
    "082-mft-ASAQ_50-ASPY65_50": "MFT | ASAQ 50% | ASPY65 50%",
    "086-mft-ASAQ-DHAPPQ-ASPY85": "MFT | ASAQ, DHA-PPQ, ASPY85",
    "087-mft-ASAQ-DHAPPQ-ASPY75": "MFT | ASAQ, DHA-PPQ, ASPY75",
    "088-mft-ASAQ-DHAPPQ-ASPY65": "MFT | ASAQ, DHA-PPQ, ASPY65",
}
TWO_ACT = set(list(TARGETS)[:6])
THREE_ACT = set(list(TARGETS)[6:])


def main() -> None:
    rows = []
    replicate_parts = []
    for setting, market in SETTINGS.items():
        data = pd.read_csv(DATA_DIR / setting / "ntfs_6y.csv")
        data["scenario_clean"] = data["scenario"].str.replace(r"^\d+/", "", regex=True)
        sim_col = "run" if "run" in data.columns else "replicate"
        baseline = data.loc[data.scenario_clean.eq("000-status-quo")].groupby(sim_col).total_treatmentfailures.sum() / 72
        baseline_median = baseline.median()
        data = data.loc[data["scenario_clean"].isin(TARGETS)]
        if data.empty:
            raise ValueError(f"No target ASPY strategies found in setting {setting}")
        runs = six_year_runs(data)
        runs["monthly_tf"] = runs["ntf_6y"] / 72
        runs["policy_group"] = runs.scenario_clean.map(
            lambda scenario: "two_ACT_ASAQ_ASPY" if scenario in TWO_ACT else "three_ACT_ASAQ_DHAPPQ_ASPY"
        )
        runs["private_market"] = market
        replicate_parts.append(runs[["private_market", "policy_group", "monthly_tf"]])
        for scenario, group in runs.groupby("scenario_clean"):
            rows.append({
                "private_market": market,
                "scenario": scenario,
                "strategy": TARGETS[scenario],
                "policy_group": "two_ACT_ASAQ_ASPY" if scenario in TWO_ACT else "three_ACT_ASAQ_DHAPPQ_ASPY",
                "replicates": len(group),
                "median_monthly_tf": group.monthly_tf.median(),
                "p05_monthly_tf": group.monthly_tf.quantile(.05),
                "p95_monthly_tf": group.monthly_tf.quantile(.95),
                "mean_monthly_tf": group.monthly_tf.mean(),
                "reduction_vs_status_quo_pct": 100 * (baseline_median - group.monthly_tf.median()) / baseline_median,
            })

    result = pd.DataFrame(rows)
    output = RESULTS_DIR / "ntfs_aspy_summary.csv"
    average_output = RESULTS_DIR / "ntfs_aspy_group_summary.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False, float_format="%.1f")
    averages = result.groupby(["private_market", "policy_group"], sort=False).agg(
        policies=("scenario", "count"),
        replicates_per_policy=("replicates", "min"),
        average_of_policy_medians=("median_monthly_tf", "mean"),
        lowest_policy_reduction_pct=("reduction_vs_status_quo_pct", "min"),
        highest_policy_reduction_pct=("reduction_vs_status_quo_pct", "max"),
    ).reset_index()
    pooled = pd.concat(replicate_parts, ignore_index=True).groupby(
        ["private_market", "policy_group"], sort=False
    ).monthly_tf.agg(
        pooled_replicate_mean_monthly_tf="mean",
        pooled_replicate_median_monthly_tf="median",
        pooled_replicates="size",
    ).reset_index()
    averages = averages.merge(pooled, on=["private_market", "policy_group"], validate="one_to_one")
    averages.to_csv(average_output, index=False, float_format="%.1f")
    for market, group in result.groupby("private_market", sort=False):
        print(f"\nPrivate market: {market}")
        print(group[["strategy", "replicates", "median_monthly_tf", "p05_monthly_tf", "p95_monthly_tf", "reduction_vs_status_quo_pct"]]
              .to_string(index=False, formatters={
                  "median_monthly_tf": "{:,.1f}".format,
                  "p05_monthly_tf": "{:,.1f}".format,
                  "p95_monthly_tf": "{:,.1f}".format,
                  "mean_monthly_tf": "{:,.1f}".format,
              }))
    print("\nAverage of policy medians and policy reduction range:")
    print(averages.to_string(index=False, formatters={
        "average_of_policy_medians": "{:,.1f}".format,
        "pooled_replicate_mean_monthly_tf": "{:,.1f}".format,
        "pooled_replicate_median_monthly_tf": "{:,.1f}".format,
        "lowest_policy_reduction_pct": "{:.1f}%".format,
        "highest_policy_reduction_pct": "{:.1f}%".format,
    }))
    print(f"Saved {output}")
    print(f"Saved {average_output}")


if __name__ == "__main__":
    main()
