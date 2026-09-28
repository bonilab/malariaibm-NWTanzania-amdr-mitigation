# malariaibm-NWTanzania-amdr-mitigation

Code, input data, simulation outputs, and analysis workflows for modelling antimalarial drug-resistance mitigation strategies in northwest Tanzania.

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

The repository is organized to separate model configuration, simulation outputs, analysis code, and manuscript figures.

```text
.
├── README.md
├── LICENSE
├── environment/
│
├── model/
│   ├── config/
│   └── ...
│
├── data/
│   ├── input/
│   ├── calibration/
│   └── ...
│
├── scenarios/
│   ├── 004/
│   ├── 005/
│   ├── 006/
│   └── 007/
│
├── analysis/
│   ├── treatment_failures/
│   ├── genotype_frequencies/
│   ├── calibration/
│   └── ...
│
├── figures/
│   ├── main/
│   └── supplementary/
│
└── tables/
    ├── main/
    └── supplementary/
```

The exact directory structure may evolve as the repository is finalized for publication.

## Reproducibility

The repository is intended to contain the materials required to reproduce the principal analyses reported in the manuscript, including:

- model configuration files;
- scenario definitions;
- analysis scripts;
- plotting scripts;
- processed simulation outputs underlying manuscript figures and tables; and
- documentation linking repository outputs to manuscript figures and tables.

Large raw simulation outputs may be archived separately if they exceed practical GitHub storage limits.

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

This repository contains the modelling, data-processing, and analysis materials for the northwest Tanzania antimalarial drug-resistance mitigation study.

Code, processed data, simulation outputs, and manuscript figure-generation workflows will be added as the repository is finalized for publication.

## Contact

For questions about the modelling framework or analyses, please open a GitHub issue or contact the corresponding authors of the associated manuscript.
