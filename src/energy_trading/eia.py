"""Fetch EIA daily spot observations and average completed Friday-ending weeks.

Requires a free EIA_API_KEY in the environment. No synthetic fallback prices.
"""
from datetime import date, timedelta
from pathlib import Path
import os
import pandas as pd
import requests
from energy_trading.data import EIA_SPOT_SERIES, REQUIRED_COLUMNS

EIA_ENDPOINT = "https://api.eia.gov/v2/petroleum/pri/spt/data/"


def fetch_eia_series(series: str, api_key: str, start: str, end: str) -> pd.DataFrame:
    if not api_key:
        raise ValueError("Set EIA_API_KEY; EIA requires a free API key")
    params = {
        "api_key": api_key, "frequency": "daily", "data[0]": "value",
        "facets[series][]": series, "start": start, "end": end,
        "sort[0][column]": "period", "sort[0][direction]": "asc",
        "length": "5000",
    }
    response = requests.get(EIA_ENDPOINT, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"EIA returned an error for {series}: {payload['error']}")
    records = payload.get("response", {}).get("data", [])
    if not records:
        raise ValueError(f"EIA returned no data for {series}")
    df = pd.DataFrame.from_records(records)
    required = {"period", "value", "series"}
    if not required.issubset(df.columns):
        raise ValueError(f"Unexpected EIA response fields for {series}: {list(df.columns)}")
    df = df[df["series"] == series].copy()
    df["date"] = pd.to_datetime(df["period"], errors="raise")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    if df.empty:
        raise ValueError(f"No numeric EIA data for {series}")
    return df[["date", "value"]].drop_duplicates("date").sort_values("date")


def fetch_completed_weekly_prices(
    api_key: str | None = None, lookback_days: int = 365, today: date | None = None
) -> pd.DataFrame:
    """Unweighted daily-close mean per complete Friday-ending calendar week."""
    api_key = api_key or os.getenv("EIA_API_KEY", "")
    today = today or date.today()
    start = (today - timedelta(days=lookback_days)).isoformat()
    end = today.isoformat()
    result = []
    for column, series in EIA_SPOT_SERIES.items():
        df = fetch_eia_series(series, api_key, start, end)
        weekly = df.set_index("date")["value"].resample("W-FRI").agg(
            ["mean", "count"]
        ).reset_index()
        weekly = weekly[(weekly["count"] >= 3) &
                        (weekly["date"].dt.date <= today)][["date", "mean"]]
        weekly.columns = ["week_ending", column]
        result.append(weekly)
    result_df = result[0]
    for frame in result[1:]:
        result_df = result_df.merge(frame, on="week_ending", how="inner", validate="one_to_one")
    if result_df.empty:
        raise ValueError("No overlapping completed weeks")
    return result_df[list(REQUIRED_COLUMNS)].sort_values("week_ending").reset_index(drop=True)


def export_weekly_csv(dest: str | Path, **kwargs) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fetch_completed_weekly_prices(**kwargs).to_csv(dest, index=False, date_format="%Y-%m-%d")
    return dest
