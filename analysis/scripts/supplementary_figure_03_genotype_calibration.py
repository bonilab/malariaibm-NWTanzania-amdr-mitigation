"""Generate Supplementary Figure 3 from calibration genotype databases."""

from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "analysis" / "data" / "raw" / "supplementary_figure_03"
REFERENCE_FILE = ROOT / "analysis" / "data" / "raw" / "shared" / "ref_genotype_data.csv"
OUTPUT_FILE = ROOT / "figures" / "supplementary" / "supplementary-figure-03.png"
SUMMARY_FILE = ROOT / "analysis" / "results" / "supplementary_figure_03_2023_genotype_frequencies.csv"
N_RUNS = 15
REGION_NAMES = {1: "Kigoma", 2: "Kagera", 3: "Mwanza", 4: "Geita"}

PALETTE = {
    "pf_mdr1_86Y": "green",
    "pf_mdr1_184F": "blue",
    "pf_crt_76T": "red",
    "pf_k13_561H": "black",
}
GENOTYPE_LABELS = {
    "pf_mdr1_86Y": "pfmdr1 86Y",
    "pf_mdr1_184F": "pfmdr1 184F",
    "pf_crt_76T": "pfcrt 76T",
    "pf_k13_561H": "pfkelch 561H",
}


def load_run(db_path: Path, run: int, region_names: dict[int, str]) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        genome = pd.read_sql_query("SELECT * FROM monthlygenomedata", conn)
        sites = pd.read_sql_query(
            "SELECT monthlydataid, locationid, infectedindividuals FROM monthlysitedata", conn
        )
        months = pd.read_sql_query("SELECT id, modeltime FROM monthlydata", conn)
        genotype_names = pd.read_sql_query("SELECT id, name FROM genotype", conn)

    merged = genome.merge(sites, on=["monthlydataid", "locationid"], how="left")
    merged = merged.merge(months[["id", "modeltime"]], left_on="monthlydataid", right_on="id", how="left")
    denominator = merged["infectedindividuals"].to_numpy(dtype=float)
    numerator = merged["weightedoccurrences"].to_numpy(dtype=float)
    merged["genotype_frequency"] = np.divide(
        numerator, denominator, out=np.zeros_like(numerator), where=denominator > 0
    )
    merged["datetime"] = pd.to_datetime(merged["modeltime"], unit="s").dt.date
    merged = merged.merge(genotype_names, left_on="genomeid", right_on="id", suffixes=("", "_genotype"))
    merged["location_name"] = merged["locationid"].map(region_names)
    if merged["location_name"].isna().any():
        unknown = sorted(merged.loc[merged["location_name"].isna(), "locationid"].unique())
        raise ValueError(f"{db_path.name} contains unmapped location IDs: {unknown}")

    # Add zeros for genotype/location/month combinations absent from the sparse database table.
    dates = merged["datetime"].drop_duplicates()
    locations = merged["locationid"].drop_duplicates()
    genotypes = genotype_names["name"].drop_duplicates()
    complete = pd.MultiIndex.from_product(
        [dates, locations, genotypes], names=["datetime", "locationid", "genotype"]
    ).to_frame(index=False)
    frequencies = merged[["datetime", "locationid", "name", "genotype_frequency"]].rename(
        columns={"name": "genotype"}
    )
    complete = complete.merge(frequencies, on=["datetime", "locationid", "genotype"], how="left")
    complete["genotype_frequency"] = complete["genotype_frequency"].fillna(0)
    complete["location_name"] = complete["locationid"].map(region_names)
    complete["run"] = run
    return complete


def extract_plot_data(all_data: pd.DataFrame) -> pd.DataFrame:
    definitions = {
        "pf_k13_561H": all_data["genotype"].str[-2].eq("H"),
        "pf_mdr1_86Y": all_data["genotype"].str[1].eq("Y"),
        "pf_mdr1_184F": all_data["genotype"].str[2].eq("F"),
        "pf_crt_76T": all_data["genotype"].str[0].eq("T"),
    }
    pieces = []
    for name, mask in definitions.items():
        group = all_data.loc[mask].groupby(
            ["datetime", "locationid", "location_name", "run"], as_index=False
        )["genotype_frequency"].sum()
        group["genotype"] = name
        pieces.append(group)
    return pd.concat(pieces, ignore_index=True)


def main() -> None:
    if not REFERENCE_FILE.exists():
        raise FileNotFoundError(f"Missing reference genotype data: {REFERENCE_FILE}")
    reference = pd.read_csv(REFERENCE_FILE)
    required_reference = {"region", "date", "gene", "frequency"}
    missing = required_reference - set(reference.columns)
    if missing:
        raise ValueError(f"{REFERENCE_FILE} is missing columns: {', '.join(sorted(missing))}")

    database_paths = [DATA_DIR / f"monthly_data_{run}.db" for run in range(N_RUNS)]
    missing_dbs = [path for path in database_paths if not path.exists()]
    if missing_dbs:
        raise FileNotFoundError("Missing run databases:\n" + "\n".join(f"  - {p}" for p in missing_dbs))

    all_data = pd.concat(
        [load_run(path, run, REGION_NAMES) for run, path in enumerate(database_paths)],
        ignore_index=True,
    )
    plot_data = extract_plot_data(all_data)
    reference["date"] = pd.to_datetime(reference["date"]).dt.date

    sns.set_context("paper")
    grid = sns.relplot(
        data=plot_data,
        x="datetime",
        y="genotype_frequency",
        hue="genotype",
        hue_order=list(PALETTE),
        col="location_name",
        col_order=sorted(REGION_NAMES.values()),
        col_wrap=2,
        kind="line",
        height=5,
        aspect=2,
        facet_kws={"sharex": True, "sharey": True},
        palette=PALETTE,
        legend=True,
        errorbar=("pi", 90),
    )
    grid.set_titles("{col_name}")
    grid.set_axis_labels("Year", "Genotype Frequency")
    grid.set(ylim=(0, 1), xlim=(pd.Timestamp("2003-01-01").date(), pd.Timestamp("2023-01-01").date()))
    grid._legend.set_title("Genotype")
    for text, name in zip(grid._legend.texts, list(PALETTE)):
        text.set_text(GENOTYPE_LABELS[name])

    for region, ax in grid.axes_dict.items():
        region_reference = reference.loc[reference["region"] == region]
        sns.scatterplot(
            data=region_reference,
            x="date",
            y="frequency",
            hue="gene",
            hue_order=list(PALETTE),
            ax=ax,
            legend=False,
            s=100,
            palette=PALETTE,
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    grid.figure.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    plt.close(grid.figure)

    at_2023 = plot_data.loc[plot_data["datetime"] == pd.Timestamp("2023-01-01").date()]
    summary = (
        at_2023.groupby(["genotype", "location_name"], as_index=False)["genotype_frequency"]
        .mean()
        .sort_values(["genotype", "location_name"])
    )
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_FILE, index=False)
    print(f"Saved {OUTPUT_FILE}")
    print(f"Saved {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
