# This script analyzes the relationship between financial news sentiment and stock market performance
# It loads article data from three sources (CNBC, Investopedia, NewsAPI) containing pre-computed sentiment scores
# It aggregates article sentiment into a weekly sentiment ratio (proportion of positive articles)
# It calculates the average weekly return across all analyzed stock tickers
# It then calculates the correlation between the sentiment and the stock market performance
# It then saves the data to a CSV file - weekly_market_sentiment_with_returns.csv

import pandas as pd
import json
import os

# Get the script's directory and output path
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

# Load sentiment data
print("\nLoading sentiment data...")
cnbc_data = load_jsonl("CNBC_items_with_predictions.jl")
inv_data = load_jsonl("Investopedia_articles_with_predictions.jl")
newsapi_data = load_jsonl("NewsAPI_items_with_predictions.jl")

print(f"Loaded {len(cnbc_data)} CNBC articles")
print(f"Loaded {len(inv_data)} Investopedia articles")
print(f"Loaded {len(newsapi_data)} NewsAPI articles")

all_articles = cnbc_data + inv_data + newsapi_data
print(f"Total articles: {len(all_articles)}")

# Extract records with valid publication date and sentiment
records = []
for article in all_articles:
    pub_date = article.get("metadata", {}).get("publish_date")
    sentiment = article.get("predicted_label")
    if pub_date and sentiment is not None:
        records.append({
            "publish_date": pub_date,
            "sentiment": sentiment
        })

print(f"\nCreated {len(records)} valid sentiment records")

# Create DataFrame
df = pd.DataFrame(records)
df["publish_date"] = pd.to_datetime(df["publish_date"])

# Bucket into ISO weeks
df["week"] = df["publish_date"].dt.to_period("W").apply(lambda r: r.start_time)

# Aggregate by week
weekly_sentiment = df.groupby("week").agg(
    article_count=("sentiment", "count"),
    positive_count=("sentiment", lambda x: (x == 1).sum())
).reset_index()
weekly_sentiment["sentiment_ratio"] = weekly_sentiment["positive_count"] / weekly_sentiment["article_count"]

print("\nWeekly sentiment summary:")
print(weekly_sentiment.head())
print("\nSentiment date range:", weekly_sentiment["week"].min(), "to", weekly_sentiment["week"].max())

# Load stock data
print("\nLoading stock data...")
stock_dir = "stock_prices/stocks/output"
stock_files = [f for f in os.listdir(stock_dir) if f.endswith("_stock_data.jsonl")]
print(f"Found {len(stock_files)} stock files: {', '.join([f.split('_')[0] for f in stock_files])}")

# Parse all stock data
all_stocks = []
for file in stock_files:
    ticker = file.split("_")[0].upper()
    data = load_jsonl(os.path.join(stock_dir, file))
    for entry in data:
        entry["ticker"] = ticker
    all_stocks.extend(data)

print(f"Total stock data points: {len(all_stocks)}")

# Build stock DataFrame
stock_df = pd.DataFrame(all_stocks)
stock_df["date"] = pd.to_datetime(stock_df["Date"])
stock_df = stock_df[["ticker", "date", "Close"]]
stock_df = stock_df.rename(columns={"Close": "close"})

print("\nStock data sample:")
print(stock_df.head())
print("\nStock date range:", stock_df["date"].min(), "to", stock_df["date"].max())

# Compute weekly returns per ticker
stock_df["week"] = stock_df["date"].dt.to_period("W").apply(lambda r: r.start_time)
weekly_close = stock_df.groupby(["week", "ticker"])["close"].last().reset_index()

# Compute returns per ticker
weekly_close["return"] = weekly_close.groupby("ticker")["close"].pct_change()

print("\nWeekly stock returns sample:")
print(weekly_close.head())

# Average weekly return across all tickers
weekly_avg_return = weekly_close.groupby("week")["return"].mean().reset_index()
weekly_avg_return.rename(columns={"return": "avg_weekly_return"}, inplace=True)

print("\nAverage weekly returns sample:")
print(weekly_avg_return.head())

# Merge with sentiment data
merged = pd.merge(weekly_sentiment, weekly_avg_return, on="week", how="inner")

print("\nMerged data sample:")
print(merged.head())

print("\nSummary Statistics:")
print(f"Total number of articles: {len(df)}")
print(f"Date range: {df['publish_date'].min()} to {df['publish_date'].max()}")
print(f"Number of weeks: {len(weekly_sentiment)}")
print(f"Number of stocks analyzed: {len(stock_files)}")

# Calculate correlation between sentiment and returns
correlation = merged["sentiment_ratio"].corr(merged["avg_weekly_return"])
print(f"\nCorrelation between sentiment ratio and average weekly returns: {correlation:.3f}")

# Save to CSV for easy viewing

output_path = os.path.join(output_dir, "weekly_market_sentiment_with_returns.csv")
merged.to_csv(output_path, index=False)
print(f"\nData has been saved to: {output_path}")
