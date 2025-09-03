# Fundamentals Report

Thanks for the update. I encountered an internal error fetching the data and don’t want to guess the source or the exact metrics you want.

To move forward efficiently, please confirm a few details. If you’d like, I can also proceed with a reasonable default setup:

Clarifications (please confirm)
- Fundamental source: Which platform or site should I pull from (e.g., a specific data provider or a URL you trust)? If you don’t have a preference, I can proceed with a standard reputable source (and note any limitations).
- Date range: Do you want July 1, 2025 through August 29, 2025 inclusive? (If you want a different window, specify exact start/end dates.)
- Metrics: Which fundamentals should be included? A practical default set:
  - Valuation: P/E (TTM), P/S (TTM), P/B (TBD)
  - Cash flow: Operating Cash Flow, Free Cash Flow
  - Size/val: Market Cap, Enterprise Value, Debt/Equity
  - Profitability: Revenue, Net Income, EBITDA
  - Others: Dividend Yield, Cash & Equivalents, Total Debt
  - Currency: Typically USD
- Granularity/format:
  - One row per data point (e.g., each ticker/date) or one row per date with all metrics?
  - Output: plain text table or CSV/Excel-friendly format?
- Insider data: Do you want insider sentiment and insider transactions included? If yes, should I pull:
  - Insider transactions (SEC Form 4 filings) and summarized sentiment, or
  - Only a basic count of insider buys/sells with net impact?

Default approach if you’re okay with it
- Source: A common financial data provider (clearly labeled).
- Window: 2025-07-01 to 2025-08-29 inclusive.
- Metrics: P/E (TTM), P/S (TTM), EV/EBITDA, Revenue, Net Income, Operating Cash Flow, Free Cash Flow, Total Debt, Debt/Equity, Cash & Equivalents, Market Cap, Enterprise Value, Dividend Yield.
- Granularity: One row per date in the window with the metrics as of that date, plus a summary row for the period.
- Output: Markdown-friendly table plus a compact CSV option if you want to download.

If you confirm, I’ll run the fetch again and return a detailed report with a Markdown table at the end, plus a compact table you can paste into a workbook.
