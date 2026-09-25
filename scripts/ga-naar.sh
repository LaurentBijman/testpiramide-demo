#!/bin/sh
# Wissel naar een demo-branch. Wordt aangeroepen door `make stap N=..` en `make klaar N=..`.
set -eu

soort="${1:-}"  # stap | klaar
n="${2:-}"

case "$soort:$n" in
  stap:0) branch=demo/stap-0-start ;;
  stap:1) branch=demo/stap-1-unit ;;
  stap:2) branch=demo/stap-2-integratie ;;
  stap:3) branch=demo/stap-3-simulatie ;;
  stap:4) branch=demo/stap-4-vastleggen ;;
  klaar:1 | klaar:2 | klaar:3 | klaar:4) branch="demo/stap-$n-klaar" ;;
  klaar:0)
    echo "Stap 0 heeft geen klaar-branch. Ga verder met: make stap N=1"
    exit 1
    ;;
  *)
    echo "Gebruik: make stap N=0..4   of   make klaar N=1..4"
    exit 1
    ;;
esac

if [ -n "$(git status --porcelain)" ]; then
  echo ""
  echo "  Je hebt nog lokale wijzigingen (een toegepaste patch of werk van je agent):"
  echo ""
  git status --short | sed 's/^/      /'
  echo ""
  echo "  Geen probleem. Kies:"
  echo "    make reset                       gooi ze weg (aanbevolen tijdens de demo)"
  echo "    git stash --include-untracked    of bewaar ze voor later"
  echo ""
  echo "  en daarna opnieuw: make $soort N=$n"
  echo ""
  exit 1
fi

bestaat() {
  git rev-parse --verify --quiet "refs/heads/$branch" >/dev/null ||
    git rev-parse --verify --quiet "refs/remotes/origin/$branch" >/dev/null
}

if ! bestaat; then
  git fetch --quiet origin 2>/dev/null || true
fi
if ! bestaat; then
  echo ""
  echo "  Branch $branch niet gevonden."
  echo "  Heb je bij het forken 'Copy the main branch only' uitgevinkt? Zo niet, fork dan"
  echo "  opnieuw (zie README) of haal de branches op uit de originele repo:"
  echo ""
  echo "    git remote add upstream <url-van-de-originele-repo>"
  echo "    git fetch upstream"
  echo "    git checkout -b $branch upstream/$branch"
  echo ""
  exit 1
fi

git checkout --quiet "$branch"
echo "Je staat nu op $branch"
