from django.shortcuts import render
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

    return render(request, "scraper.html", {"news": news_summary})
