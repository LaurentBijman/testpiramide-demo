"""Speel één geseede synthetische dag af door de echte pipeline.

Gedeeld door tests/simulation/test_replay.py en scripts/update_baseline.py,
zodat test en baseline gegarandeerd op dezelfde manier worden berekend.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

from sales_forecast import pipeline, synthetic

# 14 dagen historie voor het model + de dag die we afspelen (~5.000 orderregels).
REPLAY_SETTINGS = {"seed": 42, "days": 15, "rows_per_day": 5000}


def run_replay(workdir: Path) -> dict:
    """Genereer de data, draai de pipeline en vat de afgespeelde (laatste) dag samen."""
    csv_path = workdir / "replay.csv"
    db_path = workdir / "replay.duckdb"
    synthetic.write_csv(csv_path, **REPLAY_SETTINGS)
    result = pipeline.run(csv_path, db_path)

    with duckdb.connect(str(db_path), read_only=True) as conn:
        day = conn.execute("SELECT max(date) FROM daily_sales").fetchone()[0]
        lines = conn.execute(
            "SELECT count(*) FROM clean_sales WHERE order_date = ?", [day]
        ).fetchone()[0]
        store_totals = dict(
            conn.execute(
                "SELECT store_id, round(sum(revenue_eur), 2) FROM daily_sales "
                "WHERE date = ? GROUP BY store_id ORDER BY store_id",
                [day],
            ).fetchall()
        )

    return {
        "settings": REPLAY_SETTINGS,
        "replay_date": day.isoformat(),
        "order_lines": lines,
        "store_totals_eur": store_totals,
        "total_eur": round(sum(store_totals.values()), 2),
        "mape_pct": result.mape_pct,
    }
