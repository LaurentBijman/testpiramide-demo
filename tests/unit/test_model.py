from datetime import date

import pytest

from sales_forecast.model import backtest, forecast, mape, moving_average

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("values", "window", "expected"),
    [
        ([10.0], 7, 10.0),
        ([10.0, 20.0, 30.0], 7, 20.0),
        ([10.0, 20.0, 30.0], 2, 25.0),
        ([1.0] * 6 + [8.0], 7, 2.0),
    ],
)
def test_moving_average_uses_last_window_values(values, window, expected):
    assert moving_average(values, window) == pytest.approx(expected)


@pytest.mark.parametrize(("values", "window"), [([], 7), ([1.0], 0)], ids=["leeg", "window-0"])
def test_moving_average_rejects_bad_input(values, window):
    with pytest.raises(ValueError):
        moving_average(values, window)


@pytest.mark.parametrize(
    ("actual", "predicted", "expected"),
    [
        ([100.0], [100.0], 0.0),
        ([100.0], [90.0], 10.0),
        ([100.0, 200.0], [110.0, 180.0], 10.0),
        ([0.0, 50.0], [10.0, 25.0], 50.0),  # dag zonder omzet telt niet mee
    ],
)
def test_mape_in_percent(actual, predicted, expected):
    assert mape(actual, predicted) == pytest.approx(expected)


def test_mape_needs_equal_lengths():
    with pytest.raises(ValueError):
        mape([1.0, 2.0], [1.0])


@pytest.fixture
def daily_sales(conn):
    """Twee winkels, vier dagen; S02 heeft op 3 september geen verkopen."""
    conn.execute(
        """
        CREATE TABLE daily_sales AS
        SELECT * FROM (VALUES
            (DATE '2026-09-01', 'S01', 'C1', 10.0),
            (DATE '2026-09-02', 'S01', 'C1', 20.0),
            (DATE '2026-09-03', 'S01', 'C1', 30.0),
            (DATE '2026-09-04', 'S01', 'C1', 40.0),
            (DATE '2026-09-01', 'S02', 'C2', 50.0),
            (DATE '2026-09-02', 'S02', 'C2', 50.0),
            (DATE '2026-09-04', 'S02', 'C2', 50.0)
        ) AS t(date, store_id, cust_id, revenue_eur)
        """
    )
    return conn


def test_forecast_per_store_uses_all_history(daily_sales):
    assert forecast(daily_sales) == {"S01": 25.0, "S02": 50.0}


def test_forecast_as_of_ignores_later_days(daily_sales):
    assert forecast(daily_sales, as_of=date(2026, 9, 2)) == {"S01": 15.0, "S02": 50.0}


def test_backtest_last_day(daily_sales):
    # S01: voorspeld 20 (gem. 10, 20, 30), werkelijk 40 -> 50%; S02: 50 vs 50 -> 0%.
    assert backtest(daily_sales) == pytest.approx(25.0)
