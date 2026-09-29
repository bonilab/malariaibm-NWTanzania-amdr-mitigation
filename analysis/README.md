# Publication analysis

Processed inputs and scripts for publication figures and tables are organized here. Final outputs are written to the root-level `figures/` and `tables/` folders.

## Current structure

```text
analysis/
├── config/                 # Figure labels and annotation positions
├── data/processed/         # Shared processed data, organized by scenario
│   └── scenarios/004–007/  # Scenario-level CSV inputs
├── results/                # Derived analysis summaries, such as p-values
└── scripts/                # Reproducible figure and summary-generation scripts

figures/
├── main/                   # Main-text figures
└── supplementary/          # Supplementary figures

tables/
├── main/                   # Main-text tables
└── supplementary/          # Supplementary tables
```

## Figure 2

- Script: `scripts/figure_02_mft_cycling.py`
- Inputs: shared processed scenario data in `data/processed/scenarios/`. Figure 2 currently uses scenario `004` (47% private market); scenario `005` (10% private market) is also available for other analyses.
- Output: `../figures/main/figure-02.pdf`

From the repository root, run `python3 analysis/scripts/figure_02_mft_cycling.py` to regenerate the arrow-free PDF. The script displays MFT strategies above status quo and two-year cycling strategies below it.

## Figure 3 and Supplementary Figures 7–9

- Plot script: `scripts/figure_03_al_use.py`
- P-value script: `scripts/calculate_al_use_correlations.py`
- Inputs: shared `data/processed/scenarios/004/` through `007/` `al_used.csv` files.
- Plot outputs: `../figures/main/figure-03.png` and `../figures/supplementary/supplementary-figure-07.png` through `supplementary-figure-09.png`.
- Correlation results: `results/figure_03_al_use_correlations.csv`.

Run `python3 analysis/scripts/figure_03_al_use.py` to regenerate all four plots and `python3 analysis/scripts/calculate_al_use_correlations.py` to recalculate Pearson correlations and p-values. Plot labels and their manual positions are stored in `config/`.

## Figure 4 and Supplementary Figure 10

- Script: `scripts/figure_04_private_market_effect.py`
- Inputs: `ntfs_6y.csv` and `k13_frequency_at_2031.csv` from scenario folders `004`–`007` under `data/processed/scenarios/`.
- Outputs: `../figures/main/figure-04.png` and `../figures/supplementary/supplementary-figure-10.png`.
- Strategy labels: `config/figure_04_strategy_labels.json`.

Run `python3 analysis/scripts/figure_04_private_market_effect.py` from the repository root to regenerate both plots. Figure 4 compares scenarios `004` and `005`; Supplementary Figure 10 compares `006` and `007`.

## Figure 5 and Supplementary Figures 13–15

- Plot script: `scripts/figure_05_delay_asaq.py`
- Main-text number extraction: `scripts/summarize_delay_asaq_main_text.py`
- Inputs: shared `data/processed/scenarios/004/` through `007/` `all_monthly_data.csv.xz` files.
- Plot outputs: `../figures/main/figure-05.png` and `../figures/supplementary/supplementary-figure-13.png` through `supplementary-figure-15.png`.
- Main-text summary: `results/delay_asaq_percent_increase_from_medians.csv`.

Run `python3 analysis/scripts/figure_05_delay_asaq.py` to regenerate all four plots. Run `python3 analysis/scripts/summarize_delay_asaq_main_text.py` to extract the median six-year treatment failures and percentage increases for each delay and scenario set. The summary uses January 2026 through December 2031 (72 months).


## Supplementary Figure 16

- Script: `scripts/supplementary_figure_16_treatment_failure_trajectories.py`
- Input: `data/processed/scenarios/004/all_monthly_data.csv.xz` (shared processed scenario data).
- Output: `../figures/supplementary/supplementary-figure-16.png`.

Run `python3 analysis/scripts/supplementary_figure_16_treatment_failure_trajectories.py` from the repository root. The script draws a 4-by-4 trajectory layout with 90% simulation intervals, trailing 12-month smoothing, and a 2026 reference line.


## Supplementary Figure 17

