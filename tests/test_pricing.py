import pandas as pd
import pytest
from energy_trading.data import load_weekly_prices
from energy_trading.pricing import (
    GALLONS_PER_BARREL, crack_321_usd_per_barrel, add_crack_metrics, crack_decomposition
)


def test_unit_conversion():
    assert GALLONS_PER_BARREL == 42
    assert crack_321_usd_per_barrel(60, 2, 2) == pytest.approx(24)


def test_official_eia_snapshot():
    df = add_crack_metrics(load_weekly_prices())
    assert len(df) == 6
    assert str(df.iloc[-1]["week_ending"].date()) == "2026-10-09"
    row = df.iloc[-1]
    expected = (42 * (2 * 3.513 + 4.640) - 3 * 96.88) / 3
    assert row["crack_321_usd_bbl"] == pytest.approx(expected)
    assert row["brent_wti_spread_usd_bbl"] == pytest.approx(30.55)


def test_arithmetic_decomposition():
    df = add_crack_metrics(load_weekly_prices())
    parts = crack_decomposition(df.iloc[-2], df.iloc[-1])
    assert sum(parts.values()) == pytest.approx(
        df.iloc[-1]["crack_321_usd_bbl"] - df.iloc[-2]["crack_321_usd_bbl"]
    )


def test_missing_columns_rejected(tmp_path):
    file = tmp_path / "bad.csv"
    file.write_text("week_ending,wti_cushing_usd_bbl\n2026-01-01,10\n")
    with pytest.raises(ValueError, match="Missing columns"):
        load_weekly_prices(file)


def test_duplicate_dates_rejected(tmp_path):
    df = load_weekly_prices()
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    file = tmp_path / "duplicate.csv"
    df.to_csv(file, index=False)
    with pytest.raises(ValueError, match="unique"):
        load_weekly_prices(file)
