"""Calculate Pearson correlations used to describe Figure 3 and its supplements."""

from pathlib import Path

import pandas as pd
from scipy.stats import pearsonr
from figure_03_al_use import DATA_DIR, SETTINGS, population_al_use


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "analysis" / "results" / "figure_03_al_use_correlations.csv"
SETTING_NAMES = {
    "004": "47% private market, primary baseline",
    "005": "10% private market, primary baseline",
    "006": "47% private market, alternative baseline",
    "007": "10% private market, alternative baseline",
}


def main() -> None:
    rows = []
    for setting, (private_share, _) in SETTINGS.items():
        data = pd.read_csv(DATA_DIR / setting / "al_used.csv")
        data = population_al_use(data, setting, private_share)
        correlation, p_value = pearsonr(data["al_used"], data["total_treatmentfailures"])
        rows.append({
            "scenario_set": setting,
            "description": SETTING_NAMES[setting],
            "n_simulations": len(data),
            "pearson_r": correlation,
            # Match the notebook's reporting threshold for underflowed p-values.
            "p_value": f"<2.2e-16" if p_value < 2.2e-16 else f"{p_value:.2e}",
        })

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(RESULTS, index=False, float_format="%.12g")
    print(pd.DataFrame(rows).to_string(index=False))
    print(f"Saved {RESULTS}")


if __name__ == "__main__":
    main()
