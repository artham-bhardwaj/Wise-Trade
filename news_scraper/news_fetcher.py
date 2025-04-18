# news_scraper/news_fetcher.py

import requests
from datetime import datetime

def fetch_news(stock_name):
    url = "https://api.marketaux.com/v1/news/all"
    params = {
        "symbols": stock_name,
        "filter_entities": "true",
        "language": "en",
        "api_token": "3QLWc1YYoTwGbjX0oDfztMrasVqHXVeug9MLVLgg"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    data = response.json()
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
    return news_data
