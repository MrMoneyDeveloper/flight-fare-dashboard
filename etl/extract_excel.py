#!/usr/bin/env python
"""
Extract-step:  Read the raw CSV/Excel, run basic profiling, and
write columnar *bronze* Parquet partitions under data/bronze/yyyy-mm/.
Usage:
    python etl/extract_excel.py --source data/raw/airlines_flights_data.csv
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa

# ---------------------------------------------------------------------------#
LOG_FMT = "%(asctime)s | %(levelname)-8s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FMT)
log = logging.getLogger("extract_excel")

# ---------------------------------------------------------------------------#
def read_source(file_path: Path) -> pd.DataFrame:
    """Load CSV or Excel with fallback retries."""
    for attempt in range(1, 4):
        try:
            log.info("Loading raw file (attempt %d): %s", attempt, file_path)
            if file_path.suffix.lower() in {".xls", ".xlsx"}:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            log.info("Loaded %d rows × %d cols", len(df), df.shape[1])
            return df
        except Exception as exc:
            log.exception("Failed on attempt %d: %s", attempt, exc)
    raise RuntimeError(f"Unable to load {file_path} after 3 attempts")


def write_parquet(df: pd.DataFrame, out_dir: Path) -> None:
    """Write partitioned Parquet (by load_date=YYYY-MM)."""
    load_date = datetime.now().strftime("%Y-%m")
    target_dir = out_dir / load_date
    target_dir.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df), target_dir / "flights_bronze.parquet")
    log.info("Wrote bronze Parquet to %s", target_dir)


# ---------------------------------------------------------------------------#
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True,
                        help="Path to raw airlines CSV/Excel file")
    parser.add_argument("--out_dir", type=Path, default=Path("data/bronze"),
                        help="Output folder for bronze Parquet")
    args = parser.parse_args()

    try:
        df = read_source(args.source)
        write_parquet(df, args.out_dir)
    except Exception as exc:
        log.exception("Extraction failed: %s", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
