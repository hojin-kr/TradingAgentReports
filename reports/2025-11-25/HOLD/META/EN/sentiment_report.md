import requests
import json

def get_reddit_stock_info(curr_date, ticker):
    url = f"https://api.pushshift.io/reddit/subreddit/comments?limit=100&since={curr_date}&before={curr_date}&sort=score&order=desc&username=&body=" + ticker
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    return data

data = get_reddit_stock_info("2025-11-25", "META")

comments = []
for comment in data['data']:
    comments.append(comment['body'])

def analyze_comments(comments):
    sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
    for comment in comments:
        if 'positive' in comment.lower():
            sentiment['positive'] += 1
        elif 'negative' in comment.lower():
            sentiment['negative'] += 1
        else:
            sentiment['neutral'] += 1
    return sentiment

sentiment = analyze_comments(comments)

print("Sentiment Analysis:")
print(f"Positive Sentiment: {sentiment['positive']}")
print(f"Negative Sentiment: {sentiment['negative']}")
print(f"Neutral Sentiment: {sentiment['neutral']}")

def get_news(ticker):
    # This function would hit a news API to get the latest news about the company
    # For this example, we'll just use a hardcoded list of news articles
    news = [
        {"title": "Meta to Lay Off 11,000 Employees", "date": "2022-09-19"},
        {"title": "Meta's New AI Strategy Raises Concerns About Job Displacement", "date": "2022-10-15"},
        {"title": "Meta's Q3 Earnings Beat Expectations, But Stock Still Slumps", "date": "2022-11-18"}
    ]
    return news

news = get_news("META")

print("\nNews Analysis:")
for article in news:
    print(f"{article['title']} - {article['date']}")


def main():
    global data
    global comments
    global sentiment
    global news


    # Get Reddit comment data for the given date and ticker
    data = get_reddit_stock_info("2025-11-25", "META")


    # Extract comments from the data
    comments = []
    for comment in data['data']:
        comments.append(comment['body'])


    # Analyze sentiment of the comments
    sentiment = analyze_comments(comments)


    # Get news articles about the company
    news = get_news("META")


    # Print sentiment analysis and news articles
    print("\nSentiment Analysis:")
    print(f"Positive Sentiment: {sentiment['positive']}")
    print(f"Negative Sentiment: {sentiment['negative']}")
    print(f"Neutral Sentiment: {sentiment['neutral']}")

    print("\nNews Analysis:")
    for article in news:
        print(f"{article['title']} - {article['date']}")


if __name__ == "__main__":
    main()