from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

# Choose which news API to use
USE_GNEWS_API = True

if USE_GNEWS_API:
    from news_scraper.gnews import fetch_news
else:
    from news_scraper.marketAUX import fetch_news

from sentiment_analysis.sentiment_analyzer import analyze_sentiment
from technical_analysis.analysis import (
    fetch_stock_data,
    apply_indicators,
    StockDataFetchError,
    predict_price_movement
)

from metadata_analysis.analysis import get_metadata_for_stock


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
            return redirect('login')
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


from metadata_analysis.models import Company, Asset, Event, StockImpact  # Adjust import if needed

@login_required(login_url='login')
def dashboard_view(request):
    stock_name = request.GET.get('stock_name', '').strip().upper() or 'AMZN'

    error_message = None
    combined_news = []
    technical_analysis_results = []
    current_price = None
    predicted_price = None
    price_trend = "Unknown"
    metadata_analysis_results = []

    company_obj = None
    matched_assets = []
    related_events = []
    stock_impact_info = []

    # 0. Fetch company from DB
    try:
        company_obj = Company.objects.get(ticker_symbol=stock_name)
        matched_assets = Asset.objects.filter(company=company_obj)
    except Company.DoesNotExist:
        company_obj = None
        matched_assets = []
        logger.warning(f"No company found with ticker symbol '{stock_name}'")

    # 1. Fetch news and analyze sentiment
    try:
        news_data = fetch_news(stock_name)
        sentiment_data = []
        for article in news_data:
            sentiment = analyze_sentiment(article.get('content', ''))
            sentiment_data.append({
                "title": article.get('title', ''),
                "sentiment": sentiment,
            })
        combined_news = list(zip(news_data, sentiment_data))
    except Exception as e:
        logger.error(f"Error fetching news or sentiment for '{stock_name}': {e}")
        error_message = "Could not fetch news data."

    # 2. Technical analysis and price prediction
    try:
        stock_data = fetch_stock_data(stock_name)
        technical_raw = apply_indicators(stock_data)

        if isinstance(technical_raw, dict):
            technical_analysis_results = [
                {
                    "name": key,
                    "value": f"{val['value']:.2f}" if isinstance(val['value'], (int, float)) else val['value'],
                    "trend": val.get('trend', 'N/A'),
                    "description": val.get('description', '')
                }
                for key, val in technical_raw.items()
            ]
        elif isinstance(technical_raw, list):
            technical_analysis_results = [
                {
                    "name": item.get("name", "N/A"),
                    "value": f"{item['value']:.2f}" if isinstance(item.get("value"), (int, float)) else item.get("value", "N/A"),
                    "trend": item.get("trend", "N/A"),
                    "description": item.get("description", "")
                }
                for item in technical_raw
            ]

        current_price = round(stock_data['Close'][-1], 2)

        prediction = predict_price_movement(stock_name)
        if isinstance(prediction, dict):
            predicted_price = prediction.get('price')
            price_trend = prediction.get('trend', 'Unknown')
        else:
            predicted_price = None
            price_trend = prediction

        if current_price is not None:
            current_price = f"{current_price:.2f}"
        if predicted_price is not None:
            try:
                predicted_price = f"{float(predicted_price):.2f}"
            except Exception:
                predicted_price = None

    except StockDataFetchError as e:
        logger.error(f"Stock data fetch error for '{stock_name}': {e}")
        error_message = str(e)
    except Exception as e:
        logger.error(f"Unexpected error fetching stock data for '{stock_name}': {e}")
        error_message = "An unexpected error occurred while fetching stock data."

    # 3. Metadata analysis
    try:
        metadata_analysis_results = get_metadata_for_stock(stock_name)
        if metadata_analysis_results is None:
            metadata_analysis_results = []
        elif not isinstance(metadata_analysis_results, (list, dict)):
            metadata_analysis_results = [metadata_analysis_results]
    except Exception as e:
        logger.error(f"Error during metadata analysis for '{stock_name}': {e}")
        metadata_analysis_results = []

    # 4. Events matched to assets
    try:
        if matched_assets:
            related_events = Event.objects.filter(matched_assets__in=matched_assets).distinct()
    except Exception as e:
        logger.error(f"Error fetching related events for '{stock_name}': {e}")
        related_events = []

    # 5. Stock impact predictions from events for this company
    try:
        if company_obj:
            stock_impact_info = StockImpact.objects.filter(company=company_obj).select_related('event')
            # Prepare a list of dicts with event and predicted impact for easier template use
            stock_impact_info = [
                {
                    'event_title': impact.event.title,
                    'event_date': impact.event.date,
                    'predicted_impact': impact.get_predicted_impact_display(),  # shows emoji + label
                    'confidence_score': f"{impact.confidence_score:.2f}",
                }
                for impact in stock_impact_info
            ]
    except Exception as e:
        logger.error(f"Error fetching stock impact info for '{stock_name}': {e}")
        stock_impact_info = []

    context = {
        'query': stock_name,
        'company_info': company_obj,
        'matched_assets': matched_assets,
        'related_events': related_events,
        'stock_impact_info': stock_impact_info,  # This now contains formatted impact info
        'combined_news': combined_news,
        'technical_data': technical_analysis_results,
        'error_message': error_message,
        'current_price': current_price,
        'predicted_price': predicted_price,
        'price_trend': price_trend,
        'metadata_data': metadata_analysis_results,
    }

    return render(request, 'dashboard/dashboard.html', context)


def price_data_api(request):
    symbol = request.GET.get('symbol', '').strip()
    interval = request.GET.get('interval', '1m').strip()

    if not symbol:
        return JsonResponse({'error': 'Symbol parameter is required'}, status=400)

    try:
        stock_data = fetch_stock_data(symbol, interval=interval)
        data = {
            'dates': stock_data.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'open': stock_data['Open'].tolist(),
            'high': stock_data['High'].tolist(),
            'low': stock_data['Low'].tolist(),
            'close': stock_data['Close'].tolist(),
        }
        return JsonResponse(data)
    except StockDataFetchError as e:
        logger.error(f"Rate limit error fetching price data for symbol '{symbol}': {e}")
        return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=429)
    except Exception as e:
        logger.error(f"Error fetching price data for symbol '{symbol}': {e}")
        return JsonResponse({'error': 'Failed to fetch price data'}, status=500)
