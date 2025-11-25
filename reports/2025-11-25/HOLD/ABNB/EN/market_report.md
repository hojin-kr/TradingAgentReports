Since no data is available for ABNB, I will call the get_YFin_data tool to retrieve historical data for the next trading day.

```
{"name": "get_YFin_data", "parameters": {"end_date":"2025-11-26","start_date":"2025-11-25","symbol":"ABNB"}}
```

I will then call the get_stockstats_indicators_report tool with a later date to retrieve the required indicators for ABNB.

```
{"name": "get_stockstats_indicators_report", "parameters": {"curr_date":"2025-11-26","indicator":["close_50_sma","macd","rsi","boll_ub","boll_lb","atr","vwma"],"look_back_days":"15","symbol":"ABNB"}}
```

Let me proceed with calling the tool to get the required indicators.

Please wait while I generate the report...