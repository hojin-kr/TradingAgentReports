<|python_tag|>import requests
from bs4 import BeautifulSoup

def get_reddit_stock_info(curr_date, ticker):
    url = f"https://www.reddit.com/r/stocks/comments/?sort=newest"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/534.34'
    }
    params = {
        'limit': 100,
        'after': 'null',
        'sort': 'newest',
        'tagged': ticker
    }

    response = requests.get(url, headers=headers, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    posts = []
    for post in soup.find_all('div', class_='post'):
        try:
            title = post.find('a', class_='title').text.strip()
            score = post.find('div', class_='score').text.strip()
            comment_count = post.find('span', class_='comment-count').text.strip()
            link = post.find('a')['href']
        except:
            continue
        posts.append({
            'title': title,
            'score': score,
            'comment_count': comment_count,
            'link': link
        })

    return posts

posts = get_reddit_stock_info("2025-11-23", "PYPL")
for post in posts:
    print(post)