<|python_tag|>import pandas as pd

reddit_data = get_reddit_stock_info(curr_date="2025-11-25", ticker="VBI")

# Extract relevant information from the response
post_count = reddit_data['post_count']
comment_count = reddit_data['comment_count']
sentiment = reddit_data['sentiment']

# Create a DataFrame to organize the data
df = pd.DataFrame({
    'Date': [reddit_data['date']],
    'Post Count': post_count,
    'Comment Count': comment_count,
    'Sentiment': sentiment
})

print(df)