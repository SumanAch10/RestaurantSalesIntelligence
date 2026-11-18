"""Pure, non-destructive cleaning for restaurant order line-item data."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = ("order_id", "order_time", "item_sku", "qty", "unit_price")
OPTIONAL_COLUMNS = ("store_id", "customer_id", "payment_method", "item_name", "category")


def _clean_text(series: pd.Series) -> pd.Series:
    value = series.astype("string").str.strip()
    return value.mask(value.eq(""))


def clean_orders(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Return (clean rows, rejected rows, quality report) without changing raw.

    Required input columns are order_id, order_time, item_sku, qty, and
    unit_price. Invalid records are quarantined with explicit reject reasons.
    Exact duplicate rows are reported for review and preserved; without a
    source line-item ID, silently deleting them could discard legitimate sales.
    """
    if not isinstance(raw, pd.DataFrame):
        raise TypeError("raw must be a pandas DataFrame")

    missing = sorted(set(REQUIRED_COLUMNS) - set(raw.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    frame = raw.copy(deep=True).reset_index(drop=True)
    frame.insert(0, "source_row_number", range(2, len(frame) + 2))

    for column in OPTIONAL_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA

    for column in ("order_id", "item_sku", "store_id", "customer_id",
                   "payment_method", "item_name", "category"):
        frame[column] = _clean_text(frame[column])

    frame["order_time"] = pd.to_datetime(frame["order_time"], errors="coerce")
    frame["qty"] = pd.to_numeric(frame["qty"], errors="coerce")
    price_text = (
        frame["unit_price"].astype("string").str.strip()
        .str.replace("$", "", regex=False).str.replace(",", "", regex=False)
    )
    frame["unit_price"] = pd.to_numeric(price_text, errors="coerce")

    reasons: list[list[str]] = [[] for _ in range(len(frame))]
    checks = [
        ("order_id", frame["order_id"].isna(), "missing_order_id"),
        ("item_sku", frame["item_sku"].isna(), "missing_item_sku"),
        ("order_time", frame["order_time"].isna(), "invalid_order_time"),
        ("qty", frame["qty"].isna() | frame["qty"].le(0) | frame["qty"].mod(1).ne(0),
         "invalid_quantity"),
        ("unit_price", frame["unit_price"].isna() | frame["unit_price"].le(0),
         "invalid_unit_price"),
    ]
    for _, invalid, reason in checks:
        for position in invalid[invalid].index:
            reasons[position].append(reason)

    frame["reject_reason"] = [";".join(row) for row in reasons]
    rejected = frame.loc[frame["reject_reason"].ne("")].copy()
    clean = frame.loc[frame["reject_reason"].eq("")].drop(columns="reject_reason").copy()

    clean["store_id"] = clean["store_id"].fillna("default")
    clean["item_name"] = clean["item_name"].fillna(clean["item_sku"])
    clean["category"] = clean["category"].fillna("Unknown")
    clean["payment_method"] = clean["payment_method"].fillna("Unknown")
    clean["order_key"] = clean["store_id"].astype("string") + "-" + clean["order_id"].astype("string")
    clean["line_total"] = clean["qty"] * clean["unit_price"]
    clean["order_date"] = clean["order_time"].dt.strftime("%Y-%m-%d")
    clean["order_hour"] = clean["order_time"].dt.hour.astype("int64")
    clean["day_of_week"] = clean["order_time"].dt.day_name()

    duplicate_candidates = int(clean.duplicated(subset=list(raw.columns), keep="first").sum())
    report = {
        "input_rows": int(len(raw)),
        "accepted_rows": int(len(clean)),
        "rejected_rows": int(len(rejected)),
        "exact_duplicate_candidates_preserved": duplicate_candidates,
        "reject_reason_counts": {
            reason: int(sum(reason in item for item in reasons))
            for reason in ("missing_order_id", "missing_item_sku", "invalid_order_time",
                           "invalid_quantity", "invalid_unit_price")
            if any(reason in item for item in reasons)
        },
        "accepted_orders": int(clean["order_key"].nunique()),
        "accepted_items": int(clean["item_sku"].nunique()),
        "missing_customer_id_rows": int(clean["customer_id"].isna().sum()),
    }
    return clean, rejected, report
