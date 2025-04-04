from django.shortcuts import render
from django.http import JsonResponse
import yfinance as yf
from datetime import datetime, timedelta
from django.core.cache import cache
from news_scraper.news_fetcher import fetch_news
from sentiment_analysis.sentiment_analyzer import analyze_sentiment
from technical_analysis.analysis import fetch_stock_data, apply_indicators

# Mapping of common names to official ticker symbols
SYMBOL_MAPPING = {
    'APPLE': 'AAPL',
    'APPL': 'AAPL',
    'GOOGLE': 'GOOG',
    'MICROSOFT': 'MSFT',
    'TESLA': 'TSLA',
    'LTIMINDTREE': 'LTIM.NS',
    'LTIM': 'LTIM.NS'
    # Add more mappings as needed
}

def get_proper_symbol(query):
    """Convert common names to official ticker symbols"""
    query = query.upper()
    return SYMBOL_MAPPING.get(query, query)

def price_data_view(request):
    symbol = get_proper_symbol(request.GET.get('symbol', 'TSLA'))
    
    # Get data for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(start=start_date, end=end_date)
        
        data = {
            'dates': hist.index.strftime('%Y-%m-%d').tolist(),
            'open': hist['Open'].tolist(),
            'high': hist['High'].tolist(),
            'low': hist['Low'].tolist(),
            'close': hist['Close'].tolist()
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def dashboard_view(request):
    query = get_proper_symbol(request.GET.get('query', '').strip()) or 'TSLA'
    cache_key = f'dashboard_data_{query}'
    
    # Try to get cached data first
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'dashboard/dashboard.html', cached_data)

    # Initialize data structures
    news_data = []
    sentiment_data = []
    technical_data = []
    errors = []

    # Fetch news data
    try:
        news_data = fetch_news(query)
        sentiment_data = [
            {"title": article['title'], "sentiment": analyze_sentiment(article['content'])}
            for article in news_data
        ] if news_data else []
    except Exception as e:
        errors.append(f"News fetching error: {str(e)}")

    # Fetch technical data
    try:
        stock_data = fetch_stock_data(query)
        technical_data = apply_indicators(stock_data)
    except Exception as e:
        errors.append(f"Technical analysis error: {str(e)}")

    # Prepare zipped data with news and sentiment only
    min_length = min(
        len(news_data), 
        len(sentiment_data)
    ) if all([news_data, sentiment_data]) else 0
    
    zipped_data = list(zip(
        news_data[:min_length], 
        sentiment_data[:min_length]
    )) if min_length > 0 else []

    context = {
        'zipped_data': zipped_data,
        'technical_data': technical_data if technical_data else {},
        'query': query,
        'errors': errors,
    }

    # Cache the results for 5 minutes
    cache.set(cache_key, context, 300)
    
    return render(request, 'dashboard/dashboard.html', context)
