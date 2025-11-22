<|python_tag|>import requests

def get_reddit_stock_info(curr_date, ticker):
    url = f'https://v2.reddit.com/poll/fetch.json?limit=100&t={curr_date}&subreddit=' + ticker + '&type=simplepolls'
    headers = {
        'User-Agent': 'Stock Analysis Assistant'
    }
    response = requests.get(url, headers=headers)
    return response

requests.set_default_headers(headers={'User-Agent': 'Stock Analysis Assistant'})

response = get_reddit_stock_info("2025-11-22", "JPM")

print(response.json())