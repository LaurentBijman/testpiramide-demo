# AGENTS.md

Instructies voor AI-agents (en mensen) die in deze repo werken.

## Stack

- Python 3.12, DuckDB, pytest, ruff. Geen externe services, geen echte data.
- Pipeline: `ingest.py` (CSV → `raw_sales`) → `transform.py` (`clean_sales` →
  `daily_sales`) → `model.py` (voortschrijdend gemiddelde + MAPE).
- Testdata is synthetisch en geseed (`synthetic.py`): op elke machine exact hetzelfde.

## Commando's

| Commando         | Wat                                                   | Wanneer                              |
|------------------|-------------------------------------------------------|--------------------------------------|
| `make test`      | unit tests (`tests/unit`), < 1 s                      | na elke wijziging                    |
| `make it`        | integratietests, echte DuckDB (`tests/integration`)   | voordat je zegt dat je klaar bent    |
| `make sim`       | simulatie van een geseede dag tegen de baseline       | als je `transform.py` of `model.py` wijzigt |
| `make lint`      | ruff check + format-check                             | voor elke commit                     |
| `make all`       | lint + unit + integratie + simulatie                  | bij twijfel                          |
| `make run`       | pipeline draaien op `data/sales.csv`                  |                                      |
| `make dashboard` | dashboard tonen (leest `daily_sales`)                 |                                      |

## Architectuur

```
src/sales_forecast/
  ingest.py        leest de CSV als tekst in `raw_sales`; interpreteert niets
  transform.py     opschonen (`clean_sales`) en aggregeren (`daily_sales`)
  model.py         voorspelling per winkel + backtest (MAPE)
  dashboard.py     afnemer: leest `daily_sales` op kolomnaam
  pipeline.py      zet de stappen achter elkaar
  synthetic.py     geseede synthetische kassadata
  utils/dates.py   de enige plek waar tekst een datum wordt
tests/
  unit/            snel, in-memory DuckDB, geparametriseerd
  integration/     echte pipeline op een DuckDB-bestand; contracttest op `daily_sales`
  simulation/      afgespeelde synthetische dag vs. `baseline.json`
```

- Geld reken je in DECIMAL (exact); pas in de output wordt `revenue_eur` een DOUBLE.
- Contract `daily_sales`: `date DATE`, `store_id VARCHAR`, `cust_id VARCHAR`,
  `revenue_eur DOUBLE`, één rij per (date, store_id, cust_id).

## Regels

- Datums parsen gaat altijd via `sales_forecast.utils.dates.parse_date`. Schrijf geen
  eigen parser (geen `strptime`, `fromisoformat`, `dateutil`, ...) buiten `utils/dates.py`.
  Mist er een formaat? Voeg het toe aan `DATE_FORMATS` en aan `tests/unit/test_dates.py`.
  `tests/unit/test_architecture.py` bewaakt deze regel.
- Een falende test maak je groen door de code te repareren, niet de test. Asserts
  afzwakken, tests verwijderen of `skip`/`xfail` toevoegen mag niet. Denk je dat de test
  zelf fout is? Stop en leg uit waarom, in plaats van hem aan te passen.
- `daily_sales` is een contract met afnemers, zoals `dashboard.py`. Kolommen hernoem,
  verwijder of hertype je niet. Is een wijziging echt nodig? Stop en vraag het eerst. Een
  nieuwe kolom toevoegen mag, maar werk dan in dezelfde wijziging
  `tests/integration/test_contract.py` én alle afnemers bij.
- Raak je `transform.py` of `model.py` aan (ook "alleen voor snelheid"), draai dan
  `make sim`. Een optimalisatie mag de uitkomst niet veranderen.
- `tests/simulation/baseline.json` werk je alleen bij met `make baseline REDEN="..."`, en
  alleen als de verandering bedoeld is en de gebruiker erom vraagt. De drempels in
  `tests/simulation/test_replay.py` pas je nooit aan.
- Nieuwe logica krijgt een unit test in `tests/unit/`, bij voorkeur geparametriseerd.
- Geen nieuwe dependencies zonder te vragen.

## Klaar betekent

`make test` en `make it` zijn groen, en `make lint` geeft geen fouten.
Heb je `transform.py` of `model.py` gewijzigd, dan is ook `make sim` groen.
Meld in je samenvatting welke commando's je hebt gedraaid en wat de uitkomst was.