- Script: `scripts/supplementary_figure_17_genotype_heatmap.py`
- Raw inputs: `data/raw/004/000-status-quo_20.db`, `data/raw/004/001-basic-ASAQ_20.db`, and `data/raw/004/070-tact-ALAQ-immediate_20.db`.
- Output: `../figures/supplementary/supplementary-figure-17.png`. The script generates the PNG from the raw databases.

Run `python3 analysis/scripts/supplementary_figure_17_genotype_heatmap.py` from the repository root with the three databases at the paths above.


## Supplementary Figures 11 and 12

- Script: `scripts/supplementary_figure_11_12_aspy.py`
- Inputs: `data/processed/aspy/all_aspy_monthly_data.part-01.csv.xz` through `part-03.csv.xz`.
- Outputs: `../figures/supplementary/supplementary-figure-11.png` and `supplementary-figure-12.png`.

Run `python3 analysis/scripts/supplementary_figure_11_12_aspy.py` from the repository root. The script reads and combines the three compressed CSV parts.


## Supplementary Figure 3

- Script: `scripts/supplementary_figure_03_genotype_calibration.py`
- Inputs: 15 calibration run databases (`data/raw/supplementary_figure_03/monthly_data_0.db` through `monthly_data_14.db`) and shared `data/raw/shared/ref_genotype_data.csv`.
- Outputs: `../figures/supplementary/supplementary-figure-03.png` and `results/supplementary_figure_03_2023_genotype_frequencies.csv`.

Run `python3 analysis/scripts/supplementary_figure_03_genotype_calibration.py` from the repository root. Model location IDs use the configured region mapping; reference points are matched to panels by their `region` names.


## Supplementary Figure 4

- Script: `scripts/supplementary_figure_04_genotype_calibration.py`
- Inputs: 15 calibration run databases in `data/raw/supplementary_figure_04/` and the shared `data/raw/shared/ref_genotype_data.csv`.
- Outputs: `../figures/supplementary/supplementary-figure-04.png` and `results/supplementary_figure_04_2023_genotype_frequencies.csv`.

Run `python3 analysis/scripts/supplementary_figure_04_genotype_calibration.py` from the repository root.


## Supplementary Figures 5 and 6

- Scripts: `scripts/supplementary_figure_05_genotype_calibration.py` and `scripts/supplementary_figure_06_genotype_calibration.py`.
- Inputs: calibration run databases in `data/raw/supplementary_figure_05/` (runs 0–15) and `data/raw/supplementary_figure_06/` (runs 0–14), plus shared `data/raw/shared/ref_genotype_data.csv`.
- Outputs: `../figures/supplementary/supplementary-figure-05.png`, `../figures/supplementary/supplementary-figure-06.png`, and corresponding 2023 summary CSVs under `results/`.

Run each script from the repository root. Supplementary Figure 5 data extend through January 2024, so its x-axis includes that additional year; Figure 6 data end in January 2023.

Large scenario trajectories are stored as XZ-compressed CSVs (`.csv.xz`) and read directly by pandas. ASPY trajectories are split into three compressed CSV parts to keep each file below GitHub's per-file size limit.


## Supplementary Figure 1

- Script: `scripts/supplementary_figure_01_seasonality_calibration.py`
- Raw Kagera inputs: `data/raw/supplementary_figure_01/kagera_case_reporting_2017_2023/` (`kagera_monthly_incidence_under5s.csv` and `kagera_monthly_incidence_over5s.csv`).
- Processed seasonality data retained from the root: `data/processed/supplementary_figure_01/kag_seasonality_adjusted.csv`.
- Simulation input: `data/processed/supplementary_figure_01/simulation_output_monthly_incidence.csv`, with columns `group`, `Month`, and `incidence`. The script uses this file to plot simulated incidence distributions alongside observed seasonal weights.
- Output: `../figures/supplementary/supplementary-figure-01.png`.

Run `python3 analysis/scripts/supplementary_figure_01_seasonality_calibration.py` from the repository root.


## Supplementary Figure 2

- Script: `scripts/supplementary_figure_02_pfpr_validation.py`
- Inputs: `data/processed/supplementary_figure_02/calibration_data.csv` and `district_pfpr_comparison.csv`.
- Output: `../figures/supplementary/supplementary-figure-02.png`.

Run `python3 analysis/scripts/supplementary_figure_02_pfpr_validation.py` from the repository root. The plot compares pixel-level PfPR estimates and the district-level model-minus-Atlas differences.
