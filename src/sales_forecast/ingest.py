"""Ingest: lees de ruwe kassa-export (CSV) in DuckDB, zonder iets te interpreteren."""

from __future__ import annotations

from pathlib import Path

import duckdb

RAW_COLUMNS = (
    "order_id",
    "line_no",
    "order_date",
    "store_id",
    "cust_id",
    "product_id",
    "quantity",
    "unit_price_eur",
    "discount_pct",
)


def load_raw_sales(conn: duckdb.DuckDBPyConnection, csv_path: str | Path) -> int:
    """Laad de CSV als tabel `raw_sales` (alles als tekst) en geef het aantal rijen terug."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV niet gevonden: {path}")

    conn.execute(
        "CREATE OR REPLACE TABLE raw_sales AS "
        "SELECT * FROM read_csv(?, header = true, all_varchar = true)",
        [str(path)],
    )
    columns = tuple(row[0] for row in conn.execute("DESCRIBE raw_sales").fetchall())
    missing = [col for col in RAW_COLUMNS if col not in columns]
    if missing:
        raise ValueError(f"Kolommen ontbreken in {path.name}: {missing}")

    return conn.execute("SELECT count(*) FROM raw_sales").fetchone()[0]
