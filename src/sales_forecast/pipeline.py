"""Pipeline: ingest -> transform -> model, van CSV tot voorspelling.

Gebruik:  python -m sales_forecast.pipeline   (of: make run)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb

from sales_forecast import ingest, model, synthetic, transform

DATA_DIR = Path("data")
DEFAULT_CSV = DATA_DIR / "sales.csv"
DEFAULT_DB = DATA_DIR / "sales.duckdb"


@dataclass(frozen=True)
class PipelineResult:
    raw_rows: int
    clean_rows: int
    daily_rows: int
    forecast: dict[str, float]
    mape_pct: float


def run_on_connection(conn: duckdb.DuckDBPyConnection, csv_path: str | Path) -> PipelineResult:
    """Draai alle stappen op een bestaande verbinding (handig voor tests)."""
    raw_rows = ingest.load_raw_sales(conn, csv_path)
    counts = transform.run_transform(conn)
    return PipelineResult(
        raw_rows=raw_rows,
        clean_rows=counts["clean_rows"],
        daily_rows=counts["daily_rows"],
        forecast=model.forecast(conn),
        mape_pct=model.backtest(conn),
    )


def run(csv_path: str | Path = DEFAULT_CSV, db_path: str | Path = DEFAULT_DB) -> PipelineResult:
    """Draai de pipeline en schrijf alle tabellen naar het DuckDB-bestand `db_path`."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db_path)) as conn:
        return run_on_connection(conn, csv_path)


def main() -> int:
    if not DEFAULT_CSV.exists():
        rows = synthetic.write_csv(DEFAULT_CSV)
        print(f"Synthetische data gemaakt: {DEFAULT_CSV} ({rows:,} regels)")

    result = run()
    print(f"Ingelezen: {result.raw_rows:,} regels, na opschonen: {result.clean_rows:,}")
    print(f"daily_sales: {result.daily_rows:,} rijen in {DEFAULT_DB}")
    print(f"Backtest laatste dag: MAPE {result.mape_pct:.2f}%")
    print("Voorspelling morgen per winkel:")
    for store_id, revenue in sorted(result.forecast.items()):
        print(f"  {store_id}  EUR {revenue:>10,.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
