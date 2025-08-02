# Flight-Fare Intelligence Dashboard

This demo project turns a raw airline fare CSV into a set of interactive charts. Python scripts clean and normalise the data into Parquet, a .NET Minimal API exposes queries over DuckDB, and a small HTMX/Tailwind front-end renders the dashboard.

## Quick start

You can run everything individually or let the helper script handle it all.
The script now launches the API and static web server directly on your
machine – no Docker required.

```bash
# Start API and dashboard together
./run_all.sh

# Or run components independently
./run_all.sh --api-only   # only the API
./run_all.sh --ui-only    # only the front-end
```

Use `--no-api` or `--no-ui` to skip starting a component while running the other.

Run the following commands from the repo root to generate data and launch the dashboard manually.

```bash
# 1. Python dependencies
pip install -r requirements.txt

# 2. Extract & transform the sample data
python etl/extract_excel.py --source data/raw/airlines_flights_data.csv
python etl/transform.py

# 3. Build Tailwind CSS for the UI
cd ui
npm install
npx tailwindcss -o public/tailwind.css --minify
cd ..

# 4. Start API and dashboard locally
#    (requires the .NET 8 SDK and Python 3 installed)
dotnet run --project api --urls http://localhost:8000 &
python -m http.server 8080 --directory ui

# (Optional) emit a live JSON feed
python etl/stream_simulator.py --gold data/gold/flights_gold_*.parquet
```

The API listens on `http://localhost:8000` and the dashboard is served at `http://localhost:8080`.

## Architecture overview

| Layer            | Technology                              | Purpose                                      |
| ---------------- | --------------------------------------- | -------------------------------------------- |
| Extraction       | Python · Pandas/Polars                  | Load and validate the raw CSV/Excel          |
| Storage          | Parquet partitions                      | Compressed, analytics-friendly files         |
| Query engine     | DuckDB embedded + Dapper                | SQL access without a running database server |
| API              | .NET 8 Minimal API + SignalR            | REST endpoints and optional live feed        |
| Front-end        | Tailwind CSS · HTMX · Chart.js          | Lightweight interactive dashboard            |

The transformation step applies eight normalisation techniques (bucketed times, z-scores, one-hot encoding, etc.). The dashboard showcases various chart types including line, box/whisker and heat maps.

---

Original blueprint details can be found in [`README.md.bak`](README.md.bak).
