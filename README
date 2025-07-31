### **Re-scoped Blueprint — “Flight-Fare Intelligence Dashboard 2.0”**

*Keep the original “messy-to-insight” storyline, swap the relational DB for **columnar Parquet storage**, and layer in richer data-science touches (eight flavours of normalisation + eight distinct visualisations).*

---

## 1 | Architecture (Zero DB Server)

| Layer                      | Technology                                                                                      | Rationale                                                                              |
| -------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Extraction / Cleansing** | Python 3.12 · Pandas + Polars + Great Expectations                                              | Fast, memory-efficient wrangling; automated data-quality gates                         |
| **Storage**                | **Partitioned Parquet files** (Arrow format)                                                    | Column-ar, compressed, analytics-friendly; lives in Git repo / S3 without a running DB |
| **Query Engine**           | **DuckDB embedded** (single `.duckdb` file) exposed via ODBC → accessed from C# with **Dapper** | Gives us SQL + Dapper mapping **without** a server; DuckDB reads Parquet natively      |
| **API**                    | .NET 8 Minimal API + Dapper • SignalR for live stream                                           | Thin, strongly-typed endpoints; WebSocket push for “live” feed                         |
| **Front-End**              | Vanilla HTML • Tailwind CSS • HTMX + Chart.js                                                   | Instant responsive UI, no heavy SPA framework                                          |

> **Why this still counts as “no DB”?** DuckDB is an embedded analytics engine that simply maps SQL onto the Parquet files on disk—there’s no server to install or manage.

---

## 2 | Eight Normalisation/Transformation Techniques

| #     | Category                      | Flight-column Example                                      | Purpose                                            |
| ----- | ----------------------------- | ---------------------------------------------------------- | -------------------------------------------------- |
| **1** | **Categorical harmonisation** | `stops → {0,1,2}`                                          | Removes free-text drift (“zero”, “non-stop”, etc.) |
| **2** | **Time-bucket encoding**      | `departure_time → {Early Morning, Morning…}` ⟶ ordinal 0-5 | Feeds ML models numeric chrono order               |
| **3** | **Duration unwrap**           | `"2.17"` h ⟶ `130` minutes                                 | Consistent numeric metric                          |
| **4** | **Z-score scaling**           | `price_z = (price – µ) / σ`                                | Detect over/under-priced outliers                  |
| **5** | **Min-max scaling**           | `days_left` 0-365 ⟶ 0-1                                    | Feature range for UI sliders                       |
| **6** | **Frequency encoding**        | `airline_freq` = share of flights                          | Captures carrier popularity                        |
| **7** | **One-hot vectors**           | `class ∈ {Economy, Business}`                              | Keeps class bias explicit                          |
| **8** | **Log-transform**             | `log_price = ln(price)`                                    | Normalises right-skewed fare tail                  |

Each transformation lives in `etl/transform.py` with unit‐tests (`pytest`) and Great Expectations checks.

---

## 3 | Eight Visual Styles Showcased in the Dashboard

| #     | Component                                                                   | Insight Conveyed                 |
| ----- | --------------------------------------------------------------------------- | -------------------------------- |
| **1** | **Line chart** (Chart.js) – Median price vs. `days_left`                    | Price-decay curve                |
| **2** | **Box-and-whisker** – Fare distribution per airline                         | Detect carrier outliers          |
| **3** | **Heat-map calendar** – Avg. price by departure weekday & month             | Seasonality hotspots             |
| **4** | **Stacked area** – Class mix share over time                                | Economy vs. Business trends      |
| **5** | **Violin plot** – Flight **duration** by `stops` count                      | Time cost of layovers            |
| **6** | **Bullet KPI cards** – Data-quality score, null-rate, row latency           | Health at a glance               |
| **7** | **Radar chart** – Z-scored metrics (price, duration, days\_left) by airline | Multi-metric carrier ranking     |
| **8** | **Live ticker table** (HTMX stream) – Last 20 price updates                 | “Bloomberg”-style real-time feed |

All charts share the Tailwind theme but differ in form, emphasising your versatility with data storytelling.

---

## 4 | 7-Day Sprint Plan (updated)

| Day   | Deliverables                                                                                | Key Analyst/Engineer Focus |
| ----- | ------------------------------------------------------------------------------------------- | -------------------------- |
| **1** | Jupyter EDA of raw Excel → identify anomalies                                               | Problem framing            |
| **2** | Build **`extract_excel.py`** → convert to partitioned Parquet (`/data/YYYY-MM/…`)           | Efficient columnar storage |
| **3** | Implement **8 transformations** + tests; generate Great Expectations docs                   | Reproducible cleansing     |
| **4** | Spin up DuckDB; wire Dapper queries (`flights_latest`, `price_hist`)                        | Embedded SQL access        |
| **5** | Create Minimal API endpoints + SignalR hub; fake live feed via `python stream_simulator.py` | Real-time backend          |
| **6** | Tailwind dashboard with **8 visual widgets**; HTMX filters                                  | Interactive UX             |
| **7** | Docker Compose (Python + API + Nginx); GitHub CI; 90-sec demo video                         | Dev-ops polish             |

---

## 5 | Repository Skeleton

```
flight-fare-dashboard/
├─ data/
│  └─ (Parquet partitions)
├─ etl/
│  ├─ extract_excel.py
│  ├─ transform.py
│  ├─ stream_simulator.py
│  └─ tests/
├─ api/
│  ├─ Program.cs          # .NET 8 + SignalR
│  ├─ Repositories/       # Dapper <-> DuckDB ODBC
│  └─ Models/
├─ ui/
│  ├─ index.html
│  ├─ tailwind.css
│  └─ js/
├─ docker-compose.yml
└─ README.md
```

---

## 6 | Interview Sound-Bites

* **“No server, still SQL.”** - DuckDB queries Parquet in-process; Dapper maps straight into C# DTOs—easy to demo locally or in CI.
* **“Eight-layer normalisation.”** - I showcase categorical, numerical, and statistical techniques, each backed by tests and Great Expectations validation.
* **“Visual buffet.”** - From box-plots to live tickers, the UI proves I can pick the right chart for the story—not just default line graphs.
* **“One-command spin-up.”** - `docker compose up` builds ETL, API, and Tailwind-served UI in \~90 s.

---

### **Elevator Pitch (final form)**

> “I take a messy Excel flight-fare dump, enforce eight rigorous normalisation steps, store it as efficient Parquet, query it with embedded DuckDB + Dapper (no external DB), and present eight distinct visual perspectives—all containerised, tested, and ready for a hiring manager to explore in one click.”

Use this plan as your project README outline, then iterate feature-by-feature; the result is a **compact yet sophisticated** showcase of both analysis depth and engineering practicality.
