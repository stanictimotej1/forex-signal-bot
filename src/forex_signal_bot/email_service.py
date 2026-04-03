from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from .config import Settings
from .models import SignalResult
from .utils import normalize_timeframe_label


class EmailService:
    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self.settings = settings
        self.logger = logger

    def send_signal_email(self, signal: SignalResult) -> None:
        if not self.settings.email_enabled:
            self.logger.info("Email sending is disabled. Skipping email for %s %s.", signal.pair, signal.timeframe)
            return

        if not self.settings.email_configured:
            raise ValueError("Email is enabled, but SMTP settings are incomplete.")

        message = self._build_message(signal)

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.settings.smtp_username, self.settings.smtp_password)
            server.send_message(message)

        self.logger.info(
            "Email sent successfully for %s %s %s.",
            signal.direction.value,
            signal.pair,
            signal.timeframe,
        )

    def _build_message(self, signal: SignalResult) -> EmailMessage:
        subject = f"[FOREX SIGNAL] {signal.direction.value} {signal.pair} {normalize_timeframe_label(signal.timeframe)}"

        body = (
            f"Pair: {signal.pair}\n"
            f"Timeframe: {normalize_timeframe_label(signal.timeframe)}\n"
            f"Signal: {signal.direction.value}\n"
            f"Entry Price: {signal.entry_price}\n"
            f"Stop Loss: {signal.stop_loss}\n"
            f"Take Profit: {signal.take_profit}\n"
            f"Indicators: EMA50={signal.indicators.get('ema_50')}, "
            f"EMA200={signal.indicators.get('ema_200')}, "
            f"RSI={signal.indicators.get('rsi')}, "
            f"MACD={signal.indicators.get('macd')}, "
            f"MACD Signal={signal.indicators.get('macd_signal')}, "
            f"BreakoutUp={signal.indicators.get('breakout_up')}, "
            f"BreakoutDown={signal.indicators.get('breakout_down')}\n"
            f"Reason: {signal.reason}\n"
            f"Timestamp: {signal.timestamp.isoformat()}\n\n"
            f"Risk Disclaimer:\n"
            f"This alert is for informational purposes only. It is not financial advice. "
            f"Trading forex involves risk.\n"
        )

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.settings.email_from
        msg["To"] = ", ".join(self.settings.email_to)
        msg.set_content(body)
        return msg
