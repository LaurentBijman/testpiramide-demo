from datetime import date, datetime

import pytest

from sales_forecast.utils.dates import parse_date

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "value",
    [
        "2026-09-14",
        "  2026-09-14  ",
        "2026-09-14T18:05:00",
        "2026-09-14 18:05:00",
        "14-09-2026",
        "14/09/2026",
        date(2026, 9, 14),
        datetime(2026, 9, 14, 18, 5),
    ],
    ids=[
        "iso",
        "spaties",
        "iso-met-T",
        "iso-met-tijd",
        "nl-streepjes",
        "nl-slashes",
        "date",
        "datetime",
    ],
)
def test_parse_date_accepts_supported_formats(value):
    assert parse_date(value) == date(2026, 9, 14)


@pytest.mark.parametrize(
    "value",
    ["", "morgen", "31-02-2026", "2026/09/14", "09-14-2026", None, 20260914],
    ids=["leeg", "tekst", "30-februari", "iso-met-slashes", "amerikaans", "none", "int"],
)
def test_parse_date_rejects_everything_else(value):
    with pytest.raises(ValueError):
        parse_date(value)
