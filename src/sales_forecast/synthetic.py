"""Synthetische kassadata. Geseed: elke machine krijgt exact dezelfde rijen. Geen echte data.

De data is bewust een beetje rommelig, net als een echte kassa-export:
dubbele orderregels, Nederlandse datumnotatie, kleine letters in winkelcodes,
negatieve aantallen (retouren) en af en toe een onleesbare datum.
"""

from __future__ import annotations

import csv
import random
from collections.abc import Iterator
from datetime import date, timedelta
from pathlib import Path

from sales_forecast.ingest import RAW_COLUMNS

DEFAULT_SEED = 42
DEFAULT_START = date(2026, 9, 3)  # 15 dagen: do 3 t/m do 17 september

# Winkel -> relatieve grootte.
STORES = {
    "S01": 1.0,
    "S02": 1.4,
    "S03": 0.7,
    "S04": 1.1,
    "S05": 0.9,
    "S06": 1.6,
    "S07": 0.6,
    "S08": 1.2,
}
# Maandag t/m zondag.
WEEKDAY_FACTOR = (0.85, 0.8, 0.9, 1.0, 1.25, 1.45, 0.75)
CUSTOMERS_PER_STORE = 300
PRODUCT_COUNT = 80


def generate_rows(
    seed: int = DEFAULT_SEED,
    days: int = 15,
    start: date = DEFAULT_START,
    rows_per_day: int = 5000,
) -> Iterator[dict[str, str]]:
    """Genereer ruwe orderregels als dicts met tekstwaarden (zoals in de CSV)."""
    rng = random.Random(seed)
    products = [(f"P{i:03d}", round(rng.uniform(1.5, 60.0), 2)) for i in range(PRODUCT_COUNT)]
    store_ids = list(STORES)
    store_weights = list(STORES.values())
    order_seq = 0

    for offset in range(days):
        day = start + timedelta(days=offset)
        target = int(rows_per_day * WEEKDAY_FACTOR[day.weekday()])
        lines = 0
        while lines < target:
            store_id = rng.choices(store_ids, weights=store_weights)[0]
            cust_id = f"C{store_ids.index(store_id) + 1}{rng.randrange(CUSTOMERS_PER_STORE):04d}"
            order_seq += 1
            for line_no in range(1, rng.randint(1, 8) + 1):
                product_id, price = rng.choice(products)
                quantity = rng.choice((1, 1, 1, 2)) if price > 4 else rng.randint(1, 3)
                row = {
                    "order_id": f"O{order_seq:07d}",
                    "line_no": str(line_no),
                    "order_date": _format_date(rng, day),
                    "store_id": store_id.lower() if rng.random() < 0.05 else store_id,
                    "cust_id": "" if rng.random() < 0.01 else cust_id,
                    "product_id": product_id,
                    "quantity": str(-quantity if rng.random() < 0.003 else quantity),
                    "unit_price_eur": f"{price:.2f}",
                    "discount_pct": rng.choice(("0", "0", "0", "0", "10", "25")),
                }
                yield row
                lines += 1
                if rng.random() < 0.005:  # dubbel verstuurde orderregel
                    yield dict(row)
                    lines += 1


def _format_date(rng: random.Random, day: date) -> str:
    roll = rng.random()
    if roll < 0.002:
        return "31-02-2026"  # onleesbaar: bestaat niet
    if roll < 0.15:
        return day.strftime("%d-%m-%Y")
    if roll < 0.20:
        return f"{day.isoformat()}T{rng.randint(8, 21):02d}:{rng.randint(0, 59):02d}:00"
    return day.isoformat()


def write_csv(path: str | Path, **kwargs) -> int:
    """Schrijf gegenereerde rijen naar `path` en geef het aantal rijen terug."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAW_COLUMNS)
        writer.writeheader()
        for row in generate_rows(**kwargs):
            writer.writerow(row)
            count += 1
    return count
