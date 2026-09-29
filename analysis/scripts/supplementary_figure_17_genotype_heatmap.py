# ============================================================
# Representative single-run genotype trajectories
# New Tanzania evaluation
#
# Rows:
#   A. Status quo: AL
#   B. Immediate switch to ASAQ
#   C. Immediate switch to ALAQ
#
# R561 genotypes -> cool colors (blue / green)
# 561H genotypes -> warm colors (orange / red)
#
# Same genotype keeps the same color across all rows.
# ============================================================

import os
import sqlite3

from itertools import product
from datetime import datetime

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.cm as cm

import seaborn as sns

from matplotlib.colors import (
    LinearSegmentedColormap,
    Normalize,
)
from matplotlib.cm import ScalarMappable


# ============================================================
# CONFIGURATION
# ============================================================

# Main evaluation folder
# 004 = 47% private market - normal 76/86
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAIN_FOLDER = os.path.join(ROOT, "analysis", "data", "raw", "004")


# ------------------------------------------------------------
# Select one representative run for each strategy
# ------------------------------------------------------------

RUN_STATUS_QUO = 20
RUN_ASAQ = 20
RUN_ALAQ = 20


SCENARIOS = [
    {
        "scenario": "000-status-quo",
        "run": RUN_STATUS_QUO,
        "row_label": "A. Status quo: AL",
        "title": "Status quo: continued AL",
    },
    {
        "scenario": "001-basic-ASAQ",
        "run": RUN_ASAQ,
        "row_label": "B. Immediate switch to ASAQ",
        "title": "Immediate switch to ASAQ",
    },
    {
        "scenario": "070-tact-ALAQ-immediate",
        "run": RUN_ALAQ,
        "row_label": "C. Immediate switch to ALAQ",
        "title": "Immediate switch to ALAQ",
    },
]


# ------------------------------------------------------------
# Plot settings
# ------------------------------------------------------------

DATE_START = datetime(2024, 1, 1)
DATE_END = datetime(2032, 1, 1)

INTERVENTION_DATE = pd.Timestamp("2026-01-01")

# Genotypes below this are removed from heatmap completely
FREQUENCY_LIMIT = 0.0015

# Genotypes exceeding this median frequency at any point
# between DATE_START and DATE_END are shown as line trajectories
LINE_FREQUENCY_LIMIT = 0.05

# Figure size
FIGSIZE = (14, 14)

OUTPUT_FILE = os.path.join(
    ROOT, "figures", "supplementary", "supplementary-figure-17.png"
)



REQUIRED_DATABASES = [
    os.path.join(MAIN_FOLDER, f"{cfg['scenario']}_{cfg['run']}.db")
    for cfg in SCENARIOS
]
missing_databases = [path for path in REQUIRED_DATABASES if not os.path.exists(path)]
if missing_databases:
    expected = "\n".join(f"  - {path}" for path in missing_databases)
    raise FileNotFoundError(
        "Supplementary Figure 17 requires these raw simulation databases:\n" + expected
    )

# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_date(db_path):
    """
    Return mapping:
        monthlydataid -> date
    """

    with sqlite3.connect(db_path) as conn:

        df = pd.read_sql_query(
            """
            SELECT
                id AS monthlydataid,
                modeltime
            FROM monthlydata
            """,
            conn,
        )

    df["date"] = pd.to_datetime(
        df["modeltime"],
        unit="s",
    )

    return df[
        [
            "monthlydataid",
            "date",
        ]
    ]


def get_genotype_mapping(db_path):
    """
    Return mapping:
        genome ID -> genotype name
    """

    with sqlite3.connect(db_path) as conn:

        rows = conn.execute(
            """
            SELECT id, name
            FROM genotype
            """
        ).fetchall()

    return dict(rows)


