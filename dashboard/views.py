<<<<<<< HEAD
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
=======
from django.shortcuts import render
from django.http import JsonResponse
import yfinance as yf
from datetime import datetime, timedelta
from django.core.cache import cache
from news_scraper.news_fetcher import fetch_news
from sentiment_analysis.sentiment_analyzer import analyze_sentiment
from technical_analysis.views import fetch as fetch_technical_data
from django.views.decorators.http import require_POST
import requests
import json

def validate_stock_symbol(symbol):
    """Validate stock symbol by checking if data exists"""
    if not symbol:
        return False
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='1d')
        return not hist.empty
    except:
        return False

def get_proper_symbol(query):
    """Get valid stock symbol using yfinance search"""
    if not query or not query.strip():
        return 'TSLA'  # Default symbol
        
    query = query.upper().strip()
    
    # First try direct lookup
    if validate_stock_symbol(query):
        return query
        
    # Try yfinance search
    try:
        search_results = yf.Tickers(query)
        if search_results.tickers:
            return search_results.tickers[0].ticker
    except:
        pass
        
    suggestions = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'WMT']
    return None, {
        'error': f"'{query}' is not a valid stock symbol",
        'message': 'Please enter a valid ticker symbol',
        'suggestions': suggestions
    }

def price_data_view(request):
    try:
        symbol = get_proper_symbol(request.GET.get('symbol', 'TSLA'))
        
        # Get data for last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        stock = yf.Ticker(symbol)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            raise ValueError(f"No data available for symbol: {symbol}")
            
        data = {
            'symbol': symbol,
            'dates': hist.index.strftime('%Y-%m-%d').tolist(),
            'open': hist['Open'].tolist(),
            'high': hist['High'].tolist(),
            'low': hist['Low'].tolist(),
            'close': hist['Close'].tolist(),
            'volume': hist['Volume'].tolist()
        }
        return JsonResponse(data)
    except ValueError as e:
        return JsonResponse({'error': str(e), 'suggestions': ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'WMT']}, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f"Failed to fetch data: {str(e)}",
            'suggestions': ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'WMT']
        }, status=400)

def dashboard_view(request):
    query_input = request.GET.get('query', '').strip()
    symbol_result = get_proper_symbol(query_input)
    
    if isinstance(symbol_result, tuple):  # Error case
        query = 'TSLA'
        error_data = symbol_result[1]
    else:  # Valid symbol case
        query = symbol_result or 'TSLA'
        error_data = None
    cache_key = f'dashboard_data_{query}'
    
    # Get or initialize watchlist from session
    watchlist = request.session.get('watchlist', [])
    watchlist_symbols = [item['symbol'] for item in watchlist]
    
    # Try to get cached data first
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'dashboard/dashboard.html', cached_data)

    # Initialize data structures
    news_data = []
    sentiment_data = []
    technical_data = []
    errors = []

    # Helper function to convert sentiment label to score
    def get_sentiment_score(sentiment):
        if isinstance(sentiment, dict):
            return sentiment.get('score', 0)
        # Handle string sentiment labels
        sentiment_map = {
            'negative': -0.5,
            'neutral': 0,
            'positive': 0.5
        }
        return sentiment_map.get(sentiment.lower(), 0)

    # Fetch news data
    try:
        news_data = fetch_news(query)
        sentiment_data = [
            {
                "title": article['title'], 
                "sentiment": analyze_sentiment(article['content'])
            }
            for article in news_data
        ] if news_data else []
    except Exception as e:
        errors.append(f"News fetching error: {str(e)}")

    # Fetch technical data
    try:
        # Use loc to avoid chained assignment warnings
        stock = yf.Ticker(query)
        hist = stock.history(period="1mo")
        
        # Basic technical indicators without TA-Lib
        technical_data = []
        if not hist.empty:
            close_prices = hist['Close']
            sma_20 = close_prices.rolling(window=20).mean().iloc[-1]
            sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
            rsi = 100 - (100 / (1 + (close_prices.diff(1).clip(lower=0).rolling(14).mean() / 
                                   -close_prices.diff(1).clip(upper=0).rolling(14).mean()).iloc[-1]))
            
            technical_data = [
                {
                    'name': 'SMA 20',
                    'value': round(sma_20, 2),
                    'trend': 'up' if sma_20 > sma_50 else 'down',
                    'description': '20-day Simple Moving Average'
                },
                {
                    'name': 'SMA 50',
                    'value': round(sma_50, 2),
                    'trend': None,
                    'description': '50-day Simple Moving Average'
                },
                {
                    'name': 'RSI',
                    'value': round(rsi, 2),
                    'trend': 'overbought' if rsi > 70 else 'oversold' if rsi < 30 else None,
                    'description': 'Relative Strength Index (14-day)'
                }
            ]
            
    except Exception as e:
        errors.append(f"Technical analysis error: {str(e)}")
        technical_data = []

    # Prepare zipped data with news and sentiment only
    min_length = min(
        len(news_data), 
        len(sentiment_data)
    ) if all([news_data, sentiment_data]) else 0
    
    zipped_data = list(zip(
        news_data[:min_length], 
        sentiment_data[:min_length]
    )) if min_length > 0 else []

    # Get recommendation from technical analysis
    recommendation = "Hold"  # Default
    recommendation_details = {}
    try:
        tech_response = fetch_technical_data(request)
        if tech_response.status_code == 200:
            tech_data = tech_response.json()
            recommendation = tech_data.get('recommendation', 'Hold')
            recommendation_details = {
                'close_price': tech_data.get('close_price'),
                'sma_50': tech_data.get('sma_50'),
                'rsi': tech_data.get('rsi')
            }
    except Exception as e:
        errors.append(f"Recommendation error: {str(e)}")

    # Calculate sentiment-based recommendation
    sentiment_scores = [get_sentiment_score(s['sentiment']) for s in sentiment_data if s]
    avg_sentiment = sum(sentiment_scores)/len(sentiment_scores) if sentiment_scores else 0
    
    # Final recommendation combining technical and sentiment analysis
    final_recommendation = recommendation
    if avg_sentiment > 0.2 and recommendation == "Hold":
        final_recommendation = "Consider Buy"
    elif avg_sentiment < -0.2 and recommendation == "Hold":
        final_recommendation = "Consider Sell"

    context = {
        'zipped_data': zipped_data,
        'technical_data': technical_data if technical_data else {},
        'query': query,
        'errors': errors,
        'recommendation': final_recommendation,
        'recommendation_details': recommendation_details,
        'sentiment_score': avg_sentiment,
        'watchlist': watchlist,
        'watchlist_symbols': watchlist_symbols,
        'popular_stocks': ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'WMT'],
        'error_data': error_data
    }

    # Cache the results for 5 minutes
    cache.set(cache_key, context, 300)
    return render(request, 'dashboard/dashboard.html', context)

@require_POST
def update_watchlist(request):
    """Handle watchlist updates from the modal"""
    try:
        symbols = request.POST.getlist('symbols[]')
        watchlist = []
        
        for symbol in symbols:
            # Validate symbol
            symbol = get_proper_symbol(symbol)
            stock = yf.Ticker(symbol)
            hist = stock.history(period='1d')
            
            if not hist.empty:
                watchlist.append({
                    'symbol': symbol,
                    'price': hist['Close'].iloc[-1],
                    'change': (hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1] * 100
                })
        
        # Update session
        request.session['watchlist'] = watchlist
        return JsonResponse({'status': 'success', 'watchlist': watchlist})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
>>>>>>> 83a97cbb0df2e8e6be15a026c1e5c13abcd467c0
