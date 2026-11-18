# OpsPulse

OpsPulse is a restaurant sales and operations analytics prototype. It turns order line-item CSVs into validated, clean data, normalized tables, and business-facing sales metrics. The goal is to grow this data engine into a SQL-backed API with demand forecasting and anomaly alerts.

## Current milestone: local data engine

The first milestone is deliberately data-first. It currently:

- validates required order fields and quarantines bad rows with reasons;
- preserves the raw input and reports exact duplicate candidates rather than silently deleting them;
- creates order, order-item, and item tables;
- calculates gross sales, average order value, daily sales, top items, and sales by hour;
- writes a JSON quality/summary report plus CSV outputs.

Forecasting, anomaly alerts, PostgreSQL persistence, API endpoints, and deployment are future milestones. The current demo data is synthetic and must not be presented as real restaurant operating data.

## Run locally

Python 3.10+ is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/generate_demo_data.py
python -m opspulse.data_engine data/demo_orders.csv --output runs/demo
```

Outputs are written under `runs/demo/`: `clean_orders.csv`, `rejected_rows.csv`, normalized `orders.csv`, `order_items.csv`, `items.csv`, metric tables, and `report.json`.

## Input contract

One CSV row represents one order line item. Required columns:

| Column | Meaning |
|---|---|
| `order_id` | Source order identifier |
| `order_time` | Parseable order timestamp |
| `item_sku` | Stable item identifier |
| `qty` | Positive whole-unit quantity |
| `unit_price` | Positive price per unit; plain numbers or values such as `$4.50` |

Optional columns: `store_id`, `customer_id`, `payment_method`, `item_name`, and `category`. When absent, store is set to `default`; item name falls back to SKU; category and payment method are set to `Unknown`. Customer IDs can be missing.

## What the numbers mean

Gross sales are the sum of quantity times unit price; they do not subtract tax, discounts, refunds, or fees because those fields are not in the input contract. Average order value is computed after combining line items by store and order ID. Metrics describe only the rows accepted by validation. Rejected rows are exported separately for inspection.

## Roadmap

1. **Data engine:** clean and validate order files, normalize tables, and produce transparent quality reports and sales metrics.
2. **Analytics:** define calendar completeness and operating hours, then add evaluated demand forecasts and anomaly detection.
3. **Storage and API:** persist validated data and analytic runs in PostgreSQL and expose them through FastAPI.
4. **Decision layer:** add inventory-aware restock suggestions only when inventory and lead-time data are available.
5. **Deployment:** containerize and deploy after local behavior and data semantics are verified.
