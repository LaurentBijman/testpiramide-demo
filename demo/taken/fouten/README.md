# Kant-en-klare fouten

Doet je agent live iets anders dan verwacht (of heb je geen agent)? Pas dan de patch toe.
Het resultaat is precies wat een agent in de valkuil zou opleveren.

| Patch                                | Toepassen op              | Wat het doet                                          | Verwacht                          |
|--------------------------------------|---------------------------|-------------------------------------------------------|-----------------------------------|
| `01-eigen-datumparser.patch`         | `demo/stap-1-unit`        | eigen `strptime`-helper in `model.py`                 | `make test`: 1 rood (architectuur) |
| `02a-regressie-ontdubbeling.patch`   | `demo/stap-1-unit`        | ontdubbeling weg uit `transform.py` (de "bug")        | `make test`: 1 rood               |
| `02b-afgezwakte-assert.patch`        | na 02a                    | `== 1` wordt `>= 1` in de test (de valkuil)           | `make test`: groen, bug blijft    |
| `03-hernoem-kolom.patch`             | `demo/stap-0-start`, `demo/stap-2-integratie` | `cust_id` wordt `customer_id` in `daily_sales` | stap 0: dashboard crasht; stap 2: `make it` rood |
| `04-versnelde-aggregatie.patch`      | `demo/stap-3-simulatie`   | `sum(q) * avg(p)` in plaats van `sum(q * p)`          | `make test`/`make it` groen, `make sim` rood |

```bash
git apply demo/taken/fouten/03-hernoem-kolom.patch   # toepassen
make reset                                           # alles terugdraaien
```
