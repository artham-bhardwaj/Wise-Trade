import yfinance as yf
import pandas as pd
import pandas_ta as ta
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
