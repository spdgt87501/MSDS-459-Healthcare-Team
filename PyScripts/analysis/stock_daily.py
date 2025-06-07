# This script processes and analyzes stock market data to calculate a sector-wide daily return
# This script loads the stock data from the JSONL files and creates a DataFrame with the stock data
# It then calculates the daily average return across tickers
# It averages these individual daily returns across all tickers to compute an overall "hc_sector_return" by day
# It saves this aggregated daily sector return data to a CSV file - healthcare_sector_returns.csv

import pandas as pd
import json
import os

# Get the script's directory and output path
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load all stock JSONL files again
def load_stock_jsonl(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

stock_dir = "stock_prices/stocks/output"
stock_files = [f for f in os.listdir(stock_dir) if f.endswith("_stock_data.jsonl")]

print("\nLoading stock data...")
print(f"Found {len(stock_files)} stock files:")
for file in stock_files:
    ticker = file.split("_")[0].upper()
    print(f"- {ticker}")

all_stocks = []
for file in stock_files:
    ticker = file.split("_")[0].upper()
    data = load_stock_jsonl(os.path.join(stock_dir, file))
    for entry in data:
        entry["ticker"] = ticker
    all_stocks.extend(data)
    print(f"Loaded {len(data)} records for {ticker}")

print(f"\nTotal stock data points: {len(all_stocks)}")

# Build DataFrame
stock_df = pd.DataFrame(all_stocks)
stock_df["date"] = pd.to_datetime(stock_df["Date"])
stock_df["close"] = stock_df["Close"]
stock_df = stock_df[["ticker", "date", "close"]]

print("\nStock data sample:")
print(stock_df.head())
print("\nStock data summary:")
print(stock_df.describe())

print("\nDate range:", stock_df["date"].min(), "to", stock_df["date"].max())
print("Number of unique trading days:", stock_df["date"].nunique())

# Calculate daily returns across tickers
daily_close = stock_df.groupby(["ticker", "date"])["close"].last().reset_index()
daily_close["return"] = daily_close.groupby("ticker")["close"].pct_change()

print("\nDaily returns sample:")
print(daily_close.head())

# Average across tickers to form sector-wide daily return
daily_avg = daily_close.groupby("date")["return"].mean().reset_index()
daily_avg.rename(columns={"return": "hc_sector_return"}, inplace=True)

print("\nSector-wide daily returns sample:")
print(daily_avg.head())

print("\nSector returns summary:")
print(daily_avg["hc_sector_return"].describe())

# Save to CSV for easy viewing
output_path = os.path.join(output_dir, "hc_sector_daily_returns.csv")
daily_avg.to_csv(output_path, index=False)
print(f"\nData has been saved to: {output_path}")