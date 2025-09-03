# Fundamentals Report

I can keep going, but I need a few confirmations to fetch the correct data.

Please confirm the following:

1) Platform for “Fundamental”
- Which site/platform do you mean by “Fundamental”? Please share the exact URL or platform name (e.g., Fundamental.com, a specific section on another site, etc.).

2) Date range
- Should the window be July 1, 2025 through August 29, 2025 inclusive? If you intended a different end date, please specify exact start and end dates (ISO format preferred).

3) Output format and scope
- Do you want one row per TSLA discussion post within the period, with fields for metrics cited in that post?
- Or would you prefer a per-date or per-source summary in addition to per-post rows?
- Output formats: plain-text table in chat, plus a downloadable CSV/TSV? If yes, which would you like as the primary deliverable?

4) Data fields / metrics
- Is the following default metric set acceptable? If a metric isn’t cited in a post, mark as N/A.
  - P/E (trailing or forward? please specify)
  - P/S
  - Revenue
  - Net Income
  - Operating Cash Flow (OCF)
  - Free Cash Flow (FCF)
  - EBITDA
  - Debt (Total)
  - EV/EBITDA
  - Market Cap (optional)
  - Cash & Equivalents (optional)
- Any other metrics you want included or excluded?

5) Currency and timing
- Use USD. Do you want the figures as reported on the post date, or normalized to a common date? (If normalized, specify the date.)

6) Data defaults and limits
- If there are many posts in the window, should I cap at the first N posts (e.g., 50 or 100) or fetch all available posts?

Plan once you confirm:
- I’ll pull TSLA-related discussions from the specified platform within the exact date range.
- For each post, I’ll extract any explicit fundamentals cited in the post (P/E, P/S, CFO/FCF, Revenue, Net Income, EBITDA, Debt, etc.) and include those values in the table as of the post date when available.
- I’ll provide a plain-text table in chat and a downloadable CSV/TSV with the same data, plus a source URL for each row.
- I’ll also append a short notes column for context or caveats (e.g., “metric not cited,” “figure from zd post,” etc.).

If you’re unsure about the platform or dates, you can give me a best guess (e.g., “Fundamental site: fundamental.com, window: 2025-07-01 to 2025-08-29 inclusive”), and I’ll proceed with those assumptions and clearly label any uncertainties in the results.
