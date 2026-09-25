# Oefening: ontwerp je eigen testpiramide

Neem je eigen project in gedachten. Beantwoord per laag twee vragen en zet de
antwoorden daarna om in regels voor `AGENTS.md`. Reken op een kwartier.

## 1. Beantwoord per laag twee vragen

| Laag        | Vraag 1: wat moet deze laag vangen?                  | Vraag 2: wanneer draait hij, en hoe snel moet hij zijn? |
|-------------|------------------------------------------------------|----------------------------------------------------------|
| Unit        | Welke regels en rekenstappen mogen nooit stuk? (bijv. opschonen, datums, features) | Bij elke wijziging; < 1 minuut |
| Integratie  | Welke contracten heb je met afnemers of bronnen? (schema's, tabellen, API's) | Bij elke pull request; < 5 minuten |
| Simulatie   | Welke uitkomst moet stabiel blijven op realistische data? (totalen, metrics) | 's Nachts of met de hand; mag langer duren |

Mijn antwoorden:

- **Unit:** ...
  - draait: ...
- **Integratie:** ...
  - draait: ...
- **Simulatie:** ...
  - draait: ...

## 2. Zet het om in AGENTS.md

Kopieer het blok hieronder naar `AGENTS.md` in je eigen repo en vul het in.
Tip: elke regel die je opschrijft, verdient ook een test die hem bewaakt.

```markdown
# AGENTS.md

## Stack

- Taal, versie, belangrijkste libraries: ...
- Data: waar komt het vandaan, is er synthetische/geseede testdata? ...

## Commando's

- `...`: unit tests. Draai ze na elke wijziging.
- `...`: integratietests. Draai ze voordat je zegt dat je klaar bent.
- `...`: simulatie/regressie op realistische data. Draai ze als je <kernmodules> wijzigt.

## Architectuur

- <map/module>: <verantwoordelijkheid>
- Eén plek voor <gedeelde logica, bijv. datums/valuta/ID's>: <module>

## Regels

- <Gedeelde logica> gaat altijd via <module>; schrijf geen eigen variant.
- Een falende test repareer je in de code, niet in de test. Geen asserts afzwakken,
  geen skip/xfail. Denk je dat de test fout is? Stop en leg uit waarom.
- <Tabel/API> is een contract met <afnemers>. Niet hernoemen of verwijderen zonder te vragen.
- Wijzig je <kernmodules>, draai dan ook <simulatie>. Baselines werk je alleen bij als
  de gebruiker erom vraagt, met een reden.

## Klaar betekent

`<unit-commando>` en `<integratie-commando>` zijn groen.
```

## 3. Controleer jezelf

- [ ] Elke laag heeft één commando dat een agent kan draaien.
- [ ] De snelste laag draait in minder dan een minuut.
- [ ] Elke regel in "Regels" wordt door minstens één test bewaakt.
- [ ] "Klaar betekent" is objectief: een agent kan zelf zien of het zo is.
