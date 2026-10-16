from unittest.mock import MagicMock, patch
import pytest
from energy_trading.eia import fetch_eia_series


def test_missing_key():
    with pytest.raises(ValueError, match="EIA_API_KEY"):
        fetch_eia_series("RWTC", "", "2026-01-01", "2026-12-31")


def test_parses_eia_payload():
    response = MagicMock()
    response.json.return_value = {"response": {"data": [
        {"series": "RWTC", "period": "2026-10-01", "value": "100.5"},
        {"series": "RWTC", "period": "2026-10-02", "value": "101.0"},
    ]}}
    with patch("energy_trading.eia.requests.get", return_value=response) as getter:
        frame = fetch_eia_series("RWTC", "test-only-key", "2026-10-01", "2026-10-02")
    assert len(frame) == 2
    assert frame.iloc[0]["value"] == pytest.approx(100.5)
    assert getter.call_args.kwargs["timeout"] == 30


def test_api_error_no_synthetic_fallback():
    response = MagicMock()
    response.json.return_value = {"error": "Invalid request"}
    with patch("energy_trading.eia.requests.get", return_value=response):
        with pytest.raises(RuntimeError, match="error"):
            fetch_eia_series("RWTC", "test-only-key", "2026-01-01", "2026-12-31")
