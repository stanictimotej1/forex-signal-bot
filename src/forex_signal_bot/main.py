from __future__ import annotations

import argparse
import traceback
from typing import Iterable

from .backtest import run_demo_backtest
from .config import Settings, load_settings
from .data_fetcher import DataFetcher
from .dedupe_store import SignalStore
from .demo_data import generate_demo_ohlc
from .email_service import EmailService
from .indicators import add_indicators
from .logger_setup import setup_logging
from .scheduler_service import BotScheduler
from .signal_engine import evaluate_signal


def scan_once(
    settings: Settings,
    fetcher: DataFetcher,
    email_service: EmailService,
    store: SignalStore,
    logger,
    use_demo_data: bool = False,
) -> None:
    logger.info("Starting market scan. demo_mode=%s", use_demo_data)

    for pair in settings.forex_pairs:
        for timeframe in settings.timeframes:
            try:
                if use_demo_data:
                    freq = "15min" if timeframe == "15min" else "1H"
                    raw_df = generate_demo_ohlc(periods=max(settings.candle_limit, 350), freq=freq)
                    if timeframe == "4h":
                        raw_df = (
                            raw_df.resample("4H")
                            .agg({"open": "first", "high": "max", "low": "min", "close": "last"})
                            .dropna()
                        )
                else:
                    raw_df = fetcher.fetch(pair, timeframe)

                enriched = add_indicators(raw_df, breakout_lookback=settings.breakout_lookback)
                signal = evaluate_signal(pair, timeframe, enriched, settings)

                logger.info(
                    "Signal evaluated | pair=%s timeframe=%s direction=%s score=%s",
                    pair,
                    timeframe,
                    signal.direction.value,
                    signal.score,
                )

                if not signal.is_actionable():
                    continue

                key = signal.dedupe_key()
                if store.has(key):
                    logger.info("Duplicate signal skipped: %s", key)
                    continue

                email_service.send_signal_email(signal)
                store.add(key)

            except Exception as exc:
                logger.error(
                    "Failed processing pair=%s timeframe=%s | error=%s\n%s",
                    pair,
                    timeframe,
                    exc,
                    traceback.format_exc(),
                )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Forex signal bot (alerts only).")
    parser.add_argument(
        "--mode",
        choices=["once", "scheduler", "demo", "backtest"],
        default="once",
        help="Runtime mode.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    settings = load_settings()
    settings.state_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(settings.log_level)
    logger.info("Bot starting in mode=%s", args.mode)

    fetcher = DataFetcher(settings, logger)
    email_service = EmailService(settings, logger)
    store = SignalStore(settings.signal_store_file)

    if args.mode == "once":
        scan_once(settings, fetcher, email_service, store, logger, use_demo_data=False)
        return

    if args.mode == "demo":
        scan_once(settings, fetcher, email_service, store, logger, use_demo_data=True)
        return

    if args.mode == "backtest":
        run_demo_backtest(settings, logger)
        return

    if args.mode == "scheduler":
        scheduler = BotScheduler(
            settings=settings,
            logger=logger,
        )
        scheduler.start(lambda: scan_once(settings, fetcher, email_service, store, logger, False))
        return


if __name__ == "__main__":
    main()
