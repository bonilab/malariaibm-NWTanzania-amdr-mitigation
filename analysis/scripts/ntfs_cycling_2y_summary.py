"""Summarize the pooled six-permutation two-year cycling strategy group."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ntfs_table_utils import DATA_DIR, RESULTS_DIR, SETTINGS, simulation_column


CYCLING = [
    "021-Cycling-2y-AL-ASAQ-DHAPPQ",
    "022-Cycling-2y-AL-DHAPPQ-ASAQ",
    "023-Cycling-2y-ASAQ-AL-DHAPPQ",
    "024-Cycling-2y-ASAQ-DHAPPQ-AL",
    "025-Cycling-2y-DHAPPQ-AL-ASAQ",
    "026-Cycling-2y-DHAPPQ-ASAQ-AL",
]


def summarize(setting: str, market: str) -> dict[str, float | int | str]:
    data = pd.read_csv(DATA_DIR / setting / "ntfs_6y.csv")
    data["scenario_clean"] = data["scenario"].str.replace(r"^\d+/", "", regex=True)
    sim_col = simulation_column(data)
    status = data.loc[data.scenario_clean.eq("000-status-quo")]
    cycling = data.loc[data.scenario_clean.isin(CYCLING)].copy()
    if status.empty or cycling.empty:
        raise ValueError(f"Missing status quo or 2-year cycling results in setting {setting}")

    baseline = status.groupby(sim_col).total_treatmentfailures.sum() / 72
    baseline_median = baseline.median()
    cycling["pooled_run"] = cycling.scenario_clean.astype(str) + "__" + cycling[sim_col].astype(str)
    monthly = cycling.groupby("pooled_run").total_treatmentfailures.sum() / 72
    median, low, high = monthly.median(), np.percentile(monthly, 5), np.percentile(monthly, 95)
    reduction = 100 * (baseline_median - median) / baseline_median
    reduction_low = 100 * (baseline_median - high) / baseline_median
    reduction_high = 100 * (baseline_median - low) / baseline_median
    return {
        "private_market": market,
        "runs": len(monthly),
        "monthly_tf_median": median,
        "monthly_tf_p05": low,
        "monthly_tf_p95": high,
        "status_quo_monthly_tf_median": baseline_median,
        "reduction_median_pct": reduction,
        "reduction_p05_pct": reduction_low,
        "reduction_p95_pct": reduction_high,
    }


def main() -> None:
    result = pd.DataFrame(summarize(setting, market) for setting, market in SETTINGS.items())
    output = RESULTS_DIR / "ntfs_cycling_2y_summary.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False, float_format="%.1f")
    print(result.to_string(index=False, formatters={
        "monthly_tf_median": "{:,.1f}".format,
        "monthly_tf_p05": "{:,.1f}".format,
        "monthly_tf_p95": "{:,.1f}".format,
        "status_quo_monthly_tf_median": "{:,.1f}".format,
        "reduction_median_pct": "{:.1f}%".format,
        "reduction_p05_pct": "{:.1f}%".format,
        "reduction_p95_pct": "{:.1f}%".format,
    }))
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
