"""Contracttest: `daily_sales` is wat afnemers (zoals dashboard.py) mogen verwachten.

Het verwachte schema staat hier bewust uitgeschreven en wordt NIET uit de code
geïmporteerd: als de code verandert, beweegt deze test niet vanzelf mee.
"""

import pytest

pytestmark = pytest.mark.integration

EXPECTED_SCHEMA = [
    ("date", "DATE"),
    ("store_id", "VARCHAR"),
    ("cust_id", "VARCHAR"),
    ("revenue_eur", "DOUBLE"),
]


def test_daily_sales_schema_is_exactly_the_contract(db):
    actual = [
        (name, column_type)
        for name, column_type, *_ in db.execute("DESCRIBE daily_sales").fetchall()
    ]
    assert actual == EXPECTED_SCHEMA


def test_daily_sales_has_one_row_per_day_store_and_customer(db):
    duplicates = db.execute(
        """
        SELECT count(*) FROM (
            SELECT date, store_id, cust_id
            FROM daily_sales
            GROUP BY date, store_id, cust_id
            HAVING count(*) > 1
        )
        """
    ).fetchone()[0]
    assert duplicates == 0


def test_daily_sales_has_no_missing_values(db):
    nulls = db.execute(
        "SELECT count(*) FROM daily_sales "
        "WHERE date IS NULL OR store_id IS NULL OR cust_id IS NULL OR revenue_eur IS NULL"
    ).fetchone()[0]
    assert nulls == 0
