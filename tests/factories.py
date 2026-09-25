"""Kleine hulpjes om testdata te maken, gedeeld door alle testlagen."""

from __future__ import annotations

import duckdb

from sales_forecast.ingest import RAW_COLUMNS


def raw_row(**overrides: str | None) -> dict[str, str | None]:
    """Eén geldige orderregel zoals hij uit de kassa komt; overschrijf wat je wilt testen."""
    row: dict[str, str | None] = {
        "order_id": "O0000001",
        "line_no": "1",
        "order_date": "2026-09-14",
        "store_id": "S01",
        "cust_id": "C10001",
        "product_id": "P001",
        "quantity": "2",
        "unit_price_eur": "10.00",
        "discount_pct": "0",
    }
    row.update(overrides)
    return row


def load_raw_rows(conn: duckdb.DuckDBPyConnection, rows: list[dict[str, str | None]]) -> None:
    """Zet rijen als `raw_sales` in DuckDB, net zoals `ingest.load_raw_sales` dat doet."""
    columns = ", ".join(f"{col} VARCHAR" for col in RAW_COLUMNS)
    conn.execute(f"CREATE OR REPLACE TABLE raw_sales ({columns})")
    placeholders = ", ".join("?" for _ in RAW_COLUMNS)
    conn.executemany(
        f"INSERT INTO raw_sales VALUES ({placeholders})",
        [[row[col] for col in RAW_COLUMNS] for row in rows],
    )
