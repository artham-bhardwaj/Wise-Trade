import json
import logging
import warnings
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpRequest
from sklearn.linear_model import LinearRegression
import numpy as np

warnings.filterwarnings('ignore', category=FutureWarning)
logger = logging.getLogger(__name__)


def fetch(request):
    stock_symbol = request.GET.get('symbol', 'AAPL')  # Default to AAPL if no symbol provided
    try:
        data = yf.download(stock_symbol, period="3mo", interval="1d")
        logger.debug(f"Fetched data for {stock_symbol}: {data.shape} rows, columns: {list(data.columns)}")
        if data.empty:
            raise ValueError("No data returned for symbol")

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]

        if 'Close' not in data.columns:
            raise KeyError("Missing 'Close' price column")

        close_price = float(data['Close'].iloc[-1])
        sma_50 = float(data['Close'].rolling(50).mean().iloc[-1])

    except Exception as e:
        logger.error(f"Failed to process {stock_symbol}: {str(e)}")
        return JsonResponse({
            'error': f"Could not process stock data: {str(e)}",
            'symbol': stock_symbol
        }, status=400)

    try:
        rsi_series = data['Close'].ta.rsi()
        rsi = float(rsi_series.iloc[-1]) if not rsi_series.empty else None
    except Exception as e:
        logger.warning(f"RSI calculation failed for {stock_symbol}: {str(e)}")
        rsi = None

    try:
        macd = data.ta.macd().iloc[-1].to_dict()
    except Exception as e:
        logger.warning(f"MACD calculation failed: {str(e)}")
        macd = None

    try:
        bb = data.ta.bbands()
        bb_pct = bb.iloc[-1]['BBP_5_2.0'] if bb is not None else None
    except Exception as e:
        logger.warning(f"Bollinger Bands calculation failed: {str(e)}")
        bb_pct = None

    recommendation = "Hold"
    confidence = 50
    price_vs_sma = close_price / sma_50
    if price_vs_sma > 1.05:
        confidence += 15
    elif price_vs_sma < 0.95:
        confidence -= 15

    if rsi is not None:
        if rsi < 30:
            confidence += 20
        elif rsi > 70:
            confidence -= 20

    if confidence >= 70:
        recommendation = "Strong Buy" if confidence > 85 else "Buy"
    elif confidence <= 30:
        recommendation = "Strong Sell" if confidence < 15 else "Sell"

    # Predictive Model: Linear Regression on last 60 days (list of predicted prices)
    predicted_prices = []
    try:
        closing_prices = data['Close'].dropna().values[-60:]  # Last 60 days
        X = np.arange(len(closing_prices)).reshape(-1, 1)
        y = closing_prices.reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)

        future_days = 5
        future_X = np.arange(len(closing_prices), len(closing_prices) + future_days).reshape(-1, 1)
        future_preds = model.predict(future_X)

        predicted_prices = [round(float(p), 2) for p in future_preds]
    except Exception as e:
        logger.warning(f"Price prediction failed: {str(e)}")
        predicted_prices = []

    response_data = {
        'symbol': stock_symbol,
        'close_price': close_price,
        'sma_50': sma_50,
        'rsi': rsi,
        'recommendation': recommendation,
        'confidence': confidence,
        'indicators': {
            'SMA_50': sma_50,
            'RSI': rsi,
            'MACD': macd,
            'Bollinger_%B': bb_pct
        },
        'predicted_prices': predicted_prices  # List of predicted prices
    }

    # Remove None values
    response_data = {k: v for k, v in response_data.items() if v is not None}
    response_data['indicators'] = {k: v for k, v in response_data['indicators'].items() if v is not None}

    return JsonResponse(response_data)


# New function to predict price movement: returns (trend, predicted_price)
def predict_price_movement(stock_symbol):
    try:
        data = yf.download(stock_symbol, period="3mo", interval="1d")
        closing_prices = data['Close'].dropna().values[-60:]
        X = np.arange(len(closing_prices)).reshape(-1, 1)
        y = closing_prices.reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)

        future_X = np.array([[len(closing_prices)]])  # predict next day
        predicted_price = model.predict(future_X)[0][0]
        print("predicted_price is ", predicted_price)
        current_price = closing_prices[-1]
        if predicted_price > current_price * 1.01:
            return "Up", round(predicted_price, 2)
        elif predicted_price < current_price * 0.99:
            return "Down", round(predicted_price, 2)
        else:
            return "No change", round(predicted_price, 2)
    except Exception as e:
        logger.warning(f"Price prediction failed: {str(e)}")
        return "Unknown", None


# Updated view to render the technical analysis page with predictions
def technical_analysis_page(request: HttpRequest):
    symbol = request.GET.get('symbol', 'AAPL')
    request.GET = request.GET.copy()
    request.GET['symbol'] = symbol

    response = fetch(request)
    data = {}

    if response.status_code == 200:
        data = json.loads(response.content)

    # Get price trend and predicted price
    price_trend, predicted_price = predict_price_movement(symbol)

    return render(request, 'dashboard/technical_analysis.html', {
        'data': data,
        'symbol': symbol,
        'predicted_prices': data.get('predicted_prices', []),
        'price_trend': price_trend,
        'predicted_price': predicted_price
    })
