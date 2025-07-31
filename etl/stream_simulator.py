#!/usr/bin/env python
"""
Stream-simulator:  Replay the gold Parquet as a JSON feed (stdout or TCP).
By default prints JSON lines to stdout at `--rate` rows per second.
You can pipe this into websockets, Redis, etc.
Usage:
    python etl/stream_simulator.py --gold data/gold/flights_gold_*.parquet --rate 5
"""
from __future__ import annotations
import argparse
import json
import logging
import random
import sys
import time
from glob import glob
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------#
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("stream_simulator")

# ---------------------------------------------------------------------------#
def pick_latest_gold(pattern: str) -> Path:
    files = sorted(glob(pattern))
    if not files:
        raise FileNotFoundError(f"No Parquet matches {pattern}")
    latest = Path(files[-1])
    log.info("Using gold file: %s", latest)
    return latest


def stream(df: pd.DataFrame, rate: float) -> None:
    """Emit one row every `1/rate` seconds (approx)."""
    delay = 1 / rate
    try:
        while True:
            row = df.sample(1).to_dict(orient="records")[0]
            sys.stdout.write(json.dumps(row) + "\n")
            sys.stdout.flush()
            time.sleep(delay)
    except KeyboardInterrupt:
        log.info("Stopped by user.")


# ---------------------------------------------------------------------------#
def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--gold", type=str, default="data/gold/flights_gold_*.parquet",
                   help="Glob pattern to gold Parquet files")
    p.add_argument("--rate", type=float, default=5,
                   help="Rows per second to emit")
    args = p.parse_args()

    try:
        gold_path = pick_latest_gold(args.gold)
        df = pd.read_parquet(gold_path)
        log.info("Streaming %d rows at %.2f rows/sec", len(df), args.rate)
        stream(df, args.rate)
    except Exception as exc:
        log.exception("Simulator failed: %s", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
