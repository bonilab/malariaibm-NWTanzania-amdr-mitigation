"""Summarize monthly treatment failures for the three AS-PY mixtures."""

from __future__ import annotations

import pandas as pd

from ntfs_table_utils import DATA_DIR, RESULTS_DIR, SETTINGS, six_year_runs


TARGETS = {
    "080-mft-ASAQ_50-ASPY85_50": "MFT | ASAQ 50% | ASPY85 50%",
    "081-mft-ASAQ_50-ASPY75_50": "MFT | ASAQ 50% | ASPY75 50%",
    "082-mft-ASAQ_50-ASPY65_50": "MFT | ASAQ 50% | ASPY65 50%",
}


def main() -> None:
    rows = []
    for setting, market in SETTINGS.items():
        data = pd.read_csv(DATA_DIR / setting / "ntfs_6y.csv")
        data["scenario_clean"] = data["scenario"].str.replace(r"^\d+/", "", regex=True)
        data = data.loc[data["scenario_clean"].isin(TARGETS)]
        if data.empty:
            raise ValueError(f"No target ASPY strategies found in setting {setting}")
        runs = six_year_runs(data)
        runs["monthly_tf"] = runs["ntf_6y"] / 72
        for scenario, group in runs.groupby("scenario_clean"):
            rows.append({
                "private_market": market,
                "scenario": scenario,
                "strategy": TARGETS[scenario],
                "median_monthly_tf": group.monthly_tf.median(),
                "p05_monthly_tf": group.monthly_tf.quantile(.05),
                "p95_monthly_tf": group.monthly_tf.quantile(.95),
                "mean_monthly_tf": group.monthly_tf.mean(),
            })

    result = pd.DataFrame(rows)
    output = RESULTS_DIR / "ntfs_aspy_summary.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False, float_format="%.1f")
    for market, group in result.groupby("private_market", sort=False):
        print(f"\nPrivate market: {market}")
        print(group[["strategy", "median_monthly_tf", "p05_monthly_tf", "p95_monthly_tf", "mean_monthly_tf"]]
              .to_string(index=False, formatters={
                  "median_monthly_tf": "{:,.1f}".format,
                  "p05_monthly_tf": "{:,.1f}".format,
                  "p95_monthly_tf": "{:,.1f}".format,
                  "mean_monthly_tf": "{:,.1f}".format,
              }))
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
