import pandas as pd

from forex_signal_bot.config import load_settings
from forex_signal_bot.indicators import add_indicators
from forex_signal_bot.signal_engine import evaluate_signal


def test_signal_engine_returns_valid_direction():
    periods = 260
    index = pd.date_range("2026-01-01", periods=periods, freq="1H", tz="UTC")
    closes = pd.Series([1.0 + i * 0.001 for i in range(periods)], index=index)

    df = pd.DataFrame(
        {
            "open": closes.shift(1).fillna(closes.iloc[0]),
            "high": closes + 0.002,
            "low": closes - 0.002,
            "close": closes,
        },
        index=index,
    )

    settings = load_settings()
    enriched = add_indicators(df, breakout_lookback=settings.breakout_lookback)
    signal = evaluate_signal("EUR/USD", "1h", enriched, settings)

    assert signal.direction.value in {"BUY", "SELL", "NO SIGNAL"}
    assert signal.pair == "EUR/USD"
    assert signal.timeframe == "1h"
