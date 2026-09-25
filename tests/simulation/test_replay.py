"""Simulatie: vergelijk een afgespeelde synthetische dag met baseline.json.

Vangt wat unit- en integratietests missen: kleine rekenverschillen die pas
opvallen bij realistische volumes (duizenden regels, meerdere regels per klant).

De drempels staan hier en niet in baseline.json: de baseline bijwerken
(make baseline) mag de lat dus nooit stilletjes lager leggen.
"""

import json
from pathlib import Path

import pytest

from sales_forecast.synthetic import STORES
from tests.simulation.replay import run_replay

pytestmark = pytest.mark.simulation

BASELINE_PATH = Path(__file__).with_name("baseline.json")
TOTAL_TOLERANCE = 0.001  # dagomzet mag maximaal 0,1% afwijken
MAPE_TOLERANCE_POINTS = 1.0  # MAPE mag maximaal 1 procentpunt slechter worden


@pytest.fixture(scope="module")
def baseline():
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def replay(tmp_path_factory):
    return run_replay(tmp_path_factory.mktemp("replay"))


def assert_within_tolerance(actual: float, expected: float, label: str) -> None:
    deviation = abs(actual - expected) / expected
    assert deviation <= TOTAL_TOLERANCE, (
        f"{label}: EUR {actual:,.2f} wijkt {deviation:.2%} af van baseline EUR {expected:,.2f} "
        f"(max {TOTAL_TOLERANCE:.1%})"
    )


def test_replays_the_same_day_and_volume(replay, baseline):
    assert replay["replay_date"] == baseline["replay_date"]
    assert replay["order_lines"] == baseline["order_lines"]


def test_daily_total_within_tolerance(replay, baseline):
    assert_within_tolerance(replay["total_eur"], baseline["total_eur"], "Dagomzet")


@pytest.mark.parametrize("store_id", sorted(STORES))
def test_store_total_within_tolerance(replay, baseline, store_id):
    assert_within_tolerance(
        replay["store_totals_eur"][store_id],
        baseline["store_totals_eur"][store_id],
        f"Dagomzet {store_id}",
    )


def test_forecast_error_not_worse_than_baseline(replay, baseline):
    limit = baseline["mape_pct"] + MAPE_TOLERANCE_POINTS
    assert replay["mape_pct"] <= limit, (
        f"MAPE {replay['mape_pct']:.2f}% is slechter dan baseline "
        f"{baseline['mape_pct']:.2f}% + {MAPE_TOLERANCE_POINTS} punt"
    )
