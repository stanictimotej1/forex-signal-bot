from __future__ import annotations

from dataclasses import asdict
from typing import List

import pandas as pd

from .config import Settings
from .models import MarketSnapshot, SignalDirection, SignalResult
from .risk import build_trade_plan


def _build_snapshot(pair: str, timeframe: str, latest: pd.Series) -> MarketSnapshot:
    return MarketSnapshot(
        pair=pair,
        timeframe=timeframe,
        timestamp=latest.name.to_pydatetime(),
        close=float(latest["close"]),
        ema_50=float(latest["ema_50"]),
        ema_200=float(latest["ema_200"]),
        rsi=float(latest["rsi"]),
        macd=float(latest["macd"]),
        macd_signal=float(latest["macd_signal"]),
        breakout_up=bool(latest["breakout_up"]),
        breakout_down=bool(latest["breakout_down"]),
        support=float(latest["support"]) if pd.notna(latest["support"]) else None,
        resistance=float(latest["resistance"]) if pd.notna(latest["resistance"]) else None,
    )


def evaluate_signal(pair: str, timeframe: str, df: pd.DataFrame, settings: Settings) -> SignalResult:
    latest = df.iloc[-1]
    snapshot = _build_snapshot(pair, timeframe, latest)

    buy_score = 0
    sell_score = 0
    reasons: List[str] = []

    trend_bullish = snapshot.ema_50 > snapshot.ema_200
    trend_bearish = snapshot.ema_50 < snapshot.ema_200
    price_above_ema = snapshot.close > snapshot.ema_50
    price_below_ema = snapshot.close < snapshot.ema_50
    macd_bullish = snapshot.macd > snapshot.macd_signal
    macd_bearish = snapshot.macd < snapshot.macd_signal
    rsi_buy_ok = snapshot.rsi < settings.rsi_buy_max and snapshot.rsi > 45
    rsi_sell_ok = snapshot.rsi > settings.rsi_sell_min and snapshot.rsi < 55

    if trend_bullish:
        buy_score += 2
        reasons.append("EMA50 > EMA200")
    if trend_bearish:
        sell_score += 2
        reasons.append("EMA50 < EMA200")
    if price_above_ema:
        buy_score += 1
        reasons.append("Price above EMA50")
    if price_below_ema:
        sell_score += 1
        reasons.append("Price below EMA50")
    if macd_bullish:
        buy_score += 1
        reasons.append("MACD bullish")
    if macd_bearish:
        sell_score += 1
        reasons.append("MACD bearish")
    if rsi_buy_ok:
        buy_score += 1
        reasons.append(f"RSI supportive for BUY ({snapshot.rsi:.2f})")
    if rsi_sell_ok:
        sell_score += 1
        reasons.append(f"RSI supportive for SELL ({snapshot.rsi:.2f})")

    if settings.use_breakout_filter:
        if snapshot.breakout_up:
            buy_score += 1
            reasons.append("Breakout up confirmed")
        if snapshot.breakout_down:
            sell_score += 1
            reasons.append("Breakout down confirmed")

    indicators = {
        "close": round(snapshot.close, 5),
        "ema_50": round(snapshot.ema_50, 5),
        "ema_200": round(snapshot.ema_200, 5),
        "rsi": round(snapshot.rsi, 2),
        "macd": round(snapshot.macd, 5),
        "macd_signal": round(snapshot.macd_signal, 5),
        "breakout_up": snapshot.breakout_up,
        "breakout_down": snapshot.breakout_down,
        "buy_score": buy_score,
        "sell_score": sell_score,
    }

    if buy_score >= settings.min_signal_score and buy_score > sell_score:
        stop_loss, take_profit = build_trade_plan(
            pair=pair,
            direction="BUY",
            entry_price=snapshot.close,
            support=snapshot.support or snapshot.close * 0.998,
            resistance=snapshot.resistance or snapshot.close * 1.002,
            risk_reward_ratio=settings.risk_reward_ratio,
        )
        return SignalResult(
            pair=pair,
            timeframe=timeframe,
            direction=SignalDirection.BUY,
            entry_price=snapshot.close,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason="; ".join(reasons),
            timestamp=snapshot.timestamp,
            score=buy_score,
            indicators=indicators,
        )

    if sell_score >= settings.min_signal_score and sell_score > buy_score:
        stop_loss, take_profit = build_trade_plan(
            pair=pair,
            direction="SELL",
            entry_price=snapshot.close,
            support=snapshot.support or snapshot.close * 0.998,
            resistance=snapshot.resistance or snapshot.close * 1.002,
            risk_reward_ratio=settings.risk_reward_ratio,
        )
        return SignalResult(
            pair=pair,
            timeframe=timeframe,
            direction=SignalDirection.SELL,
            entry_price=snapshot.close,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason="; ".join(reasons),
            timestamp=snapshot.timestamp,
            score=sell_score,
            indicators=indicators,
        )

    return SignalResult(
        pair=pair,
        timeframe=timeframe,
        direction=SignalDirection.NO_SIGNAL,
        entry_price=snapshot.close,
        stop_loss=None,
        take_profit=None,
        reason="Conditions not aligned clearly enough.",
        timestamp=snapshot.timestamp,
        score=max(buy_score, sell_score),
        indicators=indicators,
    )
