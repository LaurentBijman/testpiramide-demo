# Taak 01: voeg een helper toe om datums te parsen

> Stap 1 (unit). Kopieer het tekstblok hieronder naar je agent.

```text
Nu: forecast(conn, as_of=...) en backtest(conn, day=...) in
src/sales_forecast/model.py accepteren alleen een datetime.date.

Gewenst: beide accepteren ook tekst, zoals "2026-09-14" en "14-09-2026".
Voeg een helper toe om datums te parsen.

Klaar als: make test groen is en er unit tests zijn voor as_of en day als tekst.
```

<details>
<summary>Voor de presentator: waar let je op?</summary>

- De prompt vraagt letterlijk om "een helper". Zonder regels schrijft een agent dan graag
  een eigen `strptime(...)` in `model.py` (zie `fouten/01-eigen-datumparser.patch`).
- `AGENTS.md` zegt dat datums via `utils/dates.parse_date` gaan, en
  `tests/unit/test_architecture.py` wordt rood zodra er ergens anders `strptime` staat.
- Goed resultaat: `parse_date` hergebruiken (zie branch `demo/stap-1-klaar`).
</details>
