"""Count strategies with at least approximately 50% ASAQ use and >=35% fewer failures.

ASAQ share is based on the six-year deployment schedule in the strategy label.
Cycling schedules repeat until the six-year period ends. Region-specific
strategies are weighted by the modeled baseline population in each district.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from ntfs_table_utils import LABELS, RESULTS_DIR, SETTINGS, load_setting, six_year_runs


ROOT = Path(__file__).resolve().parents[2]
PERIOD_YEARS = 6
# Treat shares that round to 50% to one decimal place as "near 50%".
NEAR_HALF_SHARE_CUTOFF = 0.495


def outside_kagera_population_share() -> float:
    """Compute the population weight outside Kagera (district 2)."""
    input_dir = ROOT / "scenarios/inputs/005/095-region-specific-Kagera-DHAPPQ-Others-ASAQ-Delay-0y/input"
    population = np.loadtxt(input_dir / "kag_initial_population.asc", skiprows=6)
    districts = np.loadtxt(input_dir / "kag_districts.asc", skiprows=6)
    valid = np.isin(districts, [1, 2, 3, 4])
    total = population[valid].sum()
    outside = population[valid & (districts != 2)].sum()
    return float(outside / total)


def asaq_share(strategy_id: str, label: str) -> float | None:
    """Return the six-year planned share of treatments assigned to ASAQ."""

    if label.startswith("MFT"):
        match = re.search(r"ASAQ\s+(\d+)%", label)
        return int(match.group(1)) / 100 if match else 0.0

    if label.startswith("Cycling"):
        therapies = re.findall(r"(AL|ASAQ|DHAPPQ)\s+(\d+)y", label)
        if not therapies:
            return 0.0
        asaq_years = 0
        elapsed = 0
        while elapsed < PERIOD_YEARS:
            for therapy, duration in therapies:
                duration = int(duration)
                used = min(duration, PERIOD_YEARS - elapsed)
                if therapy == "ASAQ":
                    asaq_years += used
                elapsed += used
                if elapsed >= PERIOD_YEARS:
                    break
        return asaq_years / PERIOD_YEARS

    if label.startswith("Triple ACT"):
        match = re.search(r"ASAQ\s+(\d+)y", label)
        return int(match.group(1)) / 6 if match else 0.0

    if label.startswith("Basic switch"):
        return 1.0 if "ASAQ" in label else 0.0

    if label.startswith("Delay"):
        match = re.search(r"ASAQ\s+(\d+)y", label)
        # The label's duration is the delay before switching to ASAQ.
        return (6 - int(match.group(1))) / 6 if match else 0.0

    if label.startswith("Kagera first"):
        outside_share = outside_kagera_population_share()
        if "first | ASAQ" in label:
            match = re.search(r"Others ASAQ - Delay (\d+)y", label)
            others_share = (6 - int(match.group(1))) / 6 if match else 0.0
            return (1 - outside_share) + outside_share * others_share
        match = re.search(r"Others ASAQ - Delay (\d+)y", label)
        others_share = (6 - int(match.group(1))) / 6 if match else 0.0
        return outside_share * others_share

    return 0.0


def summarize(setting: str, market: str) -> tuple[dict[str, object], pd.DataFrame]:
    data = load_setting(setting)
    runs = six_year_runs(data)
    runs["monthly_tf"] = runs["ntf_6y"] / 72
    baseline = runs.loc[runs.scenario_clean.eq("000-status-quo"), "monthly_tf"].median()
    summary = runs.groupby("scenario_clean").monthly_tf.median().rename("monthly_tf_median").reset_index()
    summary["reduction_pct"] = 100 * (baseline - summary.monthly_tf_median) / baseline
    summary["asaq_share"] = summary.scenario_clean.map(
        lambda sid: asaq_share(sid, LABELS.get(sid, ""))
    )
    eligible = summary.loc[summary.asaq_share.ge(NEAR_HALF_SHARE_CUTOFF)].copy()
    eligible["reduction_at_least_25pct"] = eligible.reduction_pct.ge(25)
    eligible["reduction_at_least_35pct"] = eligible.reduction_pct.ge(35)
    qualifying_25 = eligible.loc[eligible.reduction_at_least_25pct]
    qualifying_35 = eligible.loc[eligible.reduction_at_least_35pct]
    result = {
        "private_market": market,
        "strategies_with_asaq_share_at_or_near_50pct": len(eligible),
        "strategies_with_reduction_at_least_25pct": len(qualifying_25),
        "strategies_with_reduction_at_least_35pct": len(qualifying_35),
        "strategy_ids_reduction_at_least_25pct": ", ".join(qualifying_25.scenario_clean),
        "strategy_ids_reduction_at_least_35pct": ", ".join(qualifying_35.scenario_clean),
    }
    eligible["private_market"] = market
    return result, eligible


def main() -> None:
    summaries, details = zip(*(summarize(setting, market) for setting, market in SETTINGS.items()))
    result = pd.DataFrame(summaries)
    out_summary = RESULTS_DIR / "asaq_majority_reduction_count.csv"
    out_details = RESULTS_DIR / "asaq_majority_strategy_details.csv"
    result.to_csv(out_summary, index=False)
    pd.concat(details, ignore_index=True).to_csv(out_details, index=False, float_format="%.3f")
    print(result.to_string(index=False))
    print(f"Saved {out_summary}")
    print(f"Saved {out_details}")


if __name__ == "__main__":
    main()
