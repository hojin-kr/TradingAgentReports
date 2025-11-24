The issue here is that some of the indicators you're trying to retrieve are not strings, but rather variable names. The `get_stockstats_indicators_report` function expects all input indicators to be strings.

Let's start by identifying which indicators are valid string inputs and which need to be handled differently:

1. **Valid String Inputs:**
   - close_50_sma
   - close_200_sma
   - boll
   - macd
   - rsi
   - boll_ub
   - boll_lb
   - atr

2. **Need to Handle Differently:**
   - close_10_ema (for this example, we can't use it directly as an input for get_stockstats_indicators_report)
   - macds (for this example, we can't use it directly as an input for get_stockstats_indicators_report)
   - macdh (for this example, we can't use it directly as an input for get_stockstats_indicators_report)

We will retrieve the required indicators separately.

First, let's call `get_YFin_data` to ensure we have the necessary CSV data. We will store the response in a variable called `data`.

```python
data = get_YFin_data('QQQ', '2025-11-24')
```

Next, we can retrieve the required indicators using the `get_stockstats_indicators_report` function with the appropriate string inputs.

Let's call the function again but this time pass in valid indicator names as strings. For our purposes here, let's focus on getting the following:

1. Moving Averages
2. MACD-related indicators

We will then further analyze and manipulate these indicators to suit our needs.


```python
ma_data = get_stockstats_indicators_report(
    curr_date='2025-11-24', 
    indicator=['close_50_sma', 'close_200_sma'], 
    symbol='QQQ'
)

macd_data = get_stockstats_indicators_report(
    curr_date='2025-11-24', 
    indicator=['macd', 'macds'], 
    symbol='QQQ'
)
```


Let's proceed by calling these functions and further analyzing the responses in our report.