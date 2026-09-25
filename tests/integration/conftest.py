"""Integratie: de echte pipeline op een echt DuckDB-bestand in een tijdelijke map."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

from sales_forecast import pipeline

FIXTURE_CSV = Path(__file__).parent / "data" / "sales_small.csv"


@pytest.fixture(scope="module")
def pipeline_run(tmp_path_factory):
    """Draai de pipeline één keer per testmodule; geeft (resultaat, pad naar database)."""
    db_path = tmp_path_factory.mktemp("duckdb") / "sales.duckdb"
    result = pipeline.run(FIXTURE_CSV, db_path)
    return result, db_path


@pytest.fixture
def db(pipeline_run):
    """Alleen-lezen verbinding met de database die de pipeline heeft geschreven."""
    _, db_path = pipeline_run
    with duckdb.connect(str(db_path), read_only=True) as connection:
        yield connection
