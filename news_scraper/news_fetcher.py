# news_scraper/news_fetcher.py

import requests

def fetch_news(topic):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "apiKey": "fd21fc5968a346b2a43b91ff7a43e50f",
        "sortBy": "publishedAt",
        "language": "en"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    data = response.json()
    articles = data.get("articles", [])

    news_data = [
        {"title": article.get('title', 'No Title'), 
         "content": article.get('description', 'No description available.')}
        for article in articles[:5]  # Limit to the first 5 articles
    ]
    print(news_data,end='\n\n')
    return news_data