def get_monthly_genotype_frequency(db_path):
    """
    Calculate genotype frequency for each:
        month x location x genotype

    genotype frequency =
        weighted occurrences / infected individuals
    """

    with sqlite3.connect(db_path) as conn:

        df_joined = pd.read_sql_query(
            """
            SELECT
                mgd.monthlydataid,
                mgd.locationid,
                mgd.genomeid,
                mgd.weightedoccurrences,
                msd.infectedindividuals

            FROM monthlygenomedata AS mgd

            JOIN monthlysitedata AS msd

              ON mgd.monthlydataid = msd.monthlydataid
             AND mgd.locationid = msd.locationid
            """,
            conn,
        )

        all_monthlydata_ids = pd.read_sql_query(
            """
            SELECT id AS monthlydataid
            FROM monthlydata
            """,
            conn,
        )

        all_location_ids = pd.read_sql_query(
            """
            SELECT DISTINCT locationid
            FROM monthlygenomedata
            """,
            conn,
        )

        all_genotypes = pd.read_sql_query(
            """
            SELECT id AS genomeid
            FROM genotype
            """,
            conn,
        )


    # --------------------------------------------------------
    # Frequency
    # --------------------------------------------------------

    df_joined["genotype_frequency"] = np.where(
        df_joined["infectedindividuals"] > 0,
        (
            df_joined["weightedoccurrences"]
            / df_joined["infectedindividuals"]
        ),
        0.0,
    )


    # --------------------------------------------------------
    # Ensure missing genotype/location/month combinations = 0
    # --------------------------------------------------------

    all_combinations = pd.DataFrame(
        product(
            all_monthlydata_ids["monthlydataid"],
            all_location_ids["locationid"],
            all_genotypes["genomeid"],
        ),
        columns=[
            "monthlydataid",
            "locationid",
            "genomeid",
        ],
    )


    df_final = all_combinations.merge(
        df_joined[
            [
                "monthlydataid",
                "locationid",
                "genomeid",
                "genotype_frequency",
            ]
        ],
        on=[
            "monthlydataid",
            "locationid",
            "genomeid",
        ],
        how="left",
    )

    df_final["genotype_frequency"] = (
        df_final["genotype_frequency"]
        .fillna(0.0)
    )


    # --------------------------------------------------------
    # Wide format
    # --------------------------------------------------------

    return (
        df_final
        .pivot_table(
            index=[
                "monthlydataid",
                "locationid",
            ],
            columns="genomeid",
            values="genotype_frequency",
            fill_value=0.0,
        )
        .reset_index()
    )


# ============================================================
# LOAD ONE RUN
# ============================================================

def load_run(main_folder, scenario, run):

    db_path = os.path.join(
        main_folder,
        f"{scenario}_{run}.db",
    )

    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"\nDatabase not found:\n{db_path}\n"
        )

    print(
        f"Loading {scenario}, run {run}\n"
        f"  {db_path}"
    )


    # --------------------------------------------------------
    # Dates
    # --------------------------------------------------------

    dates = get_date(db_path)


    # --------------------------------------------------------
    # Genotype frequencies
    # --------------------------------------------------------

    monthly_gen_frequency = (
        get_monthly_genotype_frequency(
            db_path
        )
    )

    genotype_mapping = (
        get_genotype_mapping(
            db_path
        )
    )

    monthly_gen_frequency.columns = [
        genotype_mapping.get(col, col)
        for col
        in monthly_gen_frequency.columns
    ]

    monthly_gen_frequency = (
        monthly_gen_frequency
        .merge(
            dates,
            on="monthlydataid",
        )
    )


    return {
        "db_path": db_path,
        "genotype": monthly_gen_frequency,
    }


# ============================================================
# GENOTYPE SUMMARY
# ============================================================

def summarize_genotypes(
    monthly_gen_frequency
):

    value_columns = [
        c
        for c
        in monthly_gen_frequency.columns
        if c not in [
            "monthlydataid",
            "locationid",
            "date",
        ]
    ]

    grouped = (
        monthly_gen_frequency
        .groupby("date")[value_columns]
    )


    # --------------------------------------------------------
    # Median + 90% interval across locations
    # --------------------------------------------------------

    median_df = grouped.median()

    q05_df = grouped.quantile(
        0.05
    )

    q95_df = grouped.quantile(
        0.95
    )


    # --------------------------------------------------------
    # Remove genotypes never reaching FREQUENCY_LIMIT
    # --------------------------------------------------------

    keep = (
        median_df.max(axis=0)
        > FREQUENCY_LIMIT
    )

    median_df = (
        median_df.loc[:, keep]
    )

    q05_df = (
        q05_df.loc[:, keep]
    )

    q95_df = (
        q95_df.loc[:, keep]
    )


    return (
        median_df,
        q05_df,
        q95_df,
    )


