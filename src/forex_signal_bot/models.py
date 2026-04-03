from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class SignalDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    NO_SIGNAL = "NO SIGNAL"


@dataclass(slots=True)
class MarketSnapshot:
    pair: str
    timeframe: str
    timestamp: datetime
    close: float
    ema_50: float
    ema_200: float
    rsi: float
    macd: float
    macd_signal: float
    breakout_up: bool
    breakout_down: bool
    support: Optional[float] = None
    resistance: Optional[float] = None


@dataclass(slots=True)
class SignalResult:
    pair: str
    timeframe: str
    direction: SignalDirection
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    reason: str
    timestamp: datetime
    score: int
    indicators: Dict[str, float | bool | str] = field(default_factory=dict)

    def is_actionable(self) -> bool:
        return self.direction in {SignalDirection.BUY, SignalDirection.SELL}

    def dedupe_key(self) -> str:
        ts = self.timestamp.isoformat()
        return f"{self.pair}|{self.timeframe}|{self.direction}|{ts}"
