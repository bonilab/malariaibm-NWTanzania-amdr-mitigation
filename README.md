# Tanzania AMDR Model — Phase 1

Code, input data, simulation outputs, and analysis workflows for Phase 1 of the Tanzania antimalarial drug-resistance (AMDR) modelling project.

Phase 1 focuses on northwest Tanzania, including **Kagera, Kigoma, Geita, and Mwanza**, with particular emphasis on the emergence of *Plasmodium falciparum* `pfkelch13` R561H in Kagera and strategies to mitigate the spread and impact of antimalarial drug resistance.

This repository supports the manuscript:

**Responding to the local emergence of partial artemisinin resistance in northwest Tanzania: a modelling study**

## Overview

We use a spatially explicit individual-based model of *P. falciparum* transmission and evolution to evaluate alternative antimalarial treatment strategies in northwest Tanzania.

The analysis considers:

- first-line ACT switches;
- multiple first-line therapies (MFT);
- ACT cycling and rotation;
- triple ACT deployment;
- delayed treatment-policy changes;
- region-specific deployment strategies;
- artesunate-pyronaridine deployment under alternative assumptions about pyronaridine resistance;
- different assumptions about the size of the private antimalarial market.

Interventions are evaluated over the six-year period from **January 1, 2026 to January 1, 2032**.

The main outcomes include:

- average monthly treatment failures;
- reduction in treatment failures relative to continued artemether-lumefantrine use;
- changes in resistance-associated genotype frequencies, including `pfkelch13` R561H.

## Geographic scope

Phase 1 includes four regions of northwest Tanzania:

- Kagera
- Kigoma
- Geita
- Mwanza

Kagera is the primary region of interest because of the recent emergence and increasing frequency of `pfkelch13` R561H.

Future phases of the Tanzania AMDR modelling project are intended to expand the analysis toward national-scale treatment and resistance-mitigation planning.

## Treatment strategies

The model evaluates strategies involving:

- artemether-lumefantrine (AL);
- artesunate-amodiaquine (ASAQ);
- dihydroartemisinin-piperaquine (DHA-PPQ);
- artesunate-pyronaridine (ASPY);
- artemether-lumefantrine-amodiaquine triple ACT (ALAQ).

A total of **87 unique ACT deployment strategies** were generated, including immediate switches, delayed switches, MFT, cycling, triple ACT deployment, and geographically differentiated strategies.

## Baseline scenarios

Four main baseline scenarios are considered, combining:

- **47% private-market treatment** or **10% private-market treatment**; and
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
- processed simulation outputs underlying manuscript figures and tables;
- documentation describing the relationship between repository outputs and manuscript figures.

Large raw simulation outputs may be archived separately if they exceed practical GitHub storage limits.

A tagged release corresponding to the submitted or published manuscript will be created so that the exact analysis version remains reproducible independently of subsequent development.

## Data sources

The model uses data from multiple sources, including:

- Tanzania Demographic and Health Surveys;
- Tanzania National Malaria Control Programme data;
- Malaria Atlas Project estimates;
- WorldPop population data;
- published molecular surveillance studies;
- published therapeutic efficacy studies;
- other publicly available epidemiological and antimalarial resistance datasets.

Some source data may be subject to redistribution restrictions. Where redistribution is not permitted, this repository will provide documentation and links to the original source rather than reproducing those data.

## Citation

If you use this repository, please cite the associated manuscript:

> Nguyen TD, Ishengoma D, Ballard S-B, Zupko RJ, Farinha CC, et al.  
> *Responding to the local emergence of partial artemisinin resistance in northwest Tanzania: a modelling study.*  
> Manuscript in preparation.

A complete citation will be added after publication.

## Development status

This repository corresponds to **Phase 1** of the Tanzania AMDR modelling project.

Phase 1 focuses on northwest Tanzania and the response to emerging artemisinin partial resistance in and around Kagera region.

Later phases are intended to extend the framework to broader national-scale analyses.

## Contact

For questions about the modelling framework or analyses, please open a GitHub issue or contact the corresponding authors of the associated manuscript.
