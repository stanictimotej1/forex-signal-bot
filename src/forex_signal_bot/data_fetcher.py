from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import requests

from .config import Settings


class DataFetcher:
    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self.settings = settings
        self.logger = logger
        self.session = requests.Session()

    def fetch(self, pair: str, timeframe: str) -> pd.DataFrame:
        provider = self.settings.data_provider.lower()
        if provider != "alpha_vantage":
            raise ValueError(f"Unsupported data provider: {provider}")
        return self._fetch_alpha_vantage(pair, timeframe)

    def _fetch_alpha_vantage(self, pair: str, timeframe: str) -> pd.DataFrame:
        from_symbol, to_symbol = pair.split("/")
        timeframe = timeframe.lower()

        if not self.settings.alpha_vantage_api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY is missing in environment variables.")

        if timeframe == "15min":
            data = self._fetch_fx_intraday(from_symbol, to_symbol, "15min")
        elif timeframe == "1h":
            data = self._fetch_fx_intraday(from_symbol, to_symbol, "60min")
        elif timeframe == "4h":
            base_df = self._fetch_fx_intraday(from_symbol, to_symbol, "60min")
            data = (
                base_df.resample("4H")
                .agg(
                    {
                        "open": "first",
                        "high": "max",
                        "low": "min",
                        "close": "last",
                    }
                )
                .dropna()
            )
        else:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        data = data.tail(self.settings.candle_limit).copy()
        if len(data) < 220:
            raise ValueError(
                f"Insufficient candles for {pair} {timeframe}. Need at least 220, got {len(data)}."
            )
        return data

    def _fetch_fx_intraday(self, from_symbol: str, to_symbol: str, interval: str) -> pd.DataFrame:
        params: dict[str, Any] = {
            "function": "FX_INTRADAY",
            "from_symbol": from_symbol,
            "to_symbol": to_symbol,
            "interval": interval,
            "outputsize": "full",
            "apikey": self.settings.alpha_vantage_api_key,
        }

        response = self.session.get(
            self.settings.alpha_vantage_base_url,
            params=params,
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()

        if "Note" in payload:
            raise RuntimeError(f"Alpha Vantage rate limit or note received: {payload['Note']}")
        if "Information" in payload:
            raise RuntimeError(f"Alpha Vantage information response: {payload['Information']}")
        if "Error Message" in payload:
            raise RuntimeError(f"Alpha Vantage error: {payload['Error Message']}")

        ts_key = next((key for key in payload.keys() if "Time Series FX" in key), None)
        if not ts_key:
            raise RuntimeError(f"Unexpected Alpha Vantage response keys: {list(payload.keys())}")

        raw = payload[ts_key]
        df = pd.DataFrame.from_dict(raw, orient="index")
        df.index = pd.to_datetime(df.index, utc=True)
        df = df.sort_index()
        df = df.rename(
            columns={
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
            }
        )
        for col in ["open", "high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna()
        return df
