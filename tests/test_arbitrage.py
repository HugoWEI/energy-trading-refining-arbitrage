import pytest
from energy_trading.arbitrage import (
    CargoAssumptions, indicative_margin_usd_bbl, breakeven_brent_usd_bbl, scenario_grid
)


def test_no_cost():
    a = CargoAssumptions(0, 0, 0, 0, 0, 0, 0)
    assert indicative_margin_usd_bbl(90, 100, a) == pytest.approx(10)
    assert breakeven_brent_usd_bbl(90, a) == pytest.approx(90)


def test_costs_loss_and_breakeven():
    a = CargoAssumptions(1, 2, 3, 1, 1, 2, 1)
    assert indicative_margin_usd_bbl(70, 100, a) == pytest.approx(19)
    assert indicative_margin_usd_bbl(70, breakeven_brent_usd_bbl(70, a), a) == pytest.approx(0)


def test_spread_and_freight_sensitivity():
    grid = scenario_grid(90, 100, CargoAssumptions(), [-5, 0, 5], [0, 2])
    assert len(grid) == 6
    assert grid.iloc[0]["Illustrative margin ($/bbl)"] < grid.iloc[2]["Illustrative margin ($/bbl)"]
    assert grid.iloc[3]["Illustrative margin ($/bbl)"] < grid.iloc[0]["Illustrative margin ($/bbl)"]


def test_invalid_assumptions():
    with pytest.raises(ValueError):
        CargoAssumptions(marine_freight=-1)
    with pytest.raises(ValueError):
        CargoAssumptions(volume_loss_pct=100)
