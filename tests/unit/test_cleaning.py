from datetime import date

import pytest

from sales_forecast.transform import aggregate_daily_sales, clean_sales
from tests.factories import load_raw_rows, raw_row

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"quantity": "-1"}, "retour: negatief aantal"),
        ({"quantity": "0"}, "aantal nul"),
        ({"quantity": "twee"}, "aantal is geen getal"),
        ({"unit_price_eur": "-3.50"}, "negatieve prijs"),
        ({"discount_pct": "150"}, "korting boven 100%"),
        ({"order_date": "31-02-2026"}, "datum bestaat niet"),
        ({"order_date": "morgen"}, "geen datum"),
        ({"store_id": ""}, "geen winkel"),
        ({"store_id": None}, "winkel ontbreekt"),
    ],
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_invalid_rows_are_dropped(conn, overrides, reason):
    load_raw_rows(conn, [raw_row(**overrides)])
    assert clean_sales(conn) == 0, reason


@pytest.mark.parametrize(
    "order_date", ["2026-09-14", "14-09-2026", "14/09/2026", "2026-09-14T18:05:00"]
)
def test_supported_date_formats_become_the_same_day(conn, order_date):
    load_raw_rows(conn, [raw_row(order_date=order_date)])
    clean_sales(conn)
    assert conn.execute("SELECT order_date FROM clean_sales").fetchall() == [(date(2026, 9, 14),)]


@pytest.mark.parametrize("store_id", ["S01", "s01", "  S01 "])
def test_store_id_is_normalised(conn, store_id):
    load_raw_rows(conn, [raw_row(store_id=store_id)])
    clean_sales(conn)
    assert conn.execute("SELECT store_id FROM clean_sales").fetchone()[0] == "S01"


def test_duplicate_order_line_counts_once(conn):
    row = raw_row()
    load_raw_rows(conn, [row, dict(row)])
    clean_sales(conn)
    rows = conn.execute("SELECT order_id, line_no FROM clean_sales").fetchall()
    assert len(rows) == 1


def test_missing_discount_means_no_discount(conn):
    load_raw_rows(conn, [raw_row(discount_pct="")])
    clean_sales(conn)
    assert conn.execute("SELECT discount_pct FROM clean_sales").fetchone()[0] == 0.0


def test_missing_customer_becomes_onbekend(conn):
    load_raw_rows(conn, [raw_row(cust_id=" ")])
    clean_sales(conn)
    assert conn.execute("SELECT cust_id FROM clean_sales").fetchone()[0] == "ONBEKEND"


@pytest.mark.parametrize(
    ("quantity", "price", "discount", "expected"),
    [
        ("1", "10.00", "0", 10.00),
        ("3", "2.50", "0", 7.50),
        ("2", "10.00", "25", 15.00),
        ("1", "9.99", "10", 8.99),
    ],
)
def test_revenue_is_quantity_times_price_minus_discount(conn, quantity, price, discount, expected):
    load_raw_rows(conn, [raw_row(quantity=quantity, unit_price_eur=price, discount_pct=discount)])
    clean_sales(conn)
    aggregate_daily_sales(conn)
    assert conn.execute("SELECT revenue_eur FROM daily_sales").fetchone()[0] == pytest.approx(
        expected
    )


def test_revenue_is_summed_per_day_store_and_customer(conn):
    load_raw_rows(
        conn,
        [
            raw_row(order_id="O1", cust_id="C1", unit_price_eur="10.00"),
            raw_row(order_id="O2", cust_id="C2", unit_price_eur="4.00"),
            raw_row(order_id="O3", cust_id="C1", store_id="S02", unit_price_eur="1.00"),
        ],
    )
    clean_sales(conn)
    assert aggregate_daily_sales(conn) == 3
    total = conn.execute("SELECT sum(revenue_eur) FROM daily_sales").fetchone()[0]
    assert total == pytest.approx(2 * (10.00 + 4.00 + 1.00))
