# dashboard/views.py

from django.shortcuts import render
from news_scraper.news_fetcher import fetch_news
from sentiment_analysis.sentiment_analyzer import analyze_sentiment
from technical_analysis.analysis import fetch_stock_data, apply_indicators
from itertools import zip_longest
from .llm_utils import extract_stock_symbol

def dashboard_view(request):
    user_input = request.GET.get('stock_name', '').strip()
    stock_name = extract_stock_symbol(user_input) or 'TSLA'  # Fallback to TSLA

    # Fetch financial news articles
    news_data = fetch_news(stock_name)  # Pass the stock name to fetch news

    # Perform sentiment analysis on fetched news articles
    sentiment_data = []
    for article in news_data:
        sentiment = analyze_sentiment(article['content'])
        sentiment_data.append({
            "title": article['title'],
            "sentiment": sentiment,
            "symbols": [e['symbol'] for e in article.get('entities', [])]
        })

    # Fetch technical analysis data
    stock_data = fetch_stock_data(stock_name)  # Use the stock name from user input
    technical_analysis_results = apply_indicators(stock_data)

    # Combine news and sentiment data
    combined_news = list(zip_longest(news_data, sentiment_data))
    
    context = {
        'combined_news': combined_news,
        'technical_data': technical_analysis_results,
        'query': stock_name,
    }

    return render(request, 'dashboard/dashboard.html', context)
