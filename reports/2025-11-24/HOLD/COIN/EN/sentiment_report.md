<|python_tag|>import requests
import json

def get_reddit_stock_info(curr_date, ticker):
    url = f"https://v6.reddit.com/r/stockmarket/comments/.json"
    headers = {
        "User-Agent": "StockMarketAnalysis",
        "Accept": "application/json"
    }
    params = {
        "limit": 100,
        "after": curr_date
    }

    response = requests.get(url, headers=headers, params=params)
    data = json.loads(response.text)["data"]["children"]

    sentiment_data = {}
    for post in data:
        try:
            post_data = json.loads(post["data"]["json"])
            if post_data["author"] == ticker.upper():
                if "Sentiment" in post_data["body"]:
                    sentiment = post_data["body"]["Sentiment"]
                    sentiment_data[post_data["created_utc"]] = {"sentiment": sentiment, "text": post_data["body"]}
        except (KeyError, IndexError):
            pass

    return sentiment_data

sentiment_data = get_reddit_stock_info("2025-11-24", 'COIN')
print(sentiment_data)