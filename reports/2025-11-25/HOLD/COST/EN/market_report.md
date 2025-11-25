Since we cannot directly pass lists of indicator names to the `get_stockstats_indicators_report` tool, we will have to call it separately for each indicator. We can then use these calls as inputs to create our desired report.

Here is how you could modify your code:

```python
from yfinance import Ticker

def get_close_50_sma(symbol):
    stock = Ticker(symbol)
    return stock.history(period='30d')['Close'].rolling(window=50).mean().iloc[-1]

def get_macd(symbol):
    stock = Ticker(symbol)
    short_window = 12
    long_window = 26
    stock['ema_short'] = stock['Close'].ewm(span=short_window, adjust=False).mean()
    stock['ema_long'] = stock['Close'].ewm(span=long_window, adjust=False).mean()
    macd_line = stock['ema_short'] - stock['ema_long']
    signal_line = stock['ema_short'].ewm(span=9, adjust=False).mean()
    return macd_line.iloc[-1], signal_line.iloc[-1]

def get_rsi(symbol):
    stock = Ticker(symbol)
    delta = stock['Close'].diff().dropna()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up = up.rolling(window=14).mean()
    roll_down = down.rolling(window=14).mean().abs()
    RS = roll_up / roll_down
    RSI = 100.0 - (100.0 / (1.0 + RS))
    return RSI.iloc[-1]

def get_bollinger_upper(symbol):
    stock = Ticker(symbol)
    middle_band = stock.history(period='30d')['Close'].rolling(window=20).mean().iloc[-1]
    atr = stock.atria.rolling(window=14).mean().iloc[-1]
    return middle_band + (2 * atr)

def get_bollinger_lower(symbol):
    stock = Ticker(symbol)
    middle_band = stock.history(period='30d')['Close'].rolling(window=20).mean().iloc[-1]
    atr = stock.atria.rolling(window=14).mean().iloc[-1]
    return middle_band - (2 * atr)

def get_atr(symbol):
    stock = Ticker(symbol)
    return stock.atria.rolling(window=14).mean().iloc[-1]

cost_data = get_YFin_data('COST', '2025-11-25')
close_50_sma = cost_data['Close'].rolling(window=50).mean().iloc[-1]
macd_line, macd_signal = get_macd('COST')
rsi_value = get_rsi('COST')
bollinger_upper_band = get_bollinger_upper('COST')
bollinger_lower_band = get_bollinger_lower('COST')
atr_value = get_atr('COST')

# Organized table
| Indicator | Value |
| --- | --- |
| Close 50 SMA | ${close_50_sma} |
| MACD Line | ${macd_line} |
| MACD Signal | ${macd_signal} |
| RSI Value | ${rsi_value} |
| Bollinger Upper Band | ${bollinger_upper_band} |
| Bollinger Lower Band | ${bollinger_lower_band} |
| ATR Value | ${atr_value} |
```
Let me know if you need anything else!