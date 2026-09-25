"""Datums parsen: de enige plek in de codebase waar tekst een datum wordt."""

from __future__ import annotations

from datetime import date, datetime

# Volgorde telt: eerst ISO (de standaard), daarna de Nederlandse notaties uit de kassa-export.
DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%d-%m-%Y",
    "%d/%m/%Y",
)


def parse_date(value: str | date | datetime) -> date:
    """Zet een datum (tekst, date of datetime) om naar een `date`.

    Ondersteunt ISO (`2026-09-14`, ook met tijd) en Nederlandse notatie
    (`14-09-2026`, `14/09/2026`). Gooit `ValueError` bij alles wat geen datum is.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError(f"Geen datum: {value!r}")

    text = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Onbekend datumformaat: {value!r}")
