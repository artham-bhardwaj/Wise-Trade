# news_scraper/news_fetcher.py

import requests
<<<<<<< HEAD
from datetime import datetime

def fetch_news(stock_name):
    url = "https://api.marketaux.com/v1/news/all"
    params = {
        "symbols": stock_name,
        "filter_entities": "true",
        "language": "en",
        "api_token": "3QLWc1YYoTwGbjX0oDfztMrasVqHXVeug9MLVLgg"
=======

def fetch_news(topic):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "apiKey": "fd21fc5968a346b2a43b91ff7a43e50f",
        "sortBy": "publishedAt",
        "language": "en"
>>>>>>> 83a97cbb0df2e8e6be15a026c1e5c13abcd467c0
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    data = response.json()
<<<<<<< HEAD
    articles = data.get("data", [])

    news_data = []
    for article in articles[:5]:  # Limit to first 5 articles
        try:
            published_at = datetime.strptime(
                article['published_at'], 
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ).strftime("%Y-%m-%d %H:%M")
        except:
            published_at = "Unknown date"

        news_data.append({
            "title": article.get('title', 'No Title'),
            "content": article.get('description', 'No description available.'),
            "image_url": article.get('image_url'),
            "source": article.get('source'),
            "published_at": published_at,
            "url": article.get('url'),
            "entities": [
                {
                    "symbol": e.get('symbol'),
                    "sentiment": e.get('sentiment_score')
                } 
                for e in article.get('entities', [])
                if e.get('type') == 'equity'
            ]
        })
=======
    articles = data.get("articles", [])

    news_data = [
        {"title": article.get('title', 'No Title'), 
         "content": article.get('description', 'No description available.')}
        for article in articles[:5]  # Limit to the first 5 articles
    ]
    print(news_data,end='\n\n')
>>>>>>> 83a97cbb0df2e8e6be15a026c1e5c13abcd467c0
    return news_data
