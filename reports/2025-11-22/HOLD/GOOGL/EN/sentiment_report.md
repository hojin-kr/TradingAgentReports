import pandas as pd
from datetime import date

def get_reddit_stock_info(curr_date, ticker):
    # Create a dictionary to store the data
    data = {}

    # Get the top posts from r/google
    url = f"https://www.reddit.com/r/google/top/.json?limit=100&t={curr_date}"
    response = requests.get(url)
    if response.status_code == 200:
        for post in response.json()["data"]["children"]:
            title = post["data"]["title"]
            date_posted = post["data"]["created_utc"]
            score = post["data"]["score"]

            # Store the data in the dictionary
            if ticker not in data:
                data[ticker] = []
            data[ticker].append({
                "date": date.strftime(date_posted, "%Y-%m-%d"),
                "title": title,
                "score": score
            })

    # Get the comments from r/google
    url = f"https://www.reddit.com/r/google/comments/.json?limit=100&t={curr_date}"
    response = requests.get(url)
    if response.status_code == 200:
        for comment in response.json()["data"]["children"]:
            author = comment["data"]["author"]
            text = comment["data"]["body"]
            date_posted = comment["data"]["created_utc"]

            # Store the data in the dictionary
            if ticker not in data:
                data[ticker] = []
            data[ticker].append({
                "date": date.strftime(date_posted, "%Y-%m-%d"),
                "author": author,
                "text": text
            })

    return pd.DataFrame(data[ticker])

# Call the function
df = get_reddit_stock_info("2025-11-22", "GOOGL")

print(df)