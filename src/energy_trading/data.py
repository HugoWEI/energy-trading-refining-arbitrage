"""Load price series, track provenance, and prevent accidental mixing of units."""

from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = (
    "week_ending", "wti_cushing_usd_bbl", "brent_europe_usd_bbl",
    "gasoline_usgc_usd_gal", "ulsd_usgc_usd_gal"
)
EIA_SPOT_SERIES = {
    "wti_cushing_usd_bbl": "RWTC",
    "brent_europe_usd_bbl": "RBRTE",
    "gasoline_usgc_usd_gal": "EER_EPMRU_PF4_RGC_DPG",
    "ulsd_usgc_usd_gal": "EER_EPD2DXL0_PF4_RGC_DPG",
}
SNAPSHOT_SOURCE = "https://www.eia.gov/dnav/pet/pet_pri_spt_s1_w.htm"
DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "eia_weekly_snapshot_2026-10-09.csv"


def load_weekly_prices(path: str | Path = DEFAULT_PATH) -> pd.DataFrame:
    """Read consistent weekly-average EIA prices; reject missing and malformed observations."""
    df = pd.read_csv(path)
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns: {sorted(missing_columns)}")
    df = df[list(REQUIRED_COLUMNS)].copy()
    df["week_ending"] = pd.to_datetime(df["week_ending"], errors="raise")
    for col in REQUIRED_COLUMNS[1:]:
        df[col] = pd.to_numeric(df[col], errors="raise")
        if df[col].isna().any() or (df[col] <= 0).any():
            raise ValueError(f"Series {col} contains missing or non-positive prices")
    if df["week_ending"].isna().any() or df["week_ending"].duplicated().any():
        raise ValueError("Dates must be valid and unique")
    return df.sort_values("week_ending").reset_index(drop=True)
