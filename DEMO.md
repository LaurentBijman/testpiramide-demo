# Demoscript: de testpiramide voor data- en ML-code (±15 minuten)

Draaiboek voor de presentator. Deelnemers doen live mee in hun eigen fork.
Elke stap heeft een startbranch en een `-klaar`-branch. Wie achterloopt, haalt in met één commando.

| Tijd        | Stap | Laag                     | Demomoment                                      |
|-------------|------|--------------------------|-------------------------------------------------|
| 0:00 – 1:00 | –    | –                        | Intro: wat gaan we doen                         |
| 1:00 – 3:30 | 0    | geen tests               | Agent hernoemt een kolom: "alles werkt", dashboard crasht |
| 3:30 – 7:30 | 1    | unit                     | Test + regel sturen de agent; valkuil "maak groen" |
| 7:30 – 10:00| 2    | integratie               | Zelfde hernoeming: unit groen, contracttest rood |
| 10:00 – 13:00| 3   | simulatie                | "Versnel de aggregatie": alleen de simulatie ziet het |
| 13:00 – 14:30| 4   | vastleggen               | AGENTS.md, pre-commit, CI, branch protection    |
| 14:30 – 15:00| –   | afsluiting               | De piramide + huiswerk                          |

## Voorbereiding (vóór de sessie)

- [ ] Deze repo staat op GitHub en deelnemers hebben de link. Zorg dat alle `demo/*`-branches gepusht zijn: `git push origin --all`.
- [ ] Open je eigen Codespace (of lokale clone) en draai `make setup` en `make stap N=0`, dan `make run` (maakt `data/`).
- [ ] Je agent staat klaar in dezelfde map. Open `demo/taken/` in een tabblad om te kunnen kopiëren.
- [ ] Lettergrootte terminal en editor omhoog. `make help` laat alle commando's zien.
- [ ] Doet de agent live iets anders? Pak de patch uit `demo/taken/fouten/` (zie de README daar). Het verhaal blijft hetzelfde.

Tijdens de demo gebruikt de presentator de agent. Deelnemers mogen dat ook, maar de patches zijn sneller en geven iedereen hetzelfde resultaat.
In de blokken "Jij doet mee" staan daarom de patches.

---

## Intro (0:00 – 1:00)

**Ik zeg:** "Agents schrijven snel code, maar hoe weten ze dat het klopt? Dat vertellen tests ze.
We bouwen in vier stappen een testpiramide voor een kleine verkooppijplijn: CSV → opschonen → dagomzet → voorspelling.
Na elke stap kijken we wat een agent nu wél en niet stukmaakt."

Laat kort de structuur zien: `src/sales_forecast/` met `ingest.py`, `transform.py`, `model.py`, `utils/dates.py` en `dashboard.py` (de afnemer).

---

## Stap 0: het probleem (1:00 – 3:30)

**Doel:** laten zien dat "het draait" niet betekent dat het klopt. **Laag:** nog geen, er zijn geen tests.

### Ik laat zien

1. `make stap N=0`: "We beginnen zonder tests, en `AGENTS.md` is leeg."
2. `make run`, daarna `make dashboard`: "De pipeline maakt `daily_sales`, het dashboard leest die op kolomnaam."
3. Plak `demo/taken/03-hernoem-kolom.md` in de agent: *"Hernoem cust_id naar customer_id."*
   (Terugval: `git apply demo/taken/fouten/03-hernoem-kolom.patch`.)
4. `make run`: "De agent meldt dat het klaar is, de pipeline draait. Alles werkt… toch?"
5. `python -m sales_forecast.dashboard`: "Het dashboard, een afnemer die de agent niet kent, crasht. Niemand heeft dit gemerkt."
6. `make reset`: "Terug naar het begin. Dit gaan we voorkomen."

### Jij doet mee

```bash
make stap N=0
make run
make dashboard
git apply demo/taken/fouten/03-hernoem-kolom.patch
make run
python -m sales_forecast.dashboard
make reset
```

### Verwacht resultaat

