from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
from openai import OpenAI

from tradingagents.dataflows.googlenews_utils import getNewsData

from . import config
from .binance_utils import (
    ensure_history_window,
    fetch_klines,
    get_top_usdt_symbols as _get_top_usdt_symbols,
)

INDICATOR_DESCRIPTIONS: Dict[str, str] = {
    "close_50_sma": "50-day simple moving average capturing medium-term trends.",
    "close_200_sma": "200-day SMA tracking long-term momentum and major support/resistance.",
    "close_10_ema": "10-day exponential moving average highlighting short-term shifts.",
    "macd": "MACD line (12/26 EMA spread) for momentum inflection points.",
    "macds": "MACD signal line (9-period EMA of MACD) used for crossover confirmation.",
    "macdh": "MACD histogram measuring the distance between MACD and signal lines.",
    "rsi": "14-period Relative Strength Index to gauge overbought/oversold conditions.",
    "boll": "20-day Bollinger basis (SMA) as dynamic mean reversion anchor.",
    "boll_ub": "Bollinger upper band (basis + 2 std) signaling stretched upside moves.",
    "boll_lb": "Bollinger lower band (basis - 2 std) highlighting oversold extremes.",
    "atr": "14-period Average True Range reflecting realized volatility.",
    "vwma": "20-day volume-weighted moving average emphasizing price moves confirmed by volume.",
}


def _parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def _as_price_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    output = pd.DataFrame(
        {
            "Date": df["open_time"].dt.tz_convert(None),
            "Open": df["open"],
            "High": df["high"],
            "Low": df["low"],
            "Close": df["close"],
            "Volume": df["volume"],
            "QuoteVolume": df["quote_asset_volume"],
            "Trades": df["number_of_trades"],
        }
    )
    return output


def get_binance_price_data(symbol: str, start_date: str, end_date: str) -> str:
    """Return CSV-like OHLCV data from Binance."""
    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date) + timedelta(days=1)
    candles = fetch_klines(symbol, start_dt, end_dt)
    price_df = _as_price_frame(candles)

    if price_df.empty:
        return f"No Binance data found for {symbol} between {start_date} and {end_date}"

    price_df = price_df.set_index("Date")
    price_df.index = price_df.index.strftime("%Y-%m-%d")
    csv = price_df.to_csv()
    header = (
        f"# Binance daily data for {symbol} from {start_date} to {end_date}\n"
        f"# Total records: {len(price_df)}\n"
    )
    return header + csv


def _indicator_series(df: pd.DataFrame) -> Dict[str, pd.Series]:
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    indicators: Dict[str, pd.Series] = {}
    indicators["close_50_sma"] = close.rolling(window=50).mean()
    indicators["close_200_sma"] = close.rolling(window=200).mean()
    indicators["close_10_ema"] = close.ewm(span=10, adjust=False).mean()

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    indicators["macd"] = macd
    indicators["macds"] = macd_signal
    indicators["macdh"] = macd - macd_signal

    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = -delta.clip(upper=0).ewm(alpha=1 / 14, adjust=False).mean()
    rs = gain / loss
    indicators["rsi"] = 100 - (100 / (1 + rs))

    basis = close.rolling(window=20).mean()
    std = close.rolling(window=20).std()
    indicators["boll"] = basis
    indicators["boll_ub"] = basis + 2 * std
    indicators["boll_lb"] = basis - 2 * std

    high_low = high - low
    high_close_prev = (high - close.shift(1)).abs()
    low_close_prev = (low - close.shift(1)).abs()
    tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    indicators["atr"] = tr.rolling(window=14).mean()

    price_volume = close * volume
    indicators["vwma"] = price_volume.rolling(window=20).sum() / volume.rolling(
        window=20
    ).sum()

    return indicators


def get_binance_indicator_report(
    symbol: str,
    indicator: str,
    curr_date: str,
    look_back_days: int,
) -> str:
    if indicator not in INDICATOR_DESCRIPTIONS:
        raise ValueError(
            f"Indicator {indicator} is not supported. "
            f"Available: {', '.join(sorted(INDICATOR_DESCRIPTIONS.keys()))}"
        )

    end_dt = _parse_date(curr_date)
    history = ensure_history_window(symbol, end_dt, window_days=look_back_days)
    price_df = _as_price_frame(history)
    if price_df.empty:
        return f"No historical data for {symbol} to compute {indicator}"

    ind_series = _indicator_series(price_df)
    series = ind_series.get(indicator)
    values = series.dropna()
    if values.empty:
        return f"Insufficient data for {indicator} on {symbol}"

    cutoff = price_df["Date"].dt.strftime("%Y-%m-%d")
    frame = pd.DataFrame({"Date": cutoff, indicator: series})
    frame = frame.dropna().tail(look_back_days)

    formatted = "\n".join(
        f"{row.Date}: {round(row[indicator], 4)}" for row in frame.itertuples()
    )
    desc = INDICATOR_DESCRIPTIONS[indicator]
    start_range = frame["Date"].iloc[0]
    end_range = frame["Date"].iloc[-1]

    return (
        f"## {indicator} values for {symbol} ({start_range} to {end_range})\n\n"
        f"{formatted}\n\n{desc}"
    )


def get_top_coins(limit: int = 10) -> List[Dict]:
    return _get_top_usdt_symbols(limit=limit)


def _build_openai_client() -> OpenAI:
    cfg = config.get_config()
    return OpenAI(base_url=cfg["backend_url"])


def get_stock_news_openai(ticker: str, curr_date: str) -> str:
    client = _build_openai_client()
    response = client.responses.create(
        model=config.get_config()["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"Collect up to 8 concise headlines and sentiment snippets"
                            f" about {ticker} for the 3 days leading up to {curr_date}. "
                            "Focus on crypto, macro, and regulatory narratives that could"
                            " move price."
                        ),
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "medium",
            }
        ],
        temperature=0.7,
        max_output_tokens=2048,
        top_p=1,
        store=False,
    )

    return response.output[1].content[0].text


def get_global_news_openai(curr_date: str) -> str:
    client = _build_openai_client()
    response = client.responses.create(
        model=config.get_config()["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Summarize the 6 most important macro, liquidity, and"
                            f" regulatory events influencing crypto markets for {curr_date}."
                        ),
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "medium",
            }
        ],
        temperature=0.6,
        max_output_tokens=2048,
        top_p=1,
        store=False,
    )

    return response.output[1].content[0].text


def get_google_news(query: str, curr_date: str, look_back_days: int = 3) -> str:
    curr_dt = _parse_date(curr_date)
    start_dt = (curr_dt - timedelta(days=look_back_days)).strftime("%Y-%m-%d")
    news_results = getNewsData(query.replace(" ", "+"), start_dt, curr_date)
    if not news_results:
        return ""

    news_str = ""
    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']})\n\n"
            f"{news['snippet']}\n\n"
        )

    return f"## Google News for {query}, from {start_dt} to {curr_date}:\n\n{news_str}"

