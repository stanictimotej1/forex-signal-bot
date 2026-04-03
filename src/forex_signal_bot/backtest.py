from __future__ import annotations

import logging

import pandas as pd

from .config import Settings
from .demo_data import generate_demo_ohlc
from .indicators import add_indicators
from .signal_engine import evaluate_signal


def run_demo_backtest(settings: Settings, logger: logging.Logger) -> None:
    logger.info("Starting demo backtest mode.")

    for pair in settings.forex_pairs:
        for timeframe in settings.timeframes:
            freq = "15min" if timeframe == "15min" else "1H"
            raw = generate_demo_ohlc(periods=max(settings.candle_limit, 350), freq=freq)
            if timeframe == "4h":
                raw = (
                    raw.resample("4H")
                    .agg({"open": "first", "high": "max", "low": "min", "close": "last"})
                    .dropna()
                )

            enriched = add_indicators(raw, breakout_lookback=settings.breakout_lookback)
            recent = enriched.tail(60)

            actionables = 0
            for i in range(220, len(recent)):
                window = recent.iloc[: i + 1]
                result = evaluate_signal(pair, timeframe, window, settings)
                if result.is_actionable():
                    actionables += 1

            logger.info(
                "Backtest summary | pair=%s | timeframe=%s | actionable_signals=%s | candles=%s",
                pair,
                timeframe,
                actionables,
                len(recent),
            )
