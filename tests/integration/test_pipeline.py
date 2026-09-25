"""De hele keten op een klein, met de hand narekenbaar bestand (data/sales_small.csv).

S01 verkoopt op dag n precies n x EUR 10; S02 elke dag 1 x EUR 30 met 10% korting,
plus op 5 september een extra klant (EUR 5). Rommel die eruit moet: één dubbele
orderregel, één onbestaande datum en één retour.
"""

import pytest

from sales_forecast.dashboard import render

pytestmark = pytest.mark.integration


def test_pipeline_row_counts(pipeline_run):
    result, _ = pipeline_run
    assert (result.raw_rows, result.clean_rows, result.daily_rows) == (20, 17, 17)


def test_revenue_per_store(db):
    totals = db.execute(
        "SELECT store_id, round(sum(revenue_eur), 2) FROM daily_sales GROUP BY 1 ORDER BY 1"
    ).fetchall()
    assert totals == [("S01", 360.00), ("S02", 221.00)]


def test_forecast_and_backtest(pipeline_run):
    result, _ = pipeline_run
    assert result.forecast == {"S01": 50.00, "S02": 27.71}
    assert result.mape_pct == pytest.approx(26.31, abs=0.01)


def test_dashboard_reads_daily_sales(db):
    text = render(db)
    assert "S01" in text
    assert "C1 " in text  # beste klant staat in de top 5
