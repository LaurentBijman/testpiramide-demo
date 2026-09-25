"""Dashboard: een downstream afnemer van `daily_sales`.

Leest de tabel op kolomnaam, net als een BI-tool of een ander team zou doen.
Breekt het contract (bijv. een hernoemde kolom), dan breekt dit dashboard.

Gebruik:  python -m sales_forecast.dashboard
"""

from __future__ import annotations

import sys

import duckdb

from sales_forecast.pipeline import DEFAULT_DB


def store_totals(conn: duckdb.DuckDBPyConnection) -> list[tuple[str, float]]:
    """Totale omzet per winkel, hoogste eerst."""
    return conn.execute(
        """
        SELECT store_id, round(sum(revenue_eur), 2) AS revenue_eur
        FROM daily_sales
        GROUP BY store_id
        ORDER BY revenue_eur DESC
        """
    ).fetchall()


def top_customers(conn: duckdb.DuckDBPyConnection, limit: int = 5) -> list[tuple[str, int, float]]:
    """Beste klanten: aantal actieve dagen en totale omzet."""
    return conn.execute(
        """
        SELECT cust_id,
               count(DISTINCT date) AS active_days,
               round(sum(revenue_eur), 2) AS revenue_eur
        FROM daily_sales
        WHERE cust_id <> 'ONBEKEND'
        GROUP BY cust_id
        ORDER BY revenue_eur DESC, cust_id
        LIMIT ?
        """,
        [limit],
    ).fetchall()


def render(conn: duckdb.DuckDBPyConnection) -> str:
    """Bouw het dashboard als platte tekst."""
    lines = ["== Omzet per winkel ==", ""]
    lines += [f"  {store:<6} EUR {revenue:>12,.2f}" for store, revenue in store_totals(conn)]
    lines += ["", "== Top 5 klanten ==", ""]
    lines += [
        f"  {cust:<8} {days:>2} dagen  EUR {revenue:>10,.2f}"
        for cust, days, revenue in top_customers(conn)
    ]
    return "\n".join(lines)


def main() -> int:
    if not DEFAULT_DB.exists():
        print(f"{DEFAULT_DB} bestaat nog niet. Draai eerst: make run", file=sys.stderr)
        return 1
    with duckdb.connect(str(DEFAULT_DB), read_only=True) as conn:
        print(render(conn))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
