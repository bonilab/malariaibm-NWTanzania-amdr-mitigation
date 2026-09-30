"""Shared inputs and summaries for the NTFS notebook exports."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "analysis" / "data" / "processed" / "scenarios"
RESULTS_DIR = ROOT / "analysis" / "results"
LABELS = json.loads((ROOT / "analysis/config/figure_04_strategy_labels.json").read_text())
SETTINGS = {"004": "47%", "005": "10%"}
MONTHS = 72
ID_CANDIDATES = ("run", "replicate", "simulation", "sim_id", "seed", "iteration")


def load_setting(setting: str) -> pd.DataFrame:
    path = DATA_DIR / setting / "ntfs_6y.csv"
    data = pd.read_csv(path)
    required = {"scenario", "total_treatmentfailures"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {', '.join(sorted(missing))}")
    data["scenario_clean"] = data["scenario"].str.replace(r"^\d+/", "", regex=True)
    return data


def simulation_column(data: pd.DataFrame) -> str:
    column = next((name for name in ID_CANDIDATES if name in data.columns), None)
    if column is None:
        raise ValueError(f"Cannot identify simulation ID column. Columns: {list(data.columns)}")
    return column


def six_year_runs(data: pd.DataFrame) -> pd.DataFrame:
    sim_col = simulation_column(data)
    return (
        data.groupby(["scenario_clean", sim_col])["total_treatmentfailures"]
        .sum()
        .rename("ntf_6y")
        .reset_index()
    )


def interval_summary(values: pd.Series) -> tuple[float, float, float, float]:
    return (
        float(values.median()),
        float(np.percentile(values, 5)),
        float(np.percentile(values, 95)),
        float(values.mean()),
    )


def format_interval(median: float, low: float, high: float, precision: int = 0) -> str:
    if precision == 0:
        return f"{median:,.0f} ({low:,.0f}–{high:,.0f})"
    return f"{median:,.{precision}f} ({low:,.{precision}f}–{high:,.{precision}f})"
