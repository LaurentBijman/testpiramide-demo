"""Transform: schoon de ruwe verkopen op en aggregeer naar omzet per dag, winkel en klant.

Output is de tabel `daily_sales` (date, store_id, cust_id, revenue_eur).
Het dashboard en het model lezen deze tabel op kolomnaam: het schema is een contract.
"""

from __future__ import annotations

import json

import duckdb

from sales_forecast.utils.dates import parse_date

LOOKUP_SCHEMA = {"raw_date": "VARCHAR", "order_date": "DATE"}

CLEAN_SQL = """
CREATE OR REPLACE TABLE clean_sales AS
WITH typed AS (
    SELECT
        trim(r.order_id)                                   AS order_id,
        TRY_CAST(r.line_no AS INTEGER)                     AS line_no,
        d.order_date                                       AS order_date,
        upper(trim(r.store_id))                            AS store_id,
        coalesce(nullif(trim(r.cust_id), ''), 'ONBEKEND')  AS cust_id,
        trim(r.product_id)                                 AS product_id,
        TRY_CAST(r.quantity AS INTEGER)                    AS quantity,
        TRY_CAST(r.unit_price_eur AS DECIMAL(10, 2))       AS unit_price_eur,
        coalesce(TRY_CAST(r.discount_pct AS DECIMAL(5, 2)), 0) AS discount_pct
    FROM raw_sales AS r
    LEFT JOIN date_lookup AS d ON d.raw_date = r.order_date
)
SELECT *
FROM typed
WHERE order_date IS NOT NULL
  AND store_id <> ''
  AND quantity > 0
  AND unit_price_eur >= 0
  AND discount_pct BETWEEN 0 AND 100
-- Kassa's sturen soms een orderregel twee keer: die telt maar één keer.
QUALIFY row_number() OVER (PARTITION BY order_id, line_no ORDER BY order_date) = 1
"""

AGGREGATE_SQL = """
CREATE OR REPLACE TABLE daily_sales AS
SELECT
    order_date AS date,
    store_id,
    cust_id,
    -- Rekenen in DECIMAL: exact, dus op elke machine tot op de cent dezelfde uitkomst.
    round(sum(quantity * unit_price_eur * (100 - discount_pct)) / 100, 2)::DOUBLE AS revenue_eur
FROM clean_sales
GROUP BY order_date, store_id, cust_id
ORDER BY date, store_id, cust_id
"""


def build_date_lookup(conn: duckdb.DuckDBPyConnection) -> int:
    """Parse elke unieke datumtekst uit `raw_sales` één keer; onleesbare datums worden NULL."""
    raw_dates = [
        row[0] for row in conn.execute("SELECT DISTINCT order_date FROM raw_sales").fetchall()
    ]
    lookup = []
    for raw in raw_dates:
        try:
            lookup.append({"raw_date": raw, "order_date": parse_date(raw).isoformat()})
        except ValueError:
            lookup.append({"raw_date": raw, "order_date": None})

    # Eén JSON-parameter is veel sneller dan duizenden losse INSERTs.
    conn.execute(
        "CREATE OR REPLACE TABLE date_lookup AS SELECT unnest(from_json(?, ?), recursive := true)",
        [json.dumps(lookup), json.dumps([LOOKUP_SCHEMA])],
    )
    return len(lookup)


def clean_sales(conn: duckdb.DuckDBPyConnection) -> int:
    """Maak `clean_sales` uit `raw_sales` en geef het aantal overgebleven regels terug."""
    build_date_lookup(conn)
    conn.execute(CLEAN_SQL)
    return conn.execute("SELECT count(*) FROM clean_sales").fetchone()[0]


def aggregate_daily_sales(conn: duckdb.DuckDBPyConnection) -> int:
    """Aggregeer `clean_sales` naar `daily_sales` en geef het aantal rijen terug."""
    conn.execute(AGGREGATE_SQL)
    return conn.execute("SELECT count(*) FROM daily_sales").fetchone()[0]


def run_transform(conn: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Voer de hele transformatiestap uit."""
    return {
        "clean_rows": clean_sales(conn),
        "daily_rows": aggregate_daily_sales(conn),
    }
