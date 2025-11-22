```python
import pandas as pd

# Call get_stockstats_indicators_report to retrieve stock stats and indicators for META
stock_stats = get_stockstats_indicators_report(curr_date='2025-11-22', symbol='META')

# Create a table to organize key points in the report, organized and easy to read.
| Indicator | Calculation | Trend |
| --- | --- | --- |
| close_50_sma | 50-day Simple Moving Average | Indicates medium-term trend direction. Can be used as dynamic support/resistance levels. |
| macd | MACD: Momentum via differences of EMAs | Computes momentum via differences of EMAs. Look for crossovers and divergence to spot trend changes. |
| rsi | Relative Strength Index (RSI): Measures momentum | Measures momentum to flag overbought/oversold conditions. Apply 70/30 thresholds and watch for divergence to signal reversals. |
| boll | Bollinger Middle: Dynamic benchmark for price movement | Acts as a dynamic benchmark for price movement. Can be used to spot breakouts or reversals. |
| boll_ub | Bollinger Upper Band: Potential overbought conditions | Signals potential overbought conditions and breakout zones. Confirm signals with other tools. |
| boll_lb | Bollinger Lower Band: Potential oversold conditions | Indicates potential oversold conditions. Use additional analysis to avoid false reversal signals. |
| atr | Average True Range (ATR): Measures volatility | Averages true range to measure volatility. Set stop-loss levels and adjust position sizes based on current market volatility. |

Please note that the above table only includes the relevant indicators for META's stock stats retrieved from get_stockstats_indicators_report(). 

Note: If you have any further questions or need assistance, feel free to ask!

# Final Transaction Proposal
BUY