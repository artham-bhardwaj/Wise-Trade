import yfinance as yf
import pandas as pd
import pandas_ta as ta
<<<<<<< HEAD
from django.http import HttpResponse

def fetch(request):
    # Fetch stock data
    data = yf.download("AAPL", period="3mo", interval="1d")

    # Flatten MultiIndex if it exists
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = ['_'.join(col).strip() for col in data.columns.values]

    # Apply all technical indicators
    data.ta.strategy("all")

    print(data.head())  # Debugging

    return HttpResponse("Fetched data successfully!")
=======
from django.http import JsonResponse
import warnings
import logging
warnings.filterwarnings('ignore', category=FutureWarning)

logger = logging.getLogger(__name__)

def fetch(request):
    """
    Fetch stock data and technical indicators for a given symbol.
    
    Args:
        request: Django request object containing 'symbol' parameter
        
    Returns:
        JsonResponse containing:
        - Current price data
        - Technical indicators (SMA, RSI, MACD, Bollinger Bands)
        - Trading recommendation with confidence score
    """
    # Get stock symbol from request
    stock_symbol = request.GET.get('symbol', 'AAPL')  # Default to AAPL if no symbol provided
    
    # Fetch stock data with error handling
    try:
        data = yf.download(stock_symbol, period="3mo", interval="1d")
        if data.empty:
            raise ValueError("No data returned for symbol")
            
        # Flatten MultiIndex if it exists
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]

        # Validate we have required columns
        if 'Close' not in data.columns:
            raise KeyError("Missing 'Close' price column")
            
        # Calculate basic indicators with error handling
        close_price = float(data['Close'].iloc[-1])
        sma_50 = float(data['Close'].rolling(50).mean().iloc[-1])
        
    except Exception as e:
        logger.error(f"Failed to process {stock_symbol}: {str(e)}")
        return JsonResponse({
            'error': f"Could not process stock data: {str(e)}",
            'symbol': stock_symbol
        }, status=400)
    
    # Calculate RSI with fallback
    try:
        rsi_series = data['Close'].ta.rsi()
        rsi = float(rsi_series.iloc[-1]) if not rsi_series.empty else None
    except (AttributeError, TypeError, IndexError) as e:
        logger.warning(f"RSI calculation failed for {stock_symbol}: {str(e)}")
        rsi = None
        
    # Calculate MACD with fallback
    try:
        macd = data.ta.macd().iloc[-1].to_dict()
    except (AttributeError, TypeError) as e:
        logger.warning(f"MACD calculation failed: {str(e)}")
        macd = None
        
    # Calculate Bollinger Bands with fallback
    try:
        bb = data.ta.bbands()
        bb_pct = bb.iloc[-1]['BBP_5_2.0'] if bb is not None else None
    except (AttributeError, TypeError, KeyError) as e:
        logger.warning(f"Bollinger Bands calculation failed: {str(e)}")
        bb_pct = None
    
    # Enhanced recommendation logic
    recommendation = "Hold"
    confidence = 50  # Base confidence
    
    # Price vs SMA analysis
    price_vs_sma = close_price / sma_50
    if price_vs_sma > 1.05:
        confidence += 15
    elif price_vs_sma < 0.95:
        confidence -= 15
        
    # RSI analysis
    if rsi < 30:
        confidence += 20
    elif rsi > 70:
        confidence -= 20
        
    # Final recommendation
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
    
    # Remove None values from response
    response_data = {k: v for k, v in response_data.items() if v is not None}
    response_data['indicators'] = {k: v for k, v in response_data['indicators'].items() if v is not None}
    
    return JsonResponse(response_data)
>>>>>>> 83a97cbb0df2e8e6be15a026c1e5c13abcd467c0
