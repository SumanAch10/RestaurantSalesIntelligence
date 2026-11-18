"""Business-facing sales metrics from cleaned order data."""

from __future__ import annotations

import pandas as pd


def calculate_metrics(clean: pd.DataFrame) -> dict:
    """Calculate core metrics and return both summary values and detail tables."""
    required = {"order_key", "order_time", "order_date", "order_hour",
                "item_sku", "item_name", "qty", "line_total"}
    missing = sorted(required - set(clean.columns))
    if missing:
        raise ValueError(f"Cleaned data missing columns: {', '.join(missing)}")

    if clean.empty:
        return {
            "summary": {
                "orders": 0, "units_sold": 0, "gross_sales": 0.0,
                "average_order_value": 0.0, "date_start": None, "date_end": None,
            },
            "daily_sales": pd.DataFrame(columns=["order_date", "orders", "units_sold", "gross_sales"]),
            "top_items": pd.DataFrame(columns=["item_sku", "item_name", "units_sold", "gross_sales"]),
            "peak_hours": pd.DataFrame(columns=["order_hour", "orders", "gross_sales"]),
        }

    order_totals = clean.groupby("order_key", sort=False)["line_total"].sum()
    daily_sales = (
        clean.groupby("order_date", sort=True)
        .agg(orders=("order_key", "nunique"), units_sold=("qty", "sum"),
             gross_sales=("line_total", "sum"))
        .reset_index()
    )
    top_items = (
        clean.groupby(["item_sku", "item_name"], sort=True)
        .agg(units_sold=("qty", "sum"), gross_sales=("line_total", "sum"))
        .sort_values(["units_sold", "gross_sales"], ascending=False)
        .reset_index()
    )
    peak_hours = (
        clean.groupby("order_hour", sort=True)
        .agg(orders=("order_key", "nunique"), gross_sales=("line_total", "sum"))
        .reset_index()
    )

    summary = {
        "orders": int(clean["order_key"].nunique()),
        "units_sold": int(clean["qty"].sum()),
        "gross_sales": round(float(clean["line_total"].sum()), 2),
        "average_order_value": round(float(order_totals.mean()), 2),
        "date_start": str(clean["order_date"].min()),
        "date_end": str(clean["order_date"].max()),
    }
    return {"summary": summary, "daily_sales": daily_sales,
            "top_items": top_items, "peak_hours": peak_hours}
