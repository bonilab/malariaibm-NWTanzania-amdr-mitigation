# malariaibm-NWTanzania-amdr-mitigation

Analysis code, local input data, and generated figures for modelling antimalarial drug-resistance mitigation strategies in northwest Tanzania.

This repository contains the analyses supporting the manuscript:

> **Responding to the local emergence of partial artemisinin resistance in northwest Tanzania: a modelling study**

The study focuses on Kagera and the surrounding regions of Kigoma, Geita, and Mwanza, with particular emphasis on the emergence and spread of *Plasmodium falciparum* `pfkelch13` R561H and on treatment strategies that could mitigate antimalarial drug resistance.

## Overview

We use a spatially explicit individual-based model of *P. falciparum* transmission and evolution to evaluate alternative antimalarial treatment strategies in northwest Tanzania.

The analysis considers:

- first-line ACT switches;
- multiple first-line therapies (MFT);
- ACT cycling and rotation;
- triple ACT deployment;
- delayed treatment-policy changes;
- region-specific deployment strategies;
- artesunate-pyronaridine deployment under alternative assumptions about pyronaridine resistance; and
- different assumptions about the size of the private antimalarial market.

Interventions are evaluated over the six-year period from January 1, 2026 to January 1, 2032.

The main outcomes include:

- average monthly treatment failures;
- reduction in treatment failures relative to continued artemether-lumefantrine use; and
- changes in resistance-associated genotype frequencies, including `pfkelch13` R561H.

## Geographic scope

The modelled area includes four regions of northwest Tanzania:

- Kagera
- Kigoma
- Geita
- Mwanza

Kagera is the primary region of interest because of the emergence and increasing frequency of `pfkelch13` R561H.

This repository covers the northwest Tanzania analysis described in the associated manuscript. Broader Tanzania modelling work may be maintained separately.

## Treatment strategies

The model evaluates strategies involving:

- artemether-lumefantrine (AL);
- artesunate-amodiaquine (ASAQ);
- dihydroartemisinin-piperaquine (DHA-PPQ);
- artesunate-pyronaridine (ASPY); and
- artemether-lumefantrine-amodiaquine triple ACT (ALAQ).

A total of 87 unique ACT deployment strategies were evaluated, including immediate switches, delayed switches, MFT, cycling, triple ACT deployment, and geographically differentiated strategies.

## Baseline scenarios

Four main baseline scenarios are considered, combining:

- 47% or 10% private-market antimalarial treatment; and
- primary or lower baseline frequencies of `pfcrt` 76T and `pfmdr1` 86Y.

These scenarios are used to evaluate the robustness of projected treatment outcomes and resistance trajectories.

## Repository structure

The current project layout separates analysis code, local datasets, generated figures, and table destinations.

```text
.
├── .gitignore              # Excludes Python caches and temporary files
├── README.md
├── source_code/           # Frozen Temple-Malaria-Simulation v4.1.8 source
├── scenarios/
│   └── inputs/             # Selected inputs for scenarios 004–007, by strategy
├── sample_raw_data/        # 10 raw simulation runs for selected scenario 004 strategies
├── analysis/
│   ├── README.md           # Figure workflows, inputs, outputs, and run commands
│   ├── config/             # Plot labels and annotation configuration
│   ├── data/
│   │   ├── raw/            # Local raw inputs, grouped by figure or shared use
│   │   └── processed/      # Local processed inputs, grouped by scenario or figure
│   ├── results/            # Derived summaries and analysis tables
│   └── scripts/            # Figure-generation and analysis scripts
├── figures/
│   ├── main/               # Main-text figures
│   └── supplementary/     # Supplementary figures
└── tables/                 # Reserved output locations
    ├── main/
    └── supplementary/
```

The frozen model source is from the [`v4.1.8` branch](https://github.com/bonilab/Temple-Malaria-Simulation/tree/v4.1.8), commit `7acaedcfc317744145652708848834e96d5a48ef`, and is stored under `source_code/`. Each scenario input folder preserves the source layout: `scenarios/inputs/<scenario>/<strategy>/input/`. Only `kag_beta.asc`, `kag_districts.asc`, `kag_initial_population.asc`, `kag_input.yml`, `kag_seasonality.csv`, and `kag_treatment.asc` are included there. `sample_raw_data/004/` contains raw database runs 0–9 for `000-status-quo`, `001-basic-ASAQ`, and `070-tact-ALAQ-immediate`; the remaining runs and generated CSVs are stored elsewhere. The model environment specification has not yet been added.

## Reproducibility

The analysis scripts, figure outputs, and raw and processed datasets are organized in this repository. Reproducing a figure requires the corresponding inputs under `analysis/data/` or `scenarios/inputs/` at the paths listed in `analysis/README.md` and this README. The analysis README also gives the script to run for each output.

A tagged release corresponding to the submitted or published manuscript will be created so that the exact analysis version remains reproducible independently of subsequent development.

## Data sources

The model uses data from multiple sources, including:

- Tanzania Demographic and Health Surveys;
- Tanzania National Malaria Control Programme data;
- Malaria Atlas Project estimates;
- WorldPop population data;
- published molecular surveillance studies;
- published therapeutic efficacy studies; and
- other publicly available epidemiological and antimalarial-resistance datasets.

Some source data may be subject to redistribution restrictions. Where redistribution is not permitted, this repository will provide documentation and links to the original source rather than reproducing those data.

## Citation

If you use this repository, please cite the associated manuscript:

**Responding to the local emergence of partial artemisinin resistance in northwest Tanzania: a modelling study**

Tran Dang Nguyen (1, 2), Deus Ishengoma (3, 4), Sarah-Blythe Ballard (5), Robert J Zupko (6), Carter C Farinha (1), Kien Trung Tran (1), Sarit Adhikari (1), Abdallah Lusasi (7), Daniel A Petro (1), Chao-Yi Tsai (1), Kefas Mugittu (8), Dunstan Bishanga (8), Daniel Rosen (9), Jessica Vernon (9), Oliver J Watson (10), Jonathan J Juliano (11), Jeff Bailey (12), Mwaka Kakolwa (8), Sigsbert Mkude (13), Celine Mandara (4), Naomi Serbantez, Chonge Kitojo, Sijenunu Aron (7), Samwel Lazaro (7), and Maciej F Boni (1).

1. Institute for Genomics and Evolutionary Medicine, Department of Biology, Temple University, Philadelphia, PA, USA
2. Center for Computational Epidemiology and Infectious Diseases, Ho Chi Minh City, Vietnam
3. Ifakara Health Institute, Dar es Salaam, Tanzania
4. National Institute for Medical Research, Dar es Salaam, Tanzania
5. Department of International Health, Johns Hopkins Bloomberg School of Public Health, Johns Hopkins University, Baltimore, MD
6. Center for Infectious Disease Dynamics, Department of Biology, Pennsylvania State University, University Park, PA
7. National Malaria Control Program, Dodoma, Tanzania
8. Shinda Malaria Project, Ifakara Health Institute, Dar es Salaam, Tanzania
9. MaishaMeds Full Name, City, Country
10. Imperial
11. UNC
12. Brown
13. Dhibiti Malaria Project, Population Services International, CITY, COUNTRY

Manuscript in preparation.

A complete citation will be added after publication.

## Development status

This repository currently contains the analysis scripts, figure outputs, analysis documentation, local data folders, and the frozen model source snapshot for the northwest Tanzania antimalarial drug-resistance mitigation study. The model environment specification has not yet been added.

## Contact

For questions about the modelling framework or analyses, please open a GitHub issue or contact the corresponding authors of the associated manuscript.