- `make run` werkt vóór en na de hernoeming (laatste regels: voorspelling per winkel, `S01 … S08`).
- `python -m sales_forecast.dashboard` na de hernoeming:
  ```
  _duckdb.BinderException: Binder Error: Referenced column "cust_id" not found in FROM clause!
  Candidate bindings: "customer_id", "store_id"
  ```

### Achter?

```bash
make reset && make stap N=1
```

---

## Stap 1: unit tests (3:30 – 7:30)

**Doel:** snelle tests en een regel in `AGENTS.md` sturen wat de agent doet. **Laag:** unit (in-memory, < 1 s, draait bij elke wijziging).

### Ik laat zien

1. `make stap N=1`, open `tests/unit/`: "Geparametriseerde tests voor opschonen, datums en het model, plus `test_architecture.py`, die zoekt naar `strptime` buiten `utils/dates.py`."
2. Open `AGENTS.md`: "Twee regels: datums gaan via `parse_date`, en je maakt een test niet groen door hem af te zwakken."
3. `make test`: "61 tests in minder dan een seconde. Dit mag een agent na elke wijziging draaien."
4. **Demomoment A.** Plak `demo/taken/01-helper-datums.md`: *"Voeg een helper toe om datums te parsen."*
   "De prompt vraagt om een nieuwe helper, maar kijk: de agent leest `AGENTS.md` en hergebruikt `parse_date`.
   Schrijft hij toch een eigen `strptime`, dan wordt de architectuurtest rood en herstelt hij zichzelf."
   (Terugval om de rode test te tonen: `git apply demo/taken/fouten/01-eigen-datumparser.patch`, daarna `make test`.)
5. `make reset`.
6. **Demomoment B.** `git apply demo/taken/fouten/02a-regressie-ontdubbeling.patch`, dan `make test`: "Een collega heeft de ontdubbeling weggehaald. Eén test rood."
   Plak `demo/taken/02-falende-test.md`: *"Maak de falende test groen."*
   "Dit is de valkuil. De snelste weg naar groen is de assert afzwakken."
   (Terugval: `git apply demo/taken/fouten/02b-afgezwakte-assert.patch`.)
7. `make test` (groen!), daarna `git diff --stat`: "Groen, maar kijk wat er veranderd is: de test, niet de code. Daarom staat in `AGENTS.md` dat dit niet mag. In review: altijd `tests/` in de diff checken."
8. `make reset`, daarna `make klaar N=1`: "In `-klaar` is taak 01 goed gedaan: `parse_date` hergebruikt, met nieuwe tests."

### Jij doet mee

```bash
make stap N=1
make test
git apply demo/taken/fouten/01-eigen-datumparser.patch
make test
make reset
git apply demo/taken/fouten/02a-regressie-ontdubbeling.patch
make test
git apply demo/taken/fouten/02b-afgezwakte-assert.patch
make test
git diff --stat
make reset
make klaar N=1
make test
```

### Verwacht resultaat

| Moment                           | `make test`                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| start                            | groen: `61 passed in 0.6s`                                                  |
| na `01-eigen-datumparser`        | rood: `1 failed, 60 passed`, namelijk `test_dates_are_only_parsed_in_utils_dates[model.py]`, met `model.py:16: return datetime.strptime(value, "%Y-%m-%d").date()` |
| na `02a-regressie-ontdubbeling`  | rood: `1 failed, 60 passed`, namelijk `test_duplicate_order_line_counts_once` |
| na `02b-afgezwakte-assert`       | groen: `61 passed`, maar `git diff --stat` toont `tests/unit/test_cleaning.py` |
| `demo/stap-1-klaar`              | groen: `67 passed in 0.7s`                                                  |

### Achter?

```bash
make reset && make klaar N=1
```

---

## Stap 2: integratietests (7:30 – 10:00)

**Doel:** een contracttest vangt wat unit tests niet zien: wat afnemers van je data verwachten. **Laag:** integratie (echte pipeline, DuckDB-bestand in een tijdelijke map, draait bij elke pull request).

