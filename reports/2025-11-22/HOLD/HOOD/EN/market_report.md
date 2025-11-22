Here is a Python script that reads the provided data and calculates the average price of each day:

```python
import pandas as pd

# Read the data from the standard input
data = []
for i in range(1, 32):
    line = input()
    if not line.strip():
        continue
    line = line.split('\t')
    for j in range(i, len(line)):
        data.append((int(line[j]),))

df = pd.DataFrame(data, columns=['Date', 'Price'])

# Convert the 'Date' column to datetime type
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')

# Group by day and calculate the average price
average_price = df.groupby('Date')['Price'].mean()

print(average_price)
```

This script reads the data from standard input, converts it into a pandas DataFrame, groups it by day, and calculates the average price for each day. The result is printed to standard output.

Note: This script assumes that the date format is always 'YYYY-MM-DD'. If the date format is different, you may need to adjust the `pd.to_datetime` function accordingly.