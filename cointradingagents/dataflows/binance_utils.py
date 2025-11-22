from __future__ import annotations

import math
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional

import pandas as pd
import requests

from .config import get_config


def _session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update({"User-Agent": "CoinTradingAgents/1.0"})
    return sess


def _api_get(path: str, params: Optional[Dict] = None, retries: int = 3):
    cfg = get_config()
    base_url = cfg["binance_base_url"].rstrip("/")
    url = f"{base_url}{path}"
    last_err = None
    for attempt in range(retries):
        try:
            resp = _session().get(url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and data.get("code"):
                raise RuntimeError(data.get("msg", "Binance API error"))
            return data
        except Exception as err:
            last_err = err
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to call Binance API {path}: {last_err}") from last_err


def _interval_to_ms(interval: str) -> int:
    unit = interval[-1]
    value = int(interval[:-1])
    multipliers = {"m": 60, "h": 3600, "d": 86400}
    if unit not in multipliers:
        raise ValueError(f"Unsupported interval: {interval}")
    return value * multipliers[unit] * 1000


def normalize_symbol(symbol: str, quote: str = "USDT") -> str:
    symbol = symbol.upper().replace("/", "")
    if not symbol.endswith(quote):
        symbol = f"{symbol}{quote}"
    return symbol


def get_top_usdt_symbols(limit: int = 10, min_quote_volume: float = 1_000_000):
    """Return the most liquid USDT pairs sorted by 24h quote volume."""
    tickers = _api_get("/api/v3/ticker/24hr")
    filtered: List[Dict] = []
    for entry in tickers:
        symbol = entry.get("symbol", "")
        if not symbol.endswith("USDT"):
            continue
        if any(token in symbol for token in ["UP", "DOWN", "BULL", "BEAR", "TEST"]):
            continue
        quote_volume = float(entry.get("quoteVolume", 0.0))
        if quote_volume < min_quote_volume:
            continue
        filtered.append(
            {
                "symbol": symbol,
                "base_asset": symbol[:-4],
                "quote_volume": quote_volume,
                "price_change_percent": float(entry.get("priceChangePercent", 0.0)),
                "last_price": float(entry.get("lastPrice", 0.0)),
            }
        )

    filtered.sort(key=lambda item: item["quote_volume"], reverse=True)
    return filtered[:limit]


def fetch_klines(
    symbol: str,
    start_time: datetime,
    end_time: datetime,
    interval: str = "1d",
) -> pd.DataFrame:
    """Fetch OHLCV data between two datetimes."""
    norm_symbol = normalize_symbol(symbol)
    start_ms = int(start_time.replace(tzinfo=timezone.utc).timestamp() * 1000)
    end_ms = int(end_time.replace(tzinfo=timezone.utc).timestamp() * 1000)
    interval_ms = _interval_to_ms(interval)

    records: List[List] = []
    fetch_start = start_ms

    while fetch_start < end_ms:
        params = {
            "symbol": norm_symbol,
            "interval": interval,
            "startTime": fetch_start,
            "endTime": end_ms,
            "limit": 1000,
        }
        chunk = _api_get("/api/v3/klines", params)
        if not chunk:
            break
        records.extend(chunk)
        fetch_start = int(chunk[-1][0]) + interval_ms
        if len(chunk) < 1000:
            break

    df = pd.DataFrame(
        records,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )

    if df.empty:
        return df

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)

    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "taker_buy_base",
        "taker_buy_quote",
    ]
    for col in numeric_cols:
        df[col] = df[col].astype(float)

    df["number_of_trades"] = df["number_of_trades"].astype(int)

    return df


def ensure_history_window(
    symbol: str,
    end_date: datetime,
    window_days: int,
    buffer_days: int = 260,
    interval: str = "1d",
) -> pd.DataFrame:
    """Fetch enough candles to cover the requested history window plus buffer."""
    start_date = end_date - timedelta(days=window_days + buffer_days)
    df = fetch_klines(symbol, start_date, end_date + timedelta(days=1), interval)
    return df

