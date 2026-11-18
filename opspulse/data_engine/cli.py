"""Command-line entry point for the first OpsPulse data-engine milestone."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .aggregations import calculate_metrics
from .cleaners import clean_orders
from .transformers import transform_to_tables


def run(input_csv: Path, output_dir: Path) -> dict:
    raw = pd.read_csv(input_csv)
    clean, rejected, quality = clean_orders(raw)
    tables = transform_to_tables(clean)
    metrics = calculate_metrics(clean)

    output_dir.mkdir(parents=True, exist_ok=True)
    clean.to_csv(output_dir / "clean_orders.csv", index=False)
    rejected.to_csv(output_dir / "rejected_rows.csv", index=False)
    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)
    for name in ("daily_sales", "top_items", "peak_hours"):
        metrics[name].to_csv(output_dir / f"{name}.csv", index=False)

    report = {"data_quality": quality, "sales_summary": metrics["summary"]}
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean restaurant order data and calculate sales metrics.")
    parser.add_argument("input_csv", type=Path, help="CSV containing order line items")
    parser.add_argument("--output", type=Path, default=Path("runs/latest"),
                        help="Directory for cleaned data and reports (default: runs/latest)")
    args = parser.parse_args()

    report = run(args.input_csv, args.output)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
