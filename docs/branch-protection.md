# Checks verplicht maken op `main`

De workflow `.github/workflows/tests.yml` draait twee jobs op elke pull request:
**unit** en **integratie**. Pas als je ze verplicht maakt, kan niemand (mens of agent)
meer iets op `main` krijgen met een rode test.

> Een check verschijnt pas in de keuzelijst nadat hij één keer heeft gedraaid.
> Open dus eerst een pull request (of push naar `main`) en wacht tot beide jobs klaar zijn.

## Via de website (ruleset, aanbevolen)

1. Ga naar je repo, dan **Settings → Rules → Rulesets → New ruleset → New branch ruleset**.
2. **Ruleset name**: `main beschermen`. **Enforcement status**: *Active*.
3. **Target branches → Add target → Include default branch**.
4. Vink aan:
   - **Restrict deletions**
   - **Block force pushes**
   - **Require a pull request before merging** (reviews mag je op 0 laten voor de demo)
   - **Require status checks to pass**, dan **Add checks** en kies `unit` en `integratie`.
     Vink ook **Require branches to be up to date before merging** aan.
5. **Create**.

Liever de klassieke manier? **Settings → Branches → Add branch protection rule**,
branch name pattern `main`, **Require status checks to pass before merging**, en
zoek `unit` en `integratie` op.

## Via de command line (gh)

```bash
gh api -X PUT "repos/{owner}/{repo}/branches/main/protection" \
  --input - <<'EOF'
{
  "required_status_checks": { "strict": true, "contexts": ["unit", "integratie"] },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
EOF
```

`gh` vult `{owner}/{repo}` zelf in als je in de repo-map staat.

## Waarom de simulatie níet verplicht is

`simulation.yml` draait 's nachts en is met de hand te starten (**Actions → simulation →
Run workflow**). In deze demo duurt hij een paar seconden, maar met echte volumes wordt
dat al snel minuten tot uren. Dat is te traag voor elke pull request. Wordt de nachtrun
rood, dan maak je een issue aan en heeft dat voorrang op nieuw werk.

Samengevat:

| Laag       | Workflow         | Wanneer                   | Verplicht op `main`? |
|------------|------------------|---------------------------|----------------------|
| unit       | `tests.yml`      | elke PR + pre-commit lokaal | ja                 |
| integratie | `tests.yml`      | elke PR                   | ja                   |
| simulatie  | `simulation.yml` | elke nacht + handmatig    | nee, maar rood = eerst fixen |
