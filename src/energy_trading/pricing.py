"""Unit-consistent economic indicators; not actual tradeable refinery margins."""
import pandas as pd

GALLONS_PER_BARREL = 42.0  # US gallons per petroleum barrel


def us_gallons_to_usd_per_barrel(usd_per_gallon: float) -> float:
    return float(usd_per_gallon) * GALLONS_PER_BARREL


def crack_321_usd_per_barrel(
    crude_usd_bbl: float, gasoline_usd_gal: float, diesel_usd_gal: float
) -> float:
    """Three crude barrels -> two gasoline and one diesel, gross theoretical proxy.

    No refinery yield, losses, energy, freight, marketing, capex or tax adjustment.
    Gulf Coast products vs Cushing WTI include geographical/crude-grade basis.
    """
    g = us_gallons_to_usd_per_barrel(gasoline_usd_gal)
    d = us_gallons_to_usd_per_barrel(diesel_usd_gal)
    return (2 * g + d - 3 * float(crude_usd_bbl)) / 3


def add_crack_metrics(prices: pd.DataFrame) -> pd.DataFrame:
    prices = prices.copy().sort_values("week_ending").reset_index(drop=True)
    prices["gasoline_usgc_usd_bbl"] = prices["gasoline_usgc_usd_gal"] * 42
    prices["diesel_usgc_usd_bbl"] = prices["ulsd_usgc_usd_gal"] * 42
    prices["crack_321_usd_bbl"] = (
        2 * prices["gasoline_usgc_usd_bbl"]
        + prices["diesel_usgc_usd_bbl"]
        - 3 * prices["wti_cushing_usd_bbl"]
    ) / 3
    prices["brent_wti_spread_usd_bbl"] = (
        prices["brent_europe_usd_bbl"] - prices["wti_cushing_usd_bbl"]
    )
    prices["crack_wow_usd_bbl"] = prices["crack_321_usd_bbl"].diff()
    return prices


def crack_decomposition(previous: pd.Series, current: pd.Series) -> dict[str, float]:
    """Exact week-on-week changes by factor; contributions sum to delta-crack."""
    crude = -(float(current["wti_cushing_usd_bbl"]) - float(previous["wti_cushing_usd_bbl"]))
    gasoline = 2 * 42 / 3 * (
        float(current["gasoline_usgc_usd_gal"]) - float(previous["gasoline_usgc_usd_gal"])
    )
    diesel = 42 / 3 * (
        float(current["ulsd_usgc_usd_gal"]) - float(previous["ulsd_usgc_usd_gal"])
    )
    return {"Crude input": crude, "Gasoline output": gasoline, "Diesel output": diesel}