### Ik laat zien

1. `make stap N=2`, open `tests/integration/test_contract.py`: "Het exacte schema van `daily_sales`, **uitgeschreven** en niet geïmporteerd. Zo beweegt de test niet mee als de code verandert."
2. Kort `tests/integration/data/sales_small.csv`: "Twintig regels die je met de hand kunt narekenen, inclusief rommel: een dubbele regel, een onbestaande datum, een retour."
3. `make test` en `make it`: allebei groen.
4. **Demomoment.** Zelfde taak als in stap 0: plak `demo/taken/03-hernoem-kolom.md`.
   (Terugval: `git apply demo/taken/fouten/03-hernoem-kolom.patch`.)
5. `make test`: "Unit tests: groen. Die testen logica, geen contracten."
6. `make it`: "Integratie: rood. Precies de fout die in stap 0 in productie was beland."
7. `make reset`, daarna `make klaar N=2` en open `AGENTS.md`: "De les staat nu vast: `daily_sales` is een contract. Een goede agent stopt en vraagt het eerst."

### Jij doet mee

```bash
make stap N=2
make test
make it
git apply demo/taken/fouten/03-hernoem-kolom.patch
make test
make it
make reset
make klaar N=2
```

### Verwacht resultaat

| Moment                 | `make test`          | `make it`                                  |
|------------------------|----------------------|--------------------------------------------|
| start                  | groen: `67 passed`   | groen: `7 passed in 0.2s`                  |
| na `03-hernoem-kolom`  | groen: `67 passed`   | rood: `4 failed, 3 passed`                 |
| `demo/stap-2-klaar`    | groen: `67 passed`   | groen: `7 passed`                          |

De kern van de rode contracttest:

```
E         At index 2 diff: ('customer_id', 'VARCHAR') != ('cust_id', 'VARCHAR')
FAILED tests/integration/test_contract.py::test_daily_sales_schema_is_exactly_the_contract
FAILED tests/integration/test_pipeline.py::test_dashboard_reads_daily_sales - _duckdb.BinderException…
```

### Achter?

```bash
make reset && make klaar N=2
```

---

## Stap 3: simulatie (10:00 – 13:00)

**Doel:** kleine rekenfouten vangen die pas opvallen bij realistische volumes. **Laag:** simulatie (één geseede synthetische dag met ~5.000 orderregels tegen `baseline.json`, draait 's nachts).

### Ik laat zien

1. `make stap N=3`, open `tests/simulation/test_replay.py`: "Seed 42, 15 dagen synthetische data, we spelen de laatste dag af: 4.951 orderregels. Dagomzet per winkel mag 0,1% afwijken, MAPE maximaal 1 punt slechter. De drempels staan in de test, niet in de baseline."
2. `make sim`: groen. "Op elke machine exact dezelfde getallen: vaste seed, en geld rekenen we in DECIMAL."
3. **Demomoment.** Plak `demo/taken/04-versnel-aggregatie.md`: *"Versnel de aggregatie."*
   (Terugval: `git apply demo/taken/fouten/04-versnelde-aggregatie.patch`.)
   "De agent telt eerst de aantallen op en vermenigvuldigt dan één keer per groep. Klinkt slim."
4. `make test` en `make it`: "Allebei groen. Onze fixtures hebben één regel per klant per dag, en dan is het toevallig gelijk."
5. `make sim`: "Rood: de dagomzet ligt 2,8% te hoog. Op een dashboard zie je dat nooit, in de jaarcijfers wel."
6. "En de oplossing is níet `make baseline`. Die is alleen voor bedoelde veranderingen, met verplichte reden."
7. `make reset`, daarna `make klaar N=3` en open `AGENTS.md`: "Nieuwe regel: raak je transform of model aan, draai dan `make sim`."

### Jij doet mee

```bash
make stap N=3
make sim
git apply demo/taken/fouten/04-versnelde-aggregatie.patch
make test
make it
make sim
make reset
make klaar N=3
```

### Verwacht resultaat

| Moment                          | `make test`        | `make it`         | `make sim`                        |
|---------------------------------|--------------------|-------------------|-----------------------------------|
| start                           | groen: `67 passed` | groen: `7 passed` | groen: `11 passed in 0.6s`        |
| na `04-versnelde-aggregatie`    | groen: `67 passed` | groen: `7 passed` | rood: `9 failed, 2 passed`        |
| `demo/stap-3-klaar`             | groen              | groen             | groen: `11 passed`                |

```
E   AssertionError: Dagomzet: EUR 175,746.69 wijkt 2.76% af van baseline EUR 171,027.28 (max 0.1%)
E   AssertionError: Dagomzet S06: EUR 33,894.78 wijkt 4.14% af van baseline EUR 32,548.19 (max 0.1%)
```

Groen blijven: dezelfde dag en hetzelfde volume, en de MAPE. Een voortschrijdend gemiddelde merkt weinig van een gelijkmatige verschuiving.
Juist daarom controleren we ook de totalen.

### Achter?

```bash
make reset && make klaar N=3
```

---

## Stap 4: vastleggen (13:00 – 14:30)

**Doel:** de piramide afdwingen, zodat het niet afhangt van iemands geheugen (of dat van een agent). **Laag:** geen nieuwe; we leggen de drie lagen vast.

### Ik laat zien

1. `make stap N=4`, open `.pre-commit-config.yaml`: "Bij elke commit: ruff en de unit tests. Alleen de snelle laag, anders zet niemand hem aan." (`make hooks` zet hem aan.)
2. Open `.github/workflows/tests.yml`: "Unit en integratie op elke pull request, als twee aparte checks." Daarna `simulation.yml`: "De simulatie 's nachts en met de hand."
3. `make klaar N=4`, open `AGENTS.md`: "Stack, Commando's, Architectuur, Regels, en het belangrijkste: **Klaar betekent `make test` en `make it` zijn groen.** Een agent kan zelf controleren of hij klaar is."
4. Open `docs/branch-protection.md`: "Maak `unit` en `integratie` verplicht op `main`. Dan komt er niets meer door met een rode test, van mens of agent."
5. `make all`: alles groen.

### Jij doet mee

```bash
make stap N=4
python -m pre_commit run --all-files
make klaar N=4
make all
```

### Verwacht resultaat

- `pre-commit run --all-files`: drie keer `Passed` (ruff check, ruff format, unit tests).
- `make all`: `All checks passed!`, daarna `67 passed`, `7 passed` en `11 passed`.

### Achter?

```bash
make reset && make klaar N=4
```

---

## Afsluiting (14:30 – 15:00)

```
                /\
               /  \              SIMULATIE    1 geseede dag (~5.000 regels) vs. baseline
              / 11 \             ± 1 s hier; met echte volumes minuten tot uren
             /------\            draait: 's nachts + handmatig (simulation.yml)
            /        \
           /    7     \          INTEGRATIE   echte pipeline, DuckDB-bestand, contracttest
          /            \         < 1 s
         /--------------\        draait: elke pull request, verplicht op main (tests.yml)
        /                \
       /        67        \      UNIT         in-memory, geparametriseerd, architectuurregels
      /                    \     < 1 s
     /______________________\    draait: bij elke wijziging + pre-commit

     aantal tests per laag       sneller en vaker naar onderen, realistischer naar boven
```

**Ik zeg:** "Elke laag vangt iets wat de laag eronder mist. Unit: logica en afspraken over de code. Integratie: contracten met afnemers.
Simulatie: rekenfouten die alleen op volume zichtbaar worden. En `AGENTS.md` vertelt de agent welke laag wanneer draait en wanneer hij klaar is."

### Huiswerk (optioneel)

Ontwerp de piramide voor je eigen project met `oefening/template-AGENTS.md`:
beantwoord per laag twee vragen (*wat moet deze laag vangen?* en *wanneer draait hij, en hoe snel?*) en zet de antwoorden om in regels voor `AGENTS.md`.
