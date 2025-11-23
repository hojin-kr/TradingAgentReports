<|python_tag|>import pandas as pd

# Get the Reddit stock info
reddit_info = get_reddit_stock_info(curr_date="2025-11-23", ticker="MSFT")

# Extract the necessary data from the response
post_count = reddit_info['post_count']
comment_count = reddit_info['comment_count']
upvote_count = reddit_info['upvote_count']
downvote_count = reddit_info['downvote_count']

# Create a DataFrame to store the data
df = pd.DataFrame({
    'Date': [2025-11-23],
    'Post Count': [post_count],
    'Comment Count': [comment_count],
    'Upvote Count': [upvote_count],
    'Downvote Count': [downvote_count]
})

# Print the DataFrame
print(df)