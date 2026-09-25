"""Model: voorspel de omzet per winkel voor de volgende dag met een voortschrijdend gemiddelde."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, timedelta

import duckdb

from sales_forecast.utils.dates import parse_date

WINDOW_DAYS = 7


def store_revenue_by_day(conn: duckdb.DuckDBPyConnection) -> dict[str, list[tuple[date, float]]]:
    """Totale omzet per winkel per dag uit `daily_sales`, oplopend op datum."""
    rows = conn.execute(
        """
        SELECT store_id, date, sum(revenue_eur) AS revenue_eur
        FROM daily_sales
        GROUP BY store_id, date
        ORDER BY store_id, date
        """
    ).fetchall()
    history: dict[str, list[tuple[date, float]]] = {}
    for store_id, day, revenue in rows:
        history.setdefault(store_id, []).append((day, revenue))
    return history


def moving_average(values: Sequence[float], window: int = WINDOW_DAYS) -> float:
    """Gemiddelde van de laatste `window` waarden (of van alles, als er minder zijn)."""
    if window < 1:
        raise ValueError("window moet minstens 1 zijn")
    if not values:
        raise ValueError("Geen historie om te voorspellen")
    tail = values[-window:]
    return sum(tail) / len(tail)


def mape(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """Mean Absolute Percentage Error in procenten; dagen zonder omzet tellen niet mee."""
    if len(actual) != len(predicted):
        raise ValueError("actual en predicted moeten even lang zijn")
    pairs = [(a, p) for a, p in zip(actual, predicted, strict=True) if a != 0]
    if not pairs:
        raise ValueError("Geen dagen met omzet om MAPE over te berekenen")
    return 100 * sum(abs(a - p) / abs(a) for a, p in pairs) / len(pairs)


def forecast(
    conn: duckdb.DuckDBPyConnection,
    as_of: date | str | None = None,
    window: int = WINDOW_DAYS,
) -> dict[str, float]:
    """Voorspel per winkel de omzet voor de dag ná `as_of` (standaard: de laatste dag met data).

    `as_of` mag een `date` zijn of tekst, zoals "2026-09-14" of "14-09-2026".
    """
    cutoff = parse_date(as_of) if as_of is not None else None
    predictions: dict[str, float] = {}
    for store_id, series in store_revenue_by_day(conn).items():
        values = [revenue for day, revenue in series if cutoff is None or day <= cutoff]
        if values:
            predictions[store_id] = round(moving_average(values, window), 2)
    return predictions


def backtest(
    conn: duckdb.DuckDBPyConnection,
    day: date | str | None = None,
    window: int = WINDOW_DAYS,
) -> float:
    """MAPE van de voorspelling voor `day` (standaard: laatste dag), op basis van eerdere dagen.

    `day` mag een `date` zijn of tekst, net als `as_of` bij `forecast`.
    """
    history = store_revenue_by_day(conn)
    if not history:
        raise ValueError("daily_sales is leeg")
    if day is None:
        day = max(d for series in history.values() for d, _ in series)
    else:
        day = parse_date(day)

    predictions = forecast(conn, as_of=day - timedelta(days=1), window=window)
    actual, predicted = [], []
    for store_id, series in history.items():
        revenue_on_day = dict(series).get(day)
        if revenue_on_day is not None and store_id in predictions:
            actual.append(revenue_on_day)
            predicted.append(predictions[store_id])
    return round(mape(actual, predicted), 2)
