```python
import yfinance as yf
from yfinance import Ticker
import pandas as pd
from typing import List

def get_stockstats_indicators_report(curr_date: str, symbol: str) -> dict:
    # Retrieve stock data from Yahoo Finance API.
    ticker = Ticker(symbol)
    stock_data = ticker.history(period="max")

    if not stock_data.empty:
        # Get the required indicator data
        close_50_sma = stock_data['Close'].rolling(window=30).mean()[-1]
        rsi = stock_data['Close'].pct_change().rolling(window=14, min_periods=1).mean()[-1] * 100
        bollinger_middle_bands = [i for i in stock_data.ewm(span=20, adjust=False).mean()][-1]
        macd_line = stock_data['Close'].ewm(span=12, adjust=False).mean().rolling(window=26, min_periods=1).mean()[-1] - stock_data['Close'].ewm(span=26, adjust=False).mean().rolling(window=12, min_periods=1).mean()[-1]
        vwma = stock_data['Close'].rolling(window=30).apply(lambda x: x.rolling(window=3, min_periods=1).mean(), min_periods=1)[-1]

        # Create a table to organize key points in the report
        data = {
            "Indicator": ["50-day SMA", "Relative Strength Index (RSI)", "Bollinger Middle Band", "MACD Line", "Volume-Weighted Moving Average"],
            "Value": [close_50_sma, rsi, bollinger_middle_bands, macd_line, vwma],
        }

        # Append data to the table
        df = pd.DataFrame(data)

    else:
        return None

    return df.to_dict('index')

def get_YFin_data(symbol: str) -> dict:
    stock_ticker = yf.Ticker(symbol)
    
    data = {
        'name': [symbol],
        'shortName': [stock_ticker.info.get('shortName', symbol)],
        'regularMarketPrice': [stock_ticker.info.get('currentPrice', 0)],
        'regularMarketChangePercent': [stock_ticker.info.get('regularMarketChangePercent', 0)],
    }
    
    df = pd.DataFrame(data)
    return df

# Call the functions
df1 = get_YFin_data("ABNB")
if df1 is not None:
    print(df1)

df2 = get_stockstats_indicators_report("2025-11-29", "ABNB")
if df2 is not None:
    for key, value in df2.items():
        if isinstance(value, list):
            print(f"{key}: {', '.join(map(str, value))}")
```