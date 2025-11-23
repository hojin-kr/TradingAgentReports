<|python_tag|>import requests
import json

def get_reddit_stock_info(curr_date, ticker):
    url = f"https://v6.reddit.com/poll/fetch.json?t={ticker}&since={curr_date}"
    headers = {
        "User-Agent": "Stock Analysis Assistant"
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    polls = data['data']['children']
    sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
    for poll in polls:
        voting_info = poll['data']['voting_info']
        score = voting_info['score']
        if score > 100 and score < 300:
            sentiment['positive'] += 1
        elif score > 200 and score < 400:
            sentiment['negative'] += 1
        else:
            sentiment['neutral'] += 1
    return sentiment

sentiment = get_reddit_stock_info("2025-11-23", "MU")
print(sentiment)