"""Transform cleaned line items into analytical table-shaped DataFrames."""

from __future__ import annotations

import pandas as pd


def _single_or_missing(values: pd.Series):
    distinct = values.dropna().astype("string").unique()
    return distinct[0] if len(distinct) == 1 else pd.NA


def transform_to_tables(clean: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Create orders, order_items, and items tables from cleaned line items."""
    required = {"order_key", "order_id", "order_time", "store_id", "item_sku",
                "qty", "unit_price", "line_total"}
    missing = sorted(required - set(clean.columns))
    if missing:
        raise ValueError(f"Cleaned data missing columns: {', '.join(missing)}")

    if clean.empty:
        return {
            "orders": pd.DataFrame(columns=["order_key", "order_id", "store_id", "order_time",
                                            "customer_id", "payment_method", "order_total"]),
            "order_items": pd.DataFrame(columns=["order_key", "item_sku", "qty", "unit_price",
                                                 "line_total"]),
            "items": pd.DataFrame(columns=["item_sku", "item_name", "category"]),
        }

    grouped = clean.groupby("order_key", sort=True, dropna=False)
    orders = grouped.agg(
        order_id=("order_id", "first"),
        store_id=("store_id", "first"),
        order_time=("order_time", "min"),
        order_total=("line_total", "sum"),
        customer_id=("customer_id", _single_or_missing),
        payment_method=("payment_method", _single_or_missing),
    ).reset_index()

    order_items = (
        clean.groupby(["order_key", "item_sku", "unit_price"], sort=True, dropna=False)
        .agg(qty=("qty", "sum"), line_total=("line_total", "sum"))
        .reset_index()
    )

    items = (
        clean.groupby("item_sku", sort=True, dropna=False)
        .agg(item_name=("item_name", "first"), category=("category", "first"))
        .reset_index()
    )
    return {"orders": orders, "order_items": order_items, "items": items}
