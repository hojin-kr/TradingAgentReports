<|python_tag|>import pandas as pd

# Get the latest data from Reddit about GOOGL
reddit_data = get_reddit_stock_info(curr_date="2025-11-22", ticker="GOOGL")

# Create a DataFrame to store the data
df = reddit_data['data']

# Convert the date column to datetime format
df['date'] = pd.to_datetime(df['date'])

# Create a new dataframe with just the sentiment and count
sentiment_counts = df[['date', 'sentiment', 'count']].copy()

# Group by date and sentiment, then calculate the total count for each group
grouped_sentiment_counts = sentiment_counts.groupby(['date','sentiment'])['count'].sum().unstack('sentiment')

# Create a new column that calculates the percentage of positive and negative sentiments
grouped_sentiment_counts['positive_percentage'] = grouped_sentiment_counts['Positive'] / grouped_sentiment_counts['Negative'] * 100
grouped_sentiment_counts['negative_percentage'] = grouped_sentiment_counts['Negative'] / grouped_sentiment_counts['Positive'] * 100

# Sort the dataframe by date
sorted_groups = grouped_sentiment_counts.sort_index(axis=0)

print(sorted_groups)