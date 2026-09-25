# Testpiramide-demo

Live demo: hoe unit-, integratie- en simulatietests (plus een goede `AGENTS.md`) een
AI-agent op het rechte pad houden in data- en ML-code. Je doet mee in je eigen fork.

De code is een kleine verkooppijplijn in Python 3.12 met DuckDB (ingest → transform → model).
Er is geen echte data: alles is synthetisch en geseed, dus iedereen krijgt dezelfde uitkomsten.

## 1. Fork de repo

Klik rechtsboven op **Fork**, en dan:

> ⚠️ **Vink "Copy the main branch only" UIT.** De demo gebruikt branches per stap
> (`demo/stap-0-start`, `demo/stap-1-unit`, ...). Die heb je allemaal nodig.

Klik op **Create fork**.

## 2. Open je fork

**Codespace (aanbevolen, niets te installeren):** in je fork op **Code → Codespaces →
Create codespace on main**. Alles wordt automatisch geïnstalleerd (`.devcontainer/`).

**Lokaal in VS Code:** je hebt Python 3.12, git en `make` nodig (op Windows: gebruik WSL of een Codespace).

```bash
git clone https://github.com/<jouw-naam>/testpiramide-demo.git
cd testpiramide-demo
python3.12 -m venv .venv && source .venv/bin/activate
make setup
```

## 3. Start

```bash
make stap N=0
```

Volg daarna de presentator. Kopieer de commando's uit de blokken "Jij doet mee".

## Stappen

| Stap | Laag                  | Branch (start → klaar)                             | Commando                          |
|------|-----------------------|----------------------------------------------------|-----------------------------------|
| 0    | geen tests (probleem) | `demo/stap-0-start`                                | `make stap N=0`                   |
| 1    | unit                  | `demo/stap-1-unit` → `demo/stap-1-klaar`           | `make stap N=1` / `make klaar N=1` |
| 2    | integratie            | `demo/stap-2-integratie` → `demo/stap-2-klaar`     | `make stap N=2` / `make klaar N=2` |
| 3    | simulatie             | `demo/stap-3-simulatie` → `demo/stap-3-klaar`      | `make stap N=3` / `make klaar N=3` |
| 4    | vastleggen            | `demo/stap-4-vastleggen` → `demo/stap-4-klaar`     | `make stap N=4` / `make klaar N=4` |

`main` is het eindresultaat (gelijk aan `demo/stap-4-klaar`).

## Handig tijdens de demo

| Commando          | Wat het doet                                                   |
|-------------------|----------------------------------------------------------------|
| `make klaar N=2`  | **Achter?** Spring naar het eindresultaat van stap 2           |
| `make reset`      | Gooi je wijzigingen weg (toegepaste patch, werk van je agent)  |
| `make help`       | Alle commando's die in deze stap bestaan                       |
| `make test` / `make it` / `make sim` | unit / integratie / simulatie (vanaf stap 1 / 2 / 3) |

## Meer

- [DEMO.md](DEMO.md): het volledige draaiboek, met verwachte uitkomsten per stap
- [demo/taken/](demo/taken/): de prompts voor je agent, en in [fouten/](demo/taken/fouten/) de patches als terugvaloptie
- [oefening/template-AGENTS.md](oefening/template-AGENTS.md): huiswerk, ontwerp de piramide voor je eigen project
