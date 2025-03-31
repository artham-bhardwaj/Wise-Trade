# dashboard/views.py

from django.shortcuts import render
from news_scraper.news_fetcher import fetch_news  # Your news fetching function
from sentiment_analysis.sentiment_analyzer import analyze_sentiment
from technical_analysis.analysis import fetch_stock_data, apply_indicators
from itertools import zip_longest

def dashboard_view(request):
    query = request.GET.get('query', '').strip() or 'Tesla'  # Default query if nothing is provided

    # Fetch news articles based on the query
    news_data = fetch_news(query)

    # Perform sentiment analysis on fetched news articles
    sentiment_data = []
    for article in news_data:
        sentiment = analyze_sentiment(article['content'])
        sentiment_data.append({"title": article['title'], "sentiment": sentiment})

    # Fetch technical analysis data
    stock_data = fetch_stock_data(query)  # Replace with the stock symbol you want
    technical_analysis_results = apply_indicators(stock_data)

    context = {
        'news_data': news_data,
        'sentiment_data': sentiment_data,
        'technical_data': technical_analysis_results,
        'query': query,
    }

    return render(request, 'dashboard/dashboard.html', context)
