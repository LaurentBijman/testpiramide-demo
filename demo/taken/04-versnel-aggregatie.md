# Taak 04: versnel de aggregatie

> Stap 3 (simulatie). Kopieer het tekstblok hieronder naar je agent.

```text
Nu: aggregate_daily_sales in src/sales_forecast/transform.py rekent de omzet per
orderregel uit (aantal × prijs × korting) en telt die daarna op.

Gewenst: versnel de aggregatie.

Klaar als: make test en make it groen zijn.
```

<details>
<summary>Voor de presentator: waar let je op?</summary>

- Een voor de hand liggende "optimalisatie" is eerst aantallen optellen en dan één keer
  vermenigvuldigen: `sum(quantity) * avg(prijs × korting)` in plaats van
  `sum(quantity × prijs × korting)` (zie `fouten/04-versnelde-aggregatie.patch`).
- Wiskundig klopt dat alleen als elke klant per dag één orderregel heeft, of overal
  dezelfde prijs. Precies zo zien de kleine unit- en integratiefixtures eruit, dus die
  blijven groen.
- De simulatie speelt ~5.000 echte regels af (meerdere regels per klant, goedkope
  artikelen vaker in grotere aantallen). De dagomzet wijkt dan ~2,8% af en `make sim`
  wordt rood (drempel: 0,1%).
- Merk op: de "Klaar als" noemt `make sim` niet. Pas vanaf `demo/stap-3-klaar` staat in
  `AGENTS.md` dat wijzigingen aan transform/model ook `make sim` vereisen.
</details>
