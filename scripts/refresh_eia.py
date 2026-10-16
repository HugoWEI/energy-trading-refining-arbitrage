"""Convenience wrapper. Set EIA_API_KEY in environment before running."""
from energy_trading.eia import export_weekly_csv

if __name__ == "__main__":
    print(export_weekly_csv("data/eia_weekly_live.csv"))
