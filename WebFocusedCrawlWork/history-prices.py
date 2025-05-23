import yfinance as yf
import pandas as pd
import json
from datetime import datetime, timedelta
import time
from requests.exceptions import ConnectionError

def fetch_stock_data(tickers, start_date, end_date, max_retries=3, delay=5):
    for attempt in range(max_retries):
        try:
            data = yf.download(tickers, start=start_date, end=end_date)
            closing_prices = data['Close']
            return closing_prices
        except ConnectionError as e:
            print(f"Connection error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    print("Max retries exceeded. Please check your network connection and try again later.")
    return None

tickers = ["LLY", "UNH", "JNJ", "ABBV", "ABT", "MRK", "ISRG", "TMO", "AMGN", "BSX"]
end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")

closing_prices = fetch_stock_data(tickers, start_date, end_date, max_retries=5, delay=10)

if closing_prices is not None:
    try:
        stock_data = closing_prices.stack().reset_index()
        stock_data.columns = ['date', 'ticker', 'price']
        stock_data['date'] = stock_data['date'].dt.strftime('%Y-%m-%d')
        with open('healthcare_stock_prices.jl', 'w', encoding='utf-8') as f:
            for record in stock_data.to_dict(orient='records'):
                f.write(json.dumps(record) + '\n')
        print("Data saved to healthcare_stock_prices.jl")
    except Exception as e:
        print(f"Error processing or saving data: {e}")
else:
    print("Failed to fetch stock data after multiple attempts.")