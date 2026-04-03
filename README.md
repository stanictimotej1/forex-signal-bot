# Forex Signal Bot

Production-ready Python bot za **forex alerting**. Bot spremlja več valutnih parov in timeframe-ov, izračuna tehnične indikatorje, generira **BUY / SELL / NO SIGNAL** alerte in pošlje email prek Outlook SMTP.

> **Pomembno:** ta projekt je namenjen **izključno obvestilom**. Ne odpira trade-ov in ni namenjen avtomatskemu izvrševanju poslov.
>
> **Disclaimer:** To ni finančni nasvet. Trading vključuje tveganje in lahko povzroči izgubo kapitala.

## Features

- spremljanje parov:
  - EUR/USD
  - GBP/USD
  - USD/JPY
  - AUD/USD
  - USD/CAD
- timeframe-i:
  - 15m
  - 1h
  - 4h
- rule-based strategija:
  - EMA 50 / EMA 200
  - RSI
  - MACD
  - breakout filter
- Outlook SMTP email obvestila
- anti-duplicate signal store
- console + file logging
- `.env` konfiguracija
- enkratni test run
- scheduler za periodično skeniranje
- demo/backtest način

## Arhitektura

```text
forex_signal_bot/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── sample_email.txt
├── src/
│   └── forex_signal_bot/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── logger_setup.py
│       ├── models.py
│       ├── utils.py
│       ├── data_fetcher.py
│       ├── indicators.py
│       ├── signal_engine.py
│       ├── risk.py
│       ├── email_service.py
│       ├── scheduler_service.py
│       ├── dedupe_store.py
│       ├── backtest.py
│       └── demo_data.py
└── tests/
    └── test_signal_engine.py
```

## Strategija

Bot uporablja transparentno rule-based logiko. Signal se generira samo, ko se ujema več pogojev.

### BUY ideja
- EMA 50 > EMA 200
- cena je nad EMA 50
- RSI ni preveč visok
- MACD linija > MACD signal
- breakout filter ni izrazito bearish

### SELL ideja
- EMA 50 < EMA 200
- cena je pod EMA 50
- RSI ni preveč nizek
- MACD linija < MACD signal
- breakout filter ni izrazito bullish

### NO SIGNAL
- kadar ni dovolj potrditve ali so pogoji mešani

## Podatkovni vir

Privzeto je nastavljen **Alpha Vantage** za forex intraday in daily podatke. Potrebuješ API key.

Primer:
- `FX_INTRADAY` za 15m, 60min
- `FX_DAILY` kot fallback za 4h resample

Opomba:
- brezplačni API-ji imajo rate limite
- 4h timeframe je tukaj sestavljen iz nižjega timeframe-a z resamplanjem, zato ni namenjen institutional-grade izvedbi

Projekt je narejen tako, da lahko kasneje enostavno zamenjaš `data_fetcher.py` za broker API ali drug market data provider.

## Setup

### 1) Kloniraj repo

```bash
git clone https://github.com/yourusername/forex_signal_bot.git
cd forex_signal_bot
```

### 2) Ustvari virtual environment

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS / Linux:
```bash
source .venv/bin/activate
```

### 3) Namesti dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 4) Pripravi `.env`

Skopiraj primer:

```bash
cp .env.example .env
```

Nato izpolni vrednosti.

## Outlook SMTP setup

V `.env` nastavi:
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `EMAIL_TO`

Za Outlook / Microsoft 365 tipično uporabi:
- host: `smtp.office365.com`
- port: `587`
- STARTTLS
- poln email naslov kot username

Če tvoj tenant ali račun zahteva dodatno zaščito, uporabi **app password** ali kasneje preidi na OAuth. Pred uporabo preveri, da je SMTP AUTH omogočen za račun.

## Zagon

### Enkratni test run

```bash
python -m forex_signal_bot.main --mode once
```

To:
- prebere podatke
- izračuna indikatorje
- oceni signale
- pošlje email samo za nove veljavne signale

### Scheduler način

```bash
python -m forex_signal_bot.main --mode scheduler
```

