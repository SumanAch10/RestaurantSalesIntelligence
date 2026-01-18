# OpsPulse

OpsPulse is a FastAPI + PostgreSQL backend for ingesting restaurant/order data, running ETL + analytics (NumPy/Pandas), and exposing metrics/anomaly/forecast endpoints.

---

## Folder Structure

```text
opspulse/
├─ app/
│  ├─ main.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ logging.py
│  │  └─ security.py            # optional later
│  ├─ api/
│  │  ├─ v1/
│  │  │  ├─ router.py
│  │  │  └─ endpoints/
│  │  │     ├─ health.py
│  │  │     ├─ ingest.py
│  │  │     ├─ metrics.py
│  │  │     └─ runs.py
│  ├─ schemas/
│  │  ├─ ingest.py
│  │  ├─ metrics.py
│  │  └─ runs.py
│  ├─ db/
│  │  ├─ session.py
│  │  ├─ base.py
│  │  ├─ models/
│  │  │  ├─ order.py
│  │  │  ├─ item.py
│  │  │  ├─ order_item.py
│  │  │  ├─ inventory_snapshot.py
│  │  │  ├─ anomaly.py
│  │  │  └─ forecast.py
│  │  └─ repositories/
│  │     ├─ orders_repo.py
│  │     ├─ items_repo.py
│  │     ├─ inventory_repo.py
│  │     ├─ anomalies_repo.py
│  │     └─ forecasts_repo.py
│  ├─ services/
│  │  ├─ ingest_service.py
│  │  ├─ metrics_service.py
│  │  └─ runs_service.py
│  ├─ etl/
│  │  ├─ parsers.py              # file → DataFrame
│  │  ├─ cleaners.py             # clean_orders(df)
│  │  ├─ validators.py           # rules + error reports
│  │  └─ transformers.py         # df → normalized tables
│  ├─ analytics/
│  │  ├─ aggregations.py         # daily item sales, etc.
│  │  ├─ anomaly_detection.py    # z-score, rolling stats
│  │  └─ forecasting.py          # moving avg, exp smoothing
│  ├─ utils/
│  │  ├─ time.py
│  │  └─ dataframe.py
│  └─ tests/
│     ├─ test_cleaners.py
│     ├─ test_transformers.py
│     └─ test_analytics.py
├─ alembic/
├─ alembic.ini
├─ scripts/
│  ├─ seed_data.py
│  └─ generate_fake_orders.py
├─ docker-compose.yml
├─ Dockerfile
├─ requirements.txt (or pyproject.toml)
└─ README.md