# ============================================================
# HEATMAP DATA
# ============================================================

def make_heatmap_df(
    monthly_gen_frequency
):

    value_columns = [
        c
        for c
        in monthly_gen_frequency.columns
        if c not in [
            "monthlydataid",
            "locationid",
            "date",
        ]
    ]


    # Mean across locations for the heatmap
    plot_df = (
        monthly_gen_frequency
        .groupby("date")[value_columns]
        .mean()
        .T
    )


    # --------------------------------------------------------
    # Restrict date before thresholding
    # --------------------------------------------------------

    plot_df = plot_df.loc[
        :,
        (
            (plot_df.columns >= DATE_START)
            &
            (plot_df.columns <= DATE_END)
        ),
    ]


    # --------------------------------------------------------
    # Keep only genotypes reaching threshold in plotted window
    # --------------------------------------------------------

    keep = (
        plot_df.max(axis=1)
        > FREQUENCY_LIMIT
    )

    plot_df = (
        plot_df.loc[keep]
    )


    return plot_df


# ============================================================
# HEATMAP COLOR MAP
# ============================================================

heatmap_colors = [
    (0.00, "white"),
    (0.10, "#98c1d9"),
    (0.20, "#8faed0"),
    (0.30, "#6f4b9b"),
    (0.40, "#4e3378"),
    (0.50, "#3d245f"),
    (0.60, "#ee6c4d"),
    (0.70, "#e86044"),
    (0.80, "#e2553b"),
    (0.90, "#dc4932"),
    (1.00, "#d43d29"),
]

cmap = LinearSegmentedColormap.from_list(
    "genotype_frequency",
    heatmap_colors,
    N=256,
)


# ============================================================
# STYLE
# ============================================================

sns.set_context("paper")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})


# ============================================================
# LOAD ALL RUNS FIRST
# ============================================================

loaded_runs = {}

for cfg in SCENARIOS:

    loaded_runs[
        cfg["scenario"]
    ] = load_run(
        MAIN_FOLDER,
        cfg["scenario"],
        cfg["run"],
    )


# ============================================================
# DETERMINE GLOBAL MAJOR GENOTYPES
# ============================================================

all_major_genotypes = set()

for cfg in SCENARIOS:

    genotype_df = (
        loaded_runs[
            cfg["scenario"]
        ]["genotype"]
    )

    (
        median_df,
        q05_df,
        q95_df,
    ) = summarize_genotypes(
        genotype_df
    )


    # --------------------------------------------------------
    # Threshold ONLY within plotted interval
    # --------------------------------------------------------

    median_plot_window = (
        median_df.loc[
            (
                median_df.index
                >= DATE_START
            )
            &
            (
                median_df.index
                <= DATE_END
            )
        ]
    )


    for genotype in (
        median_plot_window.columns
    ):

        if (
            median_plot_window[
                genotype
            ].max()
            > LINE_FREQUENCY_LIMIT
        ):
            all_major_genotypes.add(
                genotype
            )


# ============================================================
# BIOLOGICAL COLOR LOGIC
# ============================================================

def genotype_background(name):
    """
    Remove the R561/H561 component for sorting.

    Examples:

        KNY--R1x -> KNY--X1x
        KNY--H1x -> KNY--X1x

    This keeps related R/H backgrounds adjacent.
    """

    return (
        name
        .replace("R1x", "X1x")
        .replace("H1x", "X1x")
    )


def genotype_sort_key(name):

    background = (
        genotype_background(name)
    )

    if "R1x" in name:
        allele_order = 0

    elif "H1x" in name:
        allele_order = 1

    else:
        allele_order = 2

    return (
        background,
        allele_order,
        name,
    )


global_genotype_order = sorted(
    all_major_genotypes,
    key=genotype_sort_key,
)


# ============================================================
# SPLIT INTO R / H / OTHER
# ============================================================

R_genotypes = [
    g
    for g
    in global_genotype_order
    if "R1x" in g
]

H_genotypes = [
    g
    for g
    in global_genotype_order
    if "H1x" in g
]

OTHER_genotypes = [
    g
    for g
    in global_genotype_order
    if (
        g not in R_genotypes
        and g not in H_genotypes
    )
]


# ============================================================
# DEFINE COOL COLORS FOR R
# ============================================================

# Alternating blue / green families gives the R backgrounds
# good separation while keeping them visually "cool".

cool_colors = [
    "#253494",
    "#2c7fb8",
    "#41b6c4",
    "#7fcdbb",
    "#c7e9b4",
    "#ffffcc",
]


# ============================================================
# DEFINE HOT COLORS FOR H
# ============================================================

hot_colors = [
    "#bd0026",
    "#f03b20",
    "#fd8d3c",
    "#feb24c",
    "#fed976",
    "#ffffb2",
]


# ============================================================
# GLOBAL COLOR MAP
# ============================================================

GLOBAL_GENOTYPE_COLORS = {}


for i, genotype in enumerate(
    R_genotypes
):

    GLOBAL_GENOTYPE_COLORS[
        genotype
    ] = cool_colors[
        i % len(cool_colors)
    ]


for i, genotype in enumerate(
    H_genotypes
):

    GLOBAL_GENOTYPE_COLORS[
        genotype
    ] = hot_colors[
        i % len(hot_colors)
    ]


for genotype in OTHER_genotypes:

    GLOBAL_GENOTYPE_COLORS[
        genotype
    ] = "0.45"


print(
    "\nGlobal genotype colors:"
)

for genotype in global_genotype_order:

    print(
        f"{genotype:15s} "
        f"{GLOBAL_GENOTYPE_COLORS[genotype]}"
    )


# ============================================================
# FIGURE
# ============================================================

fig, axes = plt.subplots(
    nrows=3,
    ncols=2,
    figsize=FIGSIZE,
    width_ratios=[
        1.10,
        0.90,
    ],
    sharex=False,
)


# ============================================================
# PLOT EACH STRATEGY
# ============================================================

for row, cfg in enumerate(
    SCENARIOS
):

    run_data = (
        loaded_runs[
            cfg["scenario"]
        ]
    )

    genotype_df = (
        run_data["genotype"]
    )

    ax_freq = axes[row, 0]

    ax_heat = axes[row, 1]


    # ========================================================
    # LEFT:
    # GENOTYPE TRAJECTORIES
    # ========================================================

    (
        median_df,
        q05_df,
        q95_df,
    ) = summarize_genotypes(
        genotype_df
    )


    median_plot_window = (
        median_df.loc[
            (
                median_df.index
                >= DATE_START
            )
            &
            (
                median_df.index
                <= DATE_END
            )
        ]
    )


    # --------------------------------------------------------
    # Keep global ordering
    # --------------------------------------------------------

    major_genotypes = [
        g
        for g
        in global_genotype_order
        if (
            g
            in median_plot_window.columns
            and
            median_plot_window[
                g
            ].max()
            > LINE_FREQUENCY_LIMIT
        )
    ]


    # --------------------------------------------------------
    # Plot trajectories
    # --------------------------------------------------------

    for genotype in (
        major_genotypes
    ):

        color = (
            GLOBAL_GENOTYPE_COLORS[
                genotype
            ]
        )

        ax_freq.plot(
            median_df.index,
            median_df[genotype],
            color=color,
            linewidth=2.0,
            label=genotype,
        )

        ax_freq.fill_between(
            median_df.index,
            q05_df[genotype],
            q95_df[genotype],
            color=color,
            alpha=0.20,
            linewidth=0,
        )


    # ========================================================
    # INTERVENTION START
    # ========================================================

    ax_freq.axvline(
        INTERVENTION_DATE,
        color="black",
        linestyle="--",
        linewidth=1.0,
        alpha=0.65,
    )


    # ========================================================
    # LEFT PANEL FORMATTING
    # ========================================================

    ax_freq.set_xlim(
        DATE_START,
        DATE_END,
    )

    ax_freq.set_ylim(
        bottom=0,
        top=0.60,
    )

    ax_freq.set_ylabel(
        "Genotype frequency"
    )


    if (
        row
        == len(SCENARIOS) - 1
    ):
        ax_freq.set_xlabel(
            "Year"
        )
    else:
        ax_freq.set_xlabel(
            ""
        )


    ax_freq.grid(
        axis="y",
        linewidth=0.5,
        alpha=0.25,
    )


    ax_freq.set_title(
        cfg["title"],
        loc="left",
    )


    # --------------------------------------------------------
    # Row label
    # --------------------------------------------------------

    ax_freq.text(
        -0.14,
        0.5,
        cfg["row_label"],
        transform=ax_freq.transAxes,
        rotation=90,
        va="center",
        ha="center",
        fontweight="bold",
        fontsize=12,
    )


    # ========================================================
    # RIGHT:
    # HEATMAP
    # ========================================================

    heat_df = make_heatmap_df(
        genotype_df
    )


    sns.heatmap(
        heat_df,
        cmap=cmap,
        vmin=0,
        vmax=1,
        ax=ax_heat,
        yticklabels=True,
        xticklabels=False,
        cbar=False,
    )


    # --------------------------------------------------------
    # Heatmap border
    # --------------------------------------------------------

    for spine in (
        ax_heat.spines.values()
    ):

        spine.set_visible(
            True
        )

        spine.set_linewidth(
            0.8
        )


    # ========================================================
    # HEATMAP YEAR TICKS
    # ========================================================

    dates = heat_df.columns

    tick_positions = []
    tick_labels = []


    for i, date in enumerate(
        dates
    ):

        if (
            date.month == 1
            and
            date.year % 2 == 0
        ):

            tick_positions.append(
                i + 0.5
            )

            tick_labels.append(
                str(date.year)
            )


    ax_heat.set_xticks(
        tick_positions
    )

    ax_heat.set_xticklabels(
        tick_labels,
        rotation=0,
    )


    if (
        row
        == len(SCENARIOS) - 1
    ):
        ax_heat.set_xlabel(
            "Year"
        )
    else:
        ax_heat.set_xlabel(
            ""
        )


    # ========================================================
    # INTERVENTION LINE ON HEATMAP
    # ========================================================

    if INTERVENTION_DATE in dates:

        intervention_idx = (
            dates.get_loc(
                INTERVENTION_DATE
            )
        )

        ax_heat.axvline(
            intervention_idx + 0.5,
            color="black",
            linestyle="--",
            linewidth=1.0,
            alpha=0.65,
        )


    # ========================================================
    # COLOR HEATMAP LABELS TO MATCH TRAJECTORIES
    # ========================================================

    for label in (
        ax_heat.get_yticklabels()
    ):

        genotype = (
            label.get_text()
        )

        if (
            genotype
            in GLOBAL_GENOTYPE_COLORS
            and
            genotype
            in major_genotypes
        ):

            label.set_color(
                GLOBAL_GENOTYPE_COLORS[
                    genotype
                ]
            )

            label.set_fontweight(
                "bold"
            )

        else:

            label.set_color(
                "0.40"
            )


# ============================================================
# SHARED HEATMAP COLORBAR
# ============================================================

sm = ScalarMappable(
    norm=Normalize(
        vmin=0,
        vmax=1,
    ),
    cmap=cmap,
)

sm.set_array([])


# [left, bottom, width, height]
cax = fig.add_axes([
    0.92,
    0.30,
    0.012,
    0.40,
])


cbar = fig.colorbar(
    sm,
    cax=cax,
)


cbar.set_label(
    "Genotype frequency",
    fontsize=11,
)

cbar.ax.tick_params(
    labelsize=9
)


# ============================================================
# GLOBAL LAYOUT
# ============================================================

fig.subplots_adjust(
    left=0.10,
    right=0.90,
    bottom=0.07,
    top=0.96,
    hspace=0.20,
    wspace=0.18,
)


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    os.path.dirname(
        OUTPUT_FILE
    ),
    exist_ok=True,
)


fig.savefig(
    OUTPUT_FILE,
    dpi=600,
    bbox_inches="tight",
)

plt.close(fig)

print(
    f"\nSaved: {OUTPUT_FILE}"
)
