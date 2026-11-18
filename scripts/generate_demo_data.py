"""Generate explicitly synthetic restaurant line-item data for local demos."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate(path: Path, days: int = 30, seed: int = 42) -> None:
    rng = random.Random(seed)
    products = [
        ("DRK-01", "Iced Coffee", "Drinks", 4.50, 24),
        ("FD-01", "Veggie Bowl", "Mains", 12.00, 18),
        ("FD-02", "Chicken Wrap", "Mains", 10.50, 22),
        ("DS-01", "Chocolate Cookie", "Dessert", 3.25, 14),
    ]
    start = datetime(2026, 1, 1, 10, 0)
    rows = []
    order_number = 1
    for day in range(days):
        date = start + timedelta(days=day)
        for _ in range(rng.randint(12, 25)):
            order_time = date.replace(hour=rng.randint(10, 21), minute=rng.randint(0, 59))
            store_id = "store-001"
            order_id = f"{date:%Y%m%d}-{order_number:05d}"
            order_number += 1
            for sku, name, category, price, daily_mean in products:
                probability = min(0.8, daily_mean / 100)
                if rng.random() < probability:
                    rows.append({
                        "order_id": order_id,
                        "order_time": order_time.isoformat(sep=" "),
                        "store_id": store_id,
                        "customer_id": f"customer-{rng.randint(1, 200):03d}",
                        "payment_method": rng.choice(["card", "cash", "mobile"]),
                        "item_sku": sku,
                        "item_name": name,
                        "category": category,
                        "qty": rng.choice([1, 1, 1, 2]),
                        "unit_price": f"{price:.2f}",
                    })
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/demo_orders.csv"))
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.days < 1:
        parser.error("--days must be at least 1")
    generate(args.output, days=args.days, seed=args.seed)
    print(f"Wrote synthetic demo data to {args.output}")


if __name__ == "__main__":
    main()
