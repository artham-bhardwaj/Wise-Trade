from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
# Set this flag to True to use GNews API, False to use MarketAux API
USE_GNEWS_API = True

if USE_GNEWS_API:
    from news_scraper.gnews import fetch_news
else:
    from news_scraper.marketAUX import fetch_news
from sentiment_analysis.sentiment_analyzer import analyze_sentiment
from technical_analysis.analysis import fetch_stock_data, apply_indicators, StockDataFetchError
from itertools import zip_longest
import logging

logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required

from django.shortcuts import redirect

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')



def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Signup successful. Please log in.")
            return redirect('login')  # 👈 Redirect to login instead of dashboard
        else:
            messages.error(request, "Signup failed. Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'dashboard/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, "Login successful.")
            return redirect('dashboard')
        else:
            messages.error(request, "Login failed. Please check your username and password.")
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')

@login_required(login_url='login')
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
    try:
        stock_data = fetch_stock_data(stock_name)  # Use the stock name from user input
        technical_analysis_results = apply_indicators(stock_data)
    except StockDataFetchError as e:
        logger.error(f"Error fetching stock data for {stock_name}: {e}")
        technical_analysis_results = None
        error_message = str(e)
    except Exception as e:
        logger.error(f"Unexpected error fetching stock data for {stock_name}: {e}")
        technical_analysis_results = None
        error_message = "An unexpected error occurred while fetching stock data."
    else:
        error_message = None

    # Combine news and sentiment data
    combined_news = list(zip_longest(news_data, sentiment_data))
    
    context = {
        'combined_news': combined_news,
        'technical_data': technical_analysis_results,
        'query': stock_name,
        'error_message': error_message,
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
    except StockDataFetchError as e:
        logger.error(f"Rate limit error fetching price data for symbol {symbol}: {e}")
        return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=429)
    except Exception as e:
        logger.error(f"Error fetching price data for symbol {symbol}: {e}")
        return JsonResponse({'error': 'Failed to fetch price data'}, status=500)
