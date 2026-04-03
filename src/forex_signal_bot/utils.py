from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_timeframe_label(timeframe: str) -> str:
    mapping = {
        "15min": "15M",
        "1h": "1H",
        "4h": "4H",
    }
    return mapping.get(timeframe.lower(), timeframe.upper())
