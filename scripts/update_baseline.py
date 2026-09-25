"""Werk tests/simulation/baseline.json bij.

Doe dit alleen als een verandering in de uitkomst BEDOELD is (bijv. een beter
model), nooit om een rode simulatietest groen te krijgen. De reden is verplicht
en komt in de baseline te staan, zodat de review hem ziet.

Gebruik:  make baseline REDEN="nieuw model met weekseizoen"
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from tests.simulation.replay import run_replay  # noqa: E402

BASELINE_PATH = ROOT / "tests" / "simulation" / "baseline.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reden", required=True, help="waarom de uitkomst bedoeld verandert")
    args = parser.parse_args()
    if not args.reden.strip():
        parser.error("--reden mag niet leeg zijn")

    with tempfile.TemporaryDirectory() as tmp:
        new = run_replay(Path(tmp))
    new["reason"] = args.reden.strip()

    if BASELINE_PATH.exists():
        old = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        for key in ("replay_date", "order_lines", "total_eur", "mape_pct"):
            marker = "" if old.get(key) == new[key] else "   <-- veranderd"
            print(f"{key:<12} {old.get(key)!s:>12} -> {new[key]!s:<12}{marker}")

    BASELINE_PATH.write_text(json.dumps(new, indent=2) + "\n", encoding="utf-8")
    print(f"Baseline geschreven: {BASELINE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
