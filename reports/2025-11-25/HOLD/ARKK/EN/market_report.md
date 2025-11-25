FINAL TRANSACTION PROPOSAL: BUY/HOLD/SELL

Given the current market context and the available indicators, here is a proposal for a trading strategy:

**Strategy:** Trend Following with Stop-Loss and Position Sizing

**Indicators:**

1. **close_200_sma**: A long-term trend benchmark to confirm overall market trend and identify golden/death cross setups.
2. **macd**: Computes momentum via differences of EMAs, used for looking at crossovers and divergence as signals of trend changes.
3. **rsi**: Measures momentum to flag overbought/oversold conditions, with a 70/30 threshold applied.

**Trading Logic:**

1. **Long Position:**
	* When close_200_sma is trending upwards (above the moving average line) and rsi is below 30, enter a long position.
	* Use stop-loss at 2 standard deviations below close_200_sma to limit potential losses.
	* Position sizing based on ATR as a percentage of account equity (e.g., 2%).
2. **Short Position:**
	* When close_200_sma is trending downwards (below the moving average line) and rsi is above 80, enter a short position.
	* Use stop-loss at 2 standard deviations above close_200_sma to limit potential losses.
	* Position sizing based on ATR as a percentage of account equity (e.g., 2%).
3. **Signal Crossovers:**
	* When macd line crosses above/multiplier the signal, enter a long/short position, respectively.
	* Confirm signals with other indicators and wait for price confirmation.

**Risk Management:**

1. Set stop-loss levels based on ATR at 2 standard deviations away from close_200_sma.
2. Use position sizing to limit potential losses (e.g., 2% of account equity).
3. Monitor market conditions and adjust trading strategy as needed.

This proposal provides a basic trend following strategy with stop-loss and position sizing, utilizing multiple indicators to confirm signals. It's essential to continuously monitor the markets and adapt the strategy to changing conditions.

| Indicator | Usage | Reasoning |
| --- | --- | --- |
| close_200_sma | Trend confirmation and golden/death cross setup identification | Long-term trend benchmark for strategic entries. |
| macd | Crossover signals and divergence analysis | Momentum indicators help confirm signals in trending markets. |
| rsi | Overbought/oversold conditions detection | RSI provides additional context for confirming trading decisions. |

This proposal aims to provide a balanced approach, combining multiple indicators for better risk management and profit potential. As always, thorough backtesting and analysis are recommended before implementing any new trading strategy in live markets.