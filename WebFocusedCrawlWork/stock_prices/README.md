# Stock Data Fetcher

This project is a Python script to fetch stock data using a public API (e.g., Yahoo Finance or Alpha Vantage).

## Features
- Fetch current stock price for a given symbol
- Display the result in the terminal

## Setup
1. Ensure you have Python 3.8+ installed.
2. (Recommended) Create a virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage
Edit the script to specify the stock symbol you want to fetch, then run:
```powershell
python fetch_stock.py
```

## Notes
- You may need an API key for some data providers (e.g., Alpha Vantage).
- For Yahoo Finance, no API key is required if using the `yfinance` package.
