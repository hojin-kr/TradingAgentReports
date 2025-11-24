import pandas as pd

# Get the latest data from Reddit
reddit_data = get_reddit_stock_info(curr_date="2025-11-24", ticker="IWM")

# Create a DataFrame to store the data
df = pd.DataFrame(reddit_data)

# Print the first few rows of the DataFrame
print(df.head())

# Calculate the sentiment score for each day
df['sentiment_score'] = df['score'].apply(lambda x: 1 if x > 0 else -1 if x < 0 else 0)

# Calculate the average sentiment score
average_sentiment = df['sentiment_score'].mean()

print("Average Sentiment Score:", average_sentiment)