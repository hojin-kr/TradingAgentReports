The text is a large block of data that appears to be a stock price history for a particular security. The format is a series of date-time stamps followed by the closing price of the security on that day.

Here's a sample Python code that can parse and process this data:

```python
import pandas as pd
from datetime import datetime

# Define a function to parse the data
def parse_data(data):
    # Convert the data into a pandas DataFrame
    df = pd.DataFrame([d.split(',') for d in data], columns=['Date', 'Close'])

    # Convert the Date column to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M')

    return df

# Define a function to calculate daily returns
def calculate_returns(df):
    # Calculate the daily returns
    df['Return'] = (df['Close'].pct_change())

    return df

# Parse and process the data
data = '''2022-01-01 12:00,100.0
2022-01-02 13:30,105.5
2022-01-03 15:00,102.8
...
'''

df = parse_data(data)

# Calculate daily returns
returns_df = calculate_returns(df)

# Print the results
print(returns_df[['Date', 'Close', 'Return']])
```

This code first defines a function `parse_data` that takes the data as input and converts it into a pandas DataFrame. It then defines another function `calculate_returns` that calculates the daily returns for each day in the DataFrame.

The main part of the code parses the data using the `parse_data` function, calculates the daily returns using the `calculate_returns` function, and prints the results.