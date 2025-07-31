#!/usr/bin/env python
"""
Transform-step: Read bronze Parquet, apply 8 normalisations, validate with
Great Expectations-style checks, and write *gold* Parquet.
Usage:
    python etl/transform.py --in_dir data/bronze --out_dir data/gold
"""
from __future__ import annotations
import argparse
import logging
from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import pyarrow as pa

# ---------------------------------------------------------------------------#
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("transform")

# ---------------------------------------------------------------------------#
def load_bronze(in_dir: Path) -> pd.DataFrame:
    latest_month = sorted(in_dir.iterdir())[-1]  # pick latest partition
    path = latest_month / "flights_bronze.parquet"
    log.info("Reading bronze data: %s", path)
    return pq.read_table(path).to_pandas()


# ---------------------------------------------------------------------------#
def normalise(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the 8 transformations described in the blueprint."""
    # 1. stops → numeric
    df["stops_n"] = df["stops"].str.extract(r"(\d+)").fillna(0).astype(int)

    # 2. departure_time ordinal bucket
    order = ["Early_Morning", "Morning", "Afternoon", "Evening", "Night", "Late_Night"]
    df["dep_bucket"] = pd.Categorical(df["departure_time"], categories=order).codes

    # 3. duration to minutes (assumes '2.17' ≈ 2h10m)
    df["duration_mins"] = (df["duration"].astype(float) * 60).round().astype(int)

    # 4. price z-score
    df["price_z"] = (df["price"] - df["price"].mean()) / df["price"].std(ddof=0)

    # 5. days_left min-max 0–1
    d_min, d_max = df["days_left"].min(), df["days_left"].max()
    df["days_left_scaled"] = (df["days_left"] - d_min) / (d_max - d_min)

    # 6. airline frequency encoding
    freq = df["airline"].value_counts(normalize=True)
    df["airline_freq"] = df["airline"].map(freq)

    # 7. class one-hot (Economy/Business)
    df = pd.get_dummies(df, columns=["class"], prefix="cls")

    # 8. log-price
    df["log_price"] = np.log(df["price"])

    log.info("Applied all transformations.")
    return df


def quality_gate(df: pd.DataFrame) -> None:
    """Abort if more than 5 % nulls appear after transform."""
    null_rate = df.isna().mean().mean()
    if null_rate > 0.05:
        raise ValueError(f"Null-rate {null_rate:.2%} exceeds 5 % threshold")
    log.info("Null-rate %.2f%% within threshold", null_rate * 100)


def write_gold(df: pd.DataFrame, out_dir: Path) -> None:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    out_file = out_dir / f"flights_gold_{ts}.parquet"
    out_dir.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df), out_file)
    log.info("Wrote gold Parquet: %s", out_file)


# ---------------------------------------------------------------------------#
def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argu_
