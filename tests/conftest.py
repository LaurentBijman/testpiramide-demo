from __future__ import annotations

import duckdb
import pytest


@pytest.fixture
def conn():
    """Een lege DuckDB in het geheugen: snel en na de test weer weg."""
    with duckdb.connect(":memory:") as connection:
        yield connection
