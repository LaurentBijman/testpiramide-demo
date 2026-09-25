# Taak 03: hernoem cust_id naar customer_id

> Stap 0 (het probleem) en stap 2 (integratie). Kopieer het tekstblok hieronder naar je agent.

```text
Nu: de tabel daily_sales heeft een kolom cust_id.

Gewenst: hernoem cust_id naar customer_id, zodat het aansluit bij de naam in het CRM.

Klaar als: de pipeline draait (make run) en de tests groen zijn.
```

<details>
<summary>Voor de presentator: waar let je op?</summary>

- Stap 0: er zijn geen tests, `make run` werkt, dus "alles werkt". Maar
  `python -m sales_forecast.dashboard` crasht: het dashboard leest `cust_id` op naam.
- Stap 2: de unit tests blijven groen (die kijken niet naar het schema), maar
  `tests/integration/test_contract.py` wordt rood, net als de dashboard-test.
- Let op: het verwachte schema staat uitgeschreven in de contracttest en wordt niet uit de
  code geïmporteerd. Anders zou de test gewoon meebewegen met de hernoeming.
- Goed resultaat vanaf `demo/stap-2-klaar`: de agent stopt en vraagt het eerst, omdat
  `AGENTS.md` zegt dat `daily_sales` een contract is.
- Terugval: `git apply demo/taken/fouten/03-hernoem-kolom.patch`.
</details>
