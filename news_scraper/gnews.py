import json
import urllib.request

def fetch_news(stock_name=None, topic=None):
    apikey = "899e417c0de356032f98b22d1a444b82"
    query = stock_name if stock_name else topic
    if not query:
        return []

    url = f"https://gnews.io/api/v4/search?q={query}&lang=en&country=us&max=10&apikey={apikey}"

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
            articles = data.get("articles", [])
            news_data = []
            for article in articles:
                news_data.append({
                    "title": article.get("title", "No Title"),
                    "content": article.get("description", "No description available."),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "published_at": article.get("publishedAt", "Unknown date"),
                    "url": article.get("url", ""),
                    "entities": []  # GNews API does not provide entities in this response
                })
            return news_data
    except Exception as e:
        print(f"Error fetching news from GNews API: {e}")
        return []
