from django.shortcuts import render
<<<<<<< HEAD
from .news_fetcher import fetch_news

def newsscraper(request):
    news_summary = ""
    
    if request.method == "POST":
        # Note: Topic parameter is no longer used but kept for form compatibility
        topic = request.POST.get("topic", "").strip()
        
        news_data = fetch_news()
        
        if not news_data:
            news_summary = "Error fetching news."
        else:
            news_summary = "\n\n".join(
                [f"{article['title']} (Source: {article['source']}) --> {article['content']}" 
                 for article in news_data]
            )
=======
import requests

def newsscraper(request):
    # API endpoint
    url = "https://newsapi.org/v2/everything"
    
    news_summary = ""
    
    if request.method == "POST":
        topic = request.POST.get("topic", "").strip()

        if not topic:
            news_summary = "No topic provided."
        else:
            params = {
                "q": topic,  # Correct variable name
                "apiKey": "fd21fc5968a346b2a43b91ff7a43e50f"  # Correct key name
            }
           
            response = requests.get(url, params=params)

            if response.status_code != 200:
                news_summary = "Error fetching news."
            else:
                # Convert response to JSON
                data = response.json()
                articles = data.get("articles", [])
                
                if articles:
                    news_summary = "\n\n".join([f"{article['title']} --> {article['description']}" for article in articles[:5]])
                else:
                    news_summary = "No relevant news found."

#      STRUCTURE OF SINGLE ARTICLE:
#       { 
#         "source": {"name": "The Verge"},
#         "title": "Cryptocurrency market sees massive surge",
#         "description": "The crypto market is booming...",
#         "url": "https://www.theverge.com/...",
#         "publishedAt": "2025-03-01T11:30:00Z"
#     }
>>>>>>> 83a97cbb0df2e8e6be15a026c1e5c13abcd467c0

    return render(request, "scraper.html", {"news": news_summary})
