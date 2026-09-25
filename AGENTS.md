# AGENTS.md

## Commando's

- `make test`: unit tests (duurt enkele seconden). Draai ze na elke wijziging.

## Regels

- Datums parsen gaat altijd via `sales_forecast.utils.dates.parse_date`. Schrijf geen
  eigen parser (geen `strptime`, `fromisoformat`, `dateutil`, ...) buiten `utils/dates.py`.
  Mist er een formaat? Voeg het toe aan `DATE_FORMATS` en aan `tests/unit/test_dates.py`.
  `tests/unit/test_architecture.py` bewaakt deze regel.
- Een falende test maak je groen door de code te repareren, niet de test. Asserts
  afzwakken, tests verwijderen of `skip`/`xfail` toevoegen mag niet. Denk je dat de test
  zelf fout is? Stop en leg uit waarom, in plaats van hem aan te passen.
