from pathlib import Path

content = """# OpsPulse — Project Flow (Data → Analytics → API → DB → Deploy)

A restaurant sales + inventory intelligence system that turns messy order data into clean tables, reliable metrics, anomaly alerts, and simple demand forecasts.

---

## 0) North Star

**What you’re building**
- A repeatable **data pipeline** (Pandas) + **analytics engine** (NumPy/Pandas)
- Backed by **PostgreSQL**
- Served by **FastAPI**
- Shippable via **Docker** (and deployable to a cloud VM / Render / Fly.io / Railway)

**Core loop**
Raw files → Clean + Validate → Normalize tables → Store → Metrics/Insights → (later) UI/BI

---

## 1) Data Assumptions

### Row meaning
- One row in the raw dataset = **one line item** on an order (order_id repeats across items)

### Typical columns (example)
- order_id, order_time, store_id, customer_id, payment_method
- item_sku, item_name, category
- qty, unit_price

---

## 2) Feature Checklist (Full Scope)

### A) Data Engine (Pandas-first)
1. **Load raw files** (CSV now; Excel later if needed)
2. **Data audit report**
   - row count, duplicates, missing values, invalid dates, invalid qty/price, unique orders/items
3. **Cleaning + Validation**
   - parse datetime
   - qty → int (reject <= 0 for “sales” pipeline)
   - unit_price → float (parse USD/$)
   - strip whitespace, normalize categories/payment methods
   - quarantine invalid rows with reasons
4. **Feature engineering**
   - date, hour, day_of_week, is_weekend
   - line_total = qty * unit_price

### B) Normalization (Relational tables)
Convert one raw line-item dataframe into:
- **orders** (one row per order_id)
- **order_items** (line items)
- **items** (catalog)
- (optional) **customers** (if meaningful)

### C) Analytics Engine (NumPy + Pandas)
1. **Metrics**
   - revenue by day/week/month
   - top items by qty and by revenue
   - average order value (AOV)
   - peak hours (hourly distribution)
2. **Anomaly Detection (NumPy)**
   - daily qty per item
   - z-score or rolling z-score
   - store anomalies (date, item, score, reason)
3. **Forecasting (NumPy)**
   - moving average / exponential smoothing
   - predict next N days demand per item
4. **Restock suggestions**
   - compare predicted demand vs inventory snapshot (later)

### D) Database (PostgreSQL)
- Store normalized tables + runs (anomaly/forecast) + results
- Enable analytics endpoints to query reliably

### E) API (FastAPI)
1. **Ingest endpoints**
2. **Metrics endpoints**
3. **Run endpoints** (anomaly/forecast)
4. **Health endpoint**
5. Pagination for list endpoints

### F) Deployment
- Dockerize API + DB
- Migrations with Alembic
- Production configuration (env vars)
- Basic logging/monitoring

---

## 3) Build Order (Recommended)

### Phase 1 — Data Engine Only (You are here)
Goal: load → clean → report → export clean tables locally (CSV/parquet)

Deliverables:
- `clean_orders(df)` returns:
  - cleaned_df
  - rejects_df (bad rows)
  - report dict (counts + reasons)
- `transform_to_tables(cleaned_df)` returns:
  - orders_df
  - order_items_df
  - items_df
- `aggregate_metrics(...)` outputs daily revenue, top items, etc.

### Phase 2 — Add NumPy Intelligence
Goal: anomaly + forecast runs using aggregated series

Deliverables:
- `detect_anomalies(daily_item_qty)` → anomalies_df
- `forecast_demand(daily_item_qty, method, horizon)` → forecast_df

### Phase 3 — Database Integration
Goal: store outputs in Postgres, read back for metrics

Deliverables:
- SQLAlchemy models + Alembic migrations
- bulk inserts for normalized tables
- stored anomalies/forecasts

### Phase 4 — API Layer (FastAPI)
Goal: endpoints to ingest, compute, query

Deliverables:
- `/health`
- `/ingest/orders`
- `/metrics/revenue`
- `/metrics/top-items`
- `/run/anomaly-detection`
- `/run/forecast`
- `/recommend/restock` (optional)

### Phase 5 — Deployment
Goal: containerized app you can run anywhere

Deliverables:
- Dockerfile + docker-compose.yml
- env-based config
- deploy to a platform

---

## 4) Minimal Folder Structure (Grow-as-you-go)

Start small, refactor when files get big:

### Stage 0 (Data-first)

opspulse/
data_engine/
init.py
sample_data.py
cleaners.py
transformers.py
aggregations.py
analytics.py

Always show details


### Stage 1 (After it grows)

opspulse/
app/
etl/
parsers.py
cleaners.py
transformers.py
analytics/
aggregations.py
anomaly_detection.py
forecasting.py

Always show details


### Stage 2 (Add DB + API)

opspulse/
app/
api/
health.py
ingest.py
metrics.py
runs.py
db/
session.py
models/
repositories/
services/

Always show details

---

## 5) Data Cleaning Contract (Rules)

### Required for “sales pipeline”
- order_id not null
- item_sku not null
- order_time parseable datetime
- qty is integer >= 1
- unit_price is float > 0

### Optional handling
- missing category → fill with \"Unknown\"
- missing customer_id → allow but track rate
- duplicates → remove using a line-item key

### Suggested line-item dedupe key
- `order_id + item_sku + order_time (+ unit_price + qty)`
(Choose based on your data reality.)

### Output expectation
- cleaned_df has correct dtypes and added columns:
  - `date`, `hour`, `line_total`

---

## 6) NumPy Components (What to implement)

### A) Rolling z-score anomaly detection
- Build daily series per item (qty sold)
- Compute rolling mean/std (window=7 or 14)
- z = (x - rolling_mean) / rolling_std
- flag abs(z) > threshold (e.g., 3)

### B) Forecasting baselines
- Moving average: mean of last 7 days
- Exponential smoothing: y_hat[t] = alpha*x[t] + (1-alpha)*y_hat[t-1]
- Output horizon N days per item

---

## 7) PostgreSQL Schema (Starter)

### Tables
- `items(id, sku, name, category)`
- `orders(id, order_id, order_time, store_id, customer_id, payment_method, order_total)`
- `order_items(id, order_id_fk, item_id_fk, qty, unit_price, line_total)`
- `anomaly_runs(id, run_time, method, window, threshold)`
- `anomalies(id, run_id_fk, item_id_fk, date, z_score, reason)`
- `forecast_runs(id, run_time, method, horizon, params)`
- `item_forecasts(id, run_id_fk, item_id_fk, date, predicted_qty)`
- (optional) `inventory_snapshots(id, snapshot_time, item_id_fk, on_hand)`

---

## 8) API Endpoints (Later)

### Ingestion
- `POST /ingest/orders` (upload CSV)
- `POST /ingest/inventory` (optional)

### Metrics
- `GET /metrics/revenue?start=&end=&granularity=day|week`
- `GET /metrics/top-items?start=&end=&k=10`
- `GET /metrics/peak-hours?start=&end=`

### Runs
- `POST /run/anomaly-detection?start=&end=&window=14&threshold=3`
- `POST /run/forecast?horizon=7&method=moving_average`

### Health
- `GET /health`

---

## 9) Deployment Plan

### Local (dev)
- `docker-compose.yml`: Postgres + API
- Alembic migrations at startup (manual command is safer first)

### Production (simple)
- Deploy Docker image to a VM
- Configure:
  - DATABASE_URL
  - APP_ENV=prod
  - log level
- Use a reverse proxy (Nginx) if needed

---

## 10) Quality Bar (What makes it “pro”)

### Data quality tracking
- Always return/store:
  - counts of rejected rows
  - reasons breakdown

### Tests (small but powerful)
- parsing unit_price formats
- qty conversion + filtering
- datetime parsing with bad strings
- anomaly detection on a tiny known series

### Documentation
- README: how to run, sample requests, schema overview

---

## 11) Current Next Steps (Your exact move)

1. Load raw CSV
2. Print a **data audit**: shape, dtypes, missing, duplicates
3. Implement `clean_orders(df)`:
   - parse time, qty, price
   - filter qty > 0 for sales pipeline
   - produce rejects + report
4. Add engineered columns: date/hour/line_total
5. Build first metric: daily revenue (groupby date)

Once you have daily revenue, we plug in NumPy anomalies and forecasts cleanly.
"""
Path("/mnt/data/project_flow.md").write_text(content, encoding="utf-8")
"/mnt/data/project_flow.md