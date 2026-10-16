"""Hypothetical transatlantic crude differential sensitivity.

IMPORTANT: Brent Europe spot and WTI Cushing spot are NOT simultaneously
executable US Gulf Coast FOB / Rotterdam CIF cargo quotes. This is a
structural screening framework, not an arbitrage backtest or P&L estimate.
"""
from dataclasses import dataclass, replace
import pandas as pd


@dataclass(frozen=True)
class CargoAssumptions:
    """User-editable illustrative $/bbl cost assumptions, NOT observed freight quotes."""
    cushing_to_gulf: float = 3.50
    marine_freight: float = 3.75
    terminal_handling: float = 1.50
    insurance: float = 0.45
    financing: float = 0.35
    grade_basis_adjustment: float = 4.00
    volume_loss_pct: float = 0.50

    def __post_init__(self):
        costs = [self.cushing_to_gulf, self.marine_freight, self.terminal_handling,
                 self.insurance, self.financing]
        if any(v < 0 for v in costs):
            raise ValueError("Actual costs cannot be negative")
        if not (0 <= self.volume_loss_pct < 100):
            raise ValueError("Volume loss must be a percentage in [0,100)")

    @property
    def non_crude_costs(self) -> float:
        return sum((self.cushing_to_gulf, self.marine_freight,
                    self.terminal_handling, self.insurance, self.financing,
                    self.grade_basis_adjustment))


def indicative_margin_usd_bbl(
    wti_cushing: float, brent_europe: float, assumptions: CargoAssumptions
) -> float:
    """Screening differential; does not constitute a physical tradable price."""
    arrival_proceeds = float(brent_europe) * (1 - assumptions.volume_loss_pct / 100)
    return arrival_proceeds - float(wti_cushing) - assumptions.non_crude_costs


def scenario_grid(
    wti: float, brent: float, assumptions: CargoAssumptions,
    spread_shocks: list[float] | None = None,
    freight_shocks: list[float] | None = None,
) -> pd.DataFrame:
    """Returns a grid varying Brent relative to base and freight relative to base.

    Shock +x means Brent moves +$x while WTI stays at the observed proxy.
    """
    spread_shocks = spread_shocks or [-15, -10, -5, 0, 5, 10, 15]
    freight_shocks = freight_shocks or [-2, 0, 2, 4, 6]
    result = []
    for freight_change in freight_shocks:
        freight = max(0, assumptions.marine_freight + freight_change)
        costs = replace(assumptions, marine_freight=freight)
        for spread_change in spread_shocks:
            margin = indicative_margin_usd_bbl(wti, brent + spread_change, costs)
            result.append({"Freight shock ($/bbl)": freight_change,
                           "Brent shock ($/bbl)": spread_change,
                           "Illustrative margin ($/bbl)": margin})
    return pd.DataFrame(result)


def breakeven_brent_usd_bbl(wti: float, assumptions: CargoAssumptions) -> float:
    factor = 1 - assumptions.volume_loss_pct / 100
    return (float(wti) + assumptions.non_crude_costs) / factor
