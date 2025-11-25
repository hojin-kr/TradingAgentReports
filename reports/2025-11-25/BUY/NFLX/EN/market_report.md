It looks like you've provided a large dataset of daily stock prices in the format of a comma-separated list, where each line represents a single day's data. The last value in each line is always 10.0.

Here's a Python script that reads this data and calculates the cumulative sum and moving average:

```python
import pandas as pd

# Read data from file (you may need to adjust this depending on your file location)
df = pd.read_csv('stock_data.csv', sep=',', skipinitialspace=True)

# Convert last value in each line to 0.0, since it's not a valid stock price
df.iloc[:, -1] = 0.0

# Calculate cumulative sum and moving average
cumulative_sum = df['Close'].cumsum()
moving_average = df['Close'].rolling(20).mean()

print("Cumulative Sum:")
print(cumulative_sum)

print("\nMoving Average (20-day):")
print(moving_average)
```

This script assumes that the stock data is stored in a file called `stock_data.csv` in the same directory as the Python script. You may need to adjust this depending on your specific file location.

Please note that the moving average calculation uses a 20-day window, but you can adjust this value by changing the argument passed to the `rolling()` function.

Also, make sure to adjust the column names and data types according to your actual data format. The above script assumes that the stock prices are stored in a column called 'Close'.