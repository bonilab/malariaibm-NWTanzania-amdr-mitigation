# malariaibm-NWTanzania-amdr-mitigation

Analysis code, local input data, generated figures, and manuscript materials for modelling antimalarial drug-resistance mitigation strategies in northwest Tanzania.

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

The current project layout separates analysis code, local datasets, generated figures, manuscript files, and table destinations.

```text
.
├── .gitignore              # Excludes Python caches and temporary files
├── README.md
├── model/
│   └── source_code/       # Placeholder for the C++ model source snapshot
├── scenarios/
│   └── inputs/             # Scenario inputs and configuration files
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
├── publication/            # Manuscript and supplementary document drafts
└── tables/                 # Reserved output locations
    ├── main/
    └── supplementary/
```

The scenario, model snapshot, and table directories are currently placeholders awaiting files. The model environment specification has not yet been added.

## Reproducibility

The analysis scripts, figure outputs, and raw and processed datasets are organized in this repository. Reproducing a figure requires the corresponding inputs under `analysis/data/` at the paths listed in `analysis/README.md`. The analysis README also gives the script to run for each output.

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

> Nguyen TD, Ishengoma D, Ballard S-B, Zupko RJ, Farinha CC, et al.  
> **Responding to the local emergence of partial artemisinin resistance in northwest Tanzania: a modelling study.**  
> Manuscript in preparation.

A complete citation will be added after publication.

## Development status

This repository currently contains analysis scripts, figure outputs, analysis documentation, local data folders, and manuscript drafts for the northwest Tanzania antimalarial drug-resistance mitigation study. The C++ model source snapshot and its environment specification are still to be added under `model/`.

## Contact

For questions about the modelling framework or analyses, please open a GitHub issue or contact the corresponding authors of the associated manuscript.
