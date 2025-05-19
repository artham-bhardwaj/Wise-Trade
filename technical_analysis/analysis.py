import yfinance as yf
import pandas as pd
import pandas_ta as ta
from yfinance.exceptions import YFRateLimitError
import time

class StockDataFetchError(Exception):
    pass

# Simple in-memory cache dictionary
_cache = {}
_cache_expiry = 300  # cache expiry time in seconds (5 minutes)

def fetch_stock_data(stock_name, interval='1m'):
    """
    Fetch historical stock data from Yahoo Finance with caching.
    Default interval is 1 minute ('1m') for live data, can be set to other intervals like '5m', '15m', '1d'.
    Returns a DataFrame with OHLCV data.
    """
    cache_key = f"{stock_name}_{interval}"
    current_time = time.time()

    # Check cache
    if cache_key in _cache:
        cached_data, timestamp = _cache[cache_key]
        if current_time - timestamp < _cache_expiry:
            return cached_data

    ticker = yf.Ticker(stock_name)
    try:
        if interval == '1d':
            df = ticker.history(period="6mo", interval=interval)
        else:
            # For intraday, fetch last 7 days max
            df = ticker.history(period="7d", interval=interval)
        if df.empty:
            raise ValueError(f"No data found for stock symbol: {stock_name} with interval {interval}")

        # Store in cache
        _cache[cache_key] = (df, current_time)

        return df
    except YFRateLimitError as e:
        raise StockDataFetchError("Rate limit exceeded for Yahoo Finance API. Please try again later.") from e

def apply_indicators(stock_data):
    """
    Apply common technical indicators to the stock_data DataFrame.
    Returns a list of dictionaries with indicator name, value, trend, and description.
    """
    df = stock_data.copy()

    # Simple Moving Average (SMA) 50
    df['SMA_50'] = ta.sma(df['Close'], length=50)
    # Exponential Moving Average (EMA) 20
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    # Relative Strength Index (RSI) 14
    df['RSI_14'] = ta.rsi(df['Close'], length=14)
    # Moving Average Convergence Divergence (MACD)
    macd = ta.macd(df['Close'])
    df = pd.concat([df, macd], axis=1)

    latest = df.iloc[-1]

    indicators = [
        {
            "name": "SMA 50",
            "value": round(latest['SMA_50'], 2) if pd.notna(latest['SMA_50']) else None,
            "trend": "up" if latest['Close'] > latest['SMA_50'] else "down",
            "description": "Simple Moving Average over 50 periods"
        },
        {
            "name": "EMA 20",
            "value": round(latest['EMA_20'], 2) if pd.notna(latest['EMA_20']) else None,
            "trend": "up" if latest['Close'] > latest['EMA_20'] else "down",
            "description": "Exponential Moving Average over 20 periods"
        },
        {
            "name": "RSI 14",
            "value": round(latest['RSI_14'], 2) if pd.notna(latest['RSI_14']) else None,
            "trend": "up" if latest['RSI_14'] > 50 else "down",
            "description": "Relative Strength Index over 14 periods"
        },
        {
            "name": "MACD",
            "value": round(latest['MACD_12_26_9'], 2) if pd.notna(latest['MACD_12_26_9']) else None,
            "trend": "up" if latest['MACD_12_26_9'] > latest['MACDs_12_26_9'] else "down",
            "description": "Moving Average Convergence Divergence"
        },
        {
            "name": "Closing Price",
            "value": round(latest['Close'], 2),
            "trend": None,
            "description": "Latest closing price"
        }
    ]

    return indicators
