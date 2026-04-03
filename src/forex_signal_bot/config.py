from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def _parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    app_env: str
    log_level: str
    data_provider: str
    alpha_vantage_api_key: str
    alpha_vantage_base_url: str
    forex_pairs: list[str]
    timeframes: list[str]
    scan_interval_minutes: int
    candle_limit: int
    request_timeout_seconds: int
    risk_reward_ratio: float
    breakout_lookback: int
    rsi_buy_max: float
    rsi_sell_min: float
    min_signal_score: int
    use_breakout_filter: bool
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    email_from: str
    email_to: list[str]
    email_enabled: bool
    state_dir: Path
    signal_store_file: Path
    scheduler_timezone: str

    @property
    def email_configured(self) -> bool:
        return bool(
            self.smtp_host
            and self.smtp_port
            and self.smtp_username
            and self.smtp_password
            and self.email_from
            and self.email_to
        )


def load_settings() -> Settings:
    state_dir = Path(os.getenv("STATE_DIR", "data"))
    signal_store_name = os.getenv("SIGNAL_STORE_FILE", "sent_signals.json")

    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        data_provider=os.getenv("DATA_PROVIDER", "alpha_vantage"),
        alpha_vantage_api_key=os.getenv("ALPHA_VANTAGE_API_KEY", ""),
        alpha_vantage_base_url=os.getenv(
            "ALPHA_VANTAGE_BASE_URL", "https://www.alphavantage.co/query"
        ),
        forex_pairs=_parse_csv(
            os.getenv(
                "FOREX_PAIRS",
                "EUR/USD,GBP/USD,USD/JPY,AUD/USD,USD/CAD",
            )
        ),
        timeframes=_parse_csv(os.getenv("TIMEFRAMES", "15min,1h,4h")),
        scan_interval_minutes=int(os.getenv("SCAN_INTERVAL_MINUTES", "15")),
        candle_limit=int(os.getenv("CANDLE_LIMIT", "350")),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20")),
        risk_reward_ratio=float(os.getenv("RISK_REWARD_RATIO", "2.0")),
        breakout_lookback=int(os.getenv("BREAKOUT_LOOKBACK", "20")),
        rsi_buy_max=float(os.getenv("RSI_BUY_MAX", "68")),
        rsi_sell_min=float(os.getenv("RSI_SELL_MIN", "32")),
        min_signal_score=int(os.getenv("MIN_SIGNAL_SCORE", "4")),
        use_breakout_filter=_parse_bool(os.getenv("USE_BREAKOUT_FILTER", "true"), True),
        smtp_host=os.getenv("SMTP_HOST", ""),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        email_from=os.getenv("EMAIL_FROM", ""),
        email_to=_parse_csv(os.getenv("EMAIL_TO", "")),
        email_enabled=_parse_bool(os.getenv("EMAIL_ENABLED", "true"), True),
        state_dir=state_dir,
        signal_store_file=state_dir / signal_store_name,
        scheduler_timezone=os.getenv("SCHEDULER_TIMEZONE", "UTC"),
    )
