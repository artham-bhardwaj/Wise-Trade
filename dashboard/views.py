# dashboard/views.py

from django.shortcuts import render
# Set this flag to True to use GNews API, False to use MarketAux API
USE_GNEWS_API = True

if USE_GNEWS_API:
    from news_scraper.gnews import fetch_news
else:
    from news_scraper.marketAUX import fetch_news
from sentiment_analysis.sentiment_analyzer import analyze_sentiment
from technical_analysis.analysis import fetch_stock_data, apply_indicators
from itertools import zip_longest
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def dashboard_view(request):
    stock_name = request.GET.get('stock_name', '').strip() or 'TSLA'  # Fallback to TSLA

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

def price_data_api(request):
    symbol = request.GET.get('symbol', '').strip()
    if not symbol:
        return JsonResponse({'error': 'Symbol parameter is required'}, status=400)
    try:
        # Fetch intraday data for live candlestick chart with 1-minute interval
        stock_data = fetch_stock_data(symbol, interval='1m')
        # Prepare data for candlestick chart
        data = {
            'dates': stock_data.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'open': stock_data['Open'].tolist(),
            'high': stock_data['High'].tolist(),
            'low': stock_data['Low'].tolist(),
            'close': stock_data['Close'].tolist(),
        }
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error fetching price data for symbol {symbol}: {e}")
        return JsonResponse({'error': 'Failed to fetch price data'}, status=500)
