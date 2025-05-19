import json
import logging
import warnings
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpRequest

warnings.filterwarnings('ignore', category=FutureWarning)
logger = logging.getLogger(__name__)


def fetch(request):
    stock_symbol = request.GET.get('symbol', 'AAPL')  # Default to AAPL if no symbol provided
    try:
        data = yf.download(stock_symbol, period="3mo", interval="1d")
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
        }
    }

    response_data = {k: v for k, v in response_data.items() if v is not None}
    response_data['indicators'] = {k: v for k, v in response_data['indicators'].items() if v is not None}

    return JsonResponse(response_data)


# ✅ NEW VIEW for rendering data dynamically
def technical_analysis_page(request: HttpRequest):
    symbol = request.GET.get('symbol', 'AAPL')
    request.GET = request.GET.copy()
    request.GET['symbol'] = symbol

    response = fetch(request)
    data = {}

    if response.status_code == 200:
        data = json.loads(response.content)

    return render(request, 'dashboard/technical_analysis.html', {
        'data': data,
        'symbol': symbol
    })
