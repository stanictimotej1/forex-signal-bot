from __future__ import annotations

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD


def add_indicators(df: pd.DataFrame, breakout_lookback: int = 20) -> pd.DataFrame:
    enriched = df.copy()

    enriched["ema_50"] = EMAIndicator(close=enriched["close"], window=50).ema_indicator()
    enriched["ema_200"] = EMAIndicator(close=enriched["close"], window=200).ema_indicator()
    enriched["rsi"] = RSIIndicator(close=enriched["close"], window=14).rsi()

    macd = MACD(close=enriched["close"], window_slow=26, window_fast=12, window_sign=9)
    enriched["macd"] = macd.macd()
    enriched["macd_signal"] = macd.macd_signal()
    enriched["macd_hist"] = macd.macd_diff()

    enriched["support"] = enriched["low"].rolling(window=breakout_lookback).min()
    enriched["resistance"] = enriched["high"].rolling(window=breakout_lookback).max()

    enriched["breakout_up"] = enriched["close"] > enriched["resistance"].shift(1)
    enriched["breakout_down"] = enriched["close"] < enriched["support"].shift(1)

    return enriched.dropna().copy()