Bot bo skeniral trg po intervalu iz `.env`.

### Demo način

```bash
python -m forex_signal_bot.main --mode demo
```

Uporabi lokalno generirane demo podatke brez klica API-ja.

### Backtest / review način

```bash
python -m forex_signal_bot.main --mode backtest
```

To ne optimizira strategije, ampak izvede preprost zgodovinski pregled signalov na demo podatkih.

## Ključne `.env` nastavitve

```env
FOREX_PAIRS=EUR/USD,GBP/USD,USD/JPY,AUD/USD,USD/CAD
TIMEFRAMES=15min,1h,4h
SCAN_INTERVAL_MINUTES=15
ALPHA_VANTAGE_API_KEY=your_key_here

SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_password_or_app_password
EMAIL_FROM=your_email@outlook.com
EMAIL_TO=target_email@example.com

RISK_REWARD_RATIO=2.0
BREAKOUT_LOOKBACK=20
RSI_BUY_MAX=68
RSI_SELL_MIN=32
MIN_SIGNAL_SCORE=4
```


## GitHub-only deploy (brez lokalnega PC-ja)

Če želiš, da bot teče brez tvojega računalnika, lahko projekt naložiš v GitHub repo in uporabiš **GitHub Actions**.

### Koraki
1. ustvari nov GitHub repo
2. naloži vse datoteke iz tega projekta
3. v repoju odpri **Settings -> Secrets and variables -> Actions**
4. dodaj secrets:
   - `ALPHA_VANTAGE_API_KEY`
   - `OUTLOOK_EMAIL`
   - `OUTLOOK_PASSWORD`
   - `EMAIL_TO`
5. workflow datoteka je že pripravljena v `.github/workflows/forex-bot.yml`
6. odpri zavihek **Actions** in klikni **Run workflow**
7. po uspešnem testu bo workflow tekel samodejno vsakih 15 minut

### Opombe
- workflow ustvari `.env` med samim runom iz GitHub Secrets
- datoteka `data/sent_signals.json` se po vsakem runu commit-a nazaj v repo, da bot ne pošilja istih signalov znova
- to je rešitev za **alerte**, ne za ultra-low-latency trading

## Deploy

### VPS
Bot lahko poženeš na:
- Ubuntu VPS
- Windows VPS
- domačem mini serverju

Priporočeno:
- systemd service na Linuxu
- virtualenv
- rotacija logov
- monitoring restarta

### GitHub
GitHub sam po sebi ni idealen za neprekinjen runtime proces. Lahko pa uporabiš:
- GitHub za source control
- VPS za runtime
- GitHub Actions samo za teste / lint / build

## Varnost

- nikoli ne commitaš `.env`
- ne hardcodaš gesel ali ključev
- uporabi `.env.example`
- za email račun po možnosti uporabi app password ali namenski mailbox

## Primer emaila

Subject:
```text
[FOREX SIGNAL] BUY EUR/USD 1H
```

Body:
```text
Pair: EUR/USD
Timeframe: 1H
Signal: BUY
Entry Idea: 1.08420
Stop Loss: 1.08180
Take Profit: 1.08900
Indicators: EMA50>EMA200, RSI=58.4, MACD bullish, breakout confirmed
Timestamp: 2026-04-03T14:15:00Z

Risk Disclaimer:
This alert is for informational purposes only. It is not financial advice. Trading involves risk.
```

## Testi

```bash
pytest -q
```

## Ideje za upgrade

- Telegram alerts
- Discord webhook alerts
- SQLite/PostgreSQL signal history
- web dashboard (FastAPI + frontend)
- Docker / docker-compose
- broker adapter layer
- boljši session/timezone handling
- multi-provider market data fallback
- OAuth za Microsoft namesto SMTP password

## Omejitve

- brezplačni market data API-ji imajo lahko rate limite in zamike
- 4h timeframe je implementiran prek resampla nižjih podatkov
- signal logika je namerno konservativna, ne “napoveduje” trga

## License

MIT ali po tvoji izbiri.
