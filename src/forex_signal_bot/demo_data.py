from __future__ import annotations

import numpy as np
import pandas as pd


def generate_demo_ohlc(periods: int = 350, freq: str = "1H", seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    index = pd.date_range(end=pd.Timestamp.utcnow(), periods=periods, freq=freq, tz="UTC")

    base = 1.10 + np.cumsum(rng.normal(0, 0.001, size=periods))
    close = pd.Series(base, index=index)
    open_ = close.shift(1).fillna(close.iloc[0])
    high = np.maximum(open_, close) + np.abs(rng.normal(0.0007, 0.0003, size=periods))
    low = np.minimum(open_, close) - np.abs(rng.normal(0.0007, 0.0003, size=periods))

    return pd.DataFrame(
        {
            "open": open_.astype(float),
            "high": pd.Series(high, index=index).astype(float),
            "low": pd.Series(low, index=index).astype(float),
            "close": close.astype(float),
        },
        index=index,
    )
