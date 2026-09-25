"""Architectuurregels uit AGENTS.md, vastgelegd als test. Zo kan een agent ze niet vergeten."""

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SRC = Path(__file__).resolve().parents[2] / "src" / "sales_forecast"
DATES_MODULE = SRC / "utils" / "dates.py"
DATE_PARSING = re.compile(r"\b(strptime|fromisoformat|dateutil|to_datetime)\b")


def source_files() -> list[Path]:
    return sorted(path for path in SRC.rglob("*.py") if path != DATES_MODULE)


@pytest.mark.parametrize("path", source_files(), ids=lambda path: path.relative_to(SRC).as_posix())
def test_dates_are_only_parsed_in_utils_dates(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = [
        f"  {path.name}:{n}: {line.strip()}"
        for n, line in enumerate(lines, 1)
        if DATE_PARSING.search(line)
    ]
    assert not hits, (
        "Datums parsen gebeurt alleen in sales_forecast.utils.dates.parse_date "
        "(zie AGENTS.md). Gevonden:\n" + "\n".join(hits)
    )
