from __future__ import annotations

import math
from typing import Literal


def round_price(price: float, digits: int = 5) -> float:
    return round(price, digits)


def infer_digits(pair: str) -> int:
    return 3 if pair.endswith("JPY") else 5


def build_trade_plan(
    pair: str,
    direction: Literal["BUY", "SELL"],
    entry_price: float,
    support: float,
    resistance: float,
    risk_reward_ratio: float,
) -> tuple[float, float]:
    digits = infer_digits(pair)

    if direction == "BUY":
        stop_loss = min(support, entry_price) if support else entry_price * 0.998
        risk_distance = max(entry_price - stop_loss, entry_price * 0.001)
        take_profit = entry_price + risk_distance * risk_reward_ratio
    else:
        stop_loss = max(resistance, entry_price) if resistance else entry_price * 1.002
        risk_distance = max(stop_loss - entry_price, entry_price * 0.001)
        take_profit = entry_price - risk_distance * risk_reward_ratio

    return round_price(stop_loss, digits), round_price(take_profit, digits)
