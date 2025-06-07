# This script builds an XGBoost prediction model using daily stock returns and sentiment data
# It uses historical daily returns and sentiment data to predict future returns
# Features include: sentiment ratio, lagged returns, and technical indicators

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score
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

# Create sentiment DataFrame
sentiment_df = pd.DataFrame(records)
sentiment_df["publish_date"] = pd.to_datetime(sentiment_df["publish_date"])

# Aggregate sentiment by day
daily_sentiment = sentiment_df.groupby(sentiment_df["publish_date"].dt.date).agg(
    article_count=("sentiment", "count"),
    positive_count=("sentiment", lambda x: (x == 1).sum())
).reset_index()
daily_sentiment["sentiment_ratio"] = daily_sentiment["positive_count"] / daily_sentiment["article_count"]
daily_sentiment["publish_date"] = pd.to_datetime(daily_sentiment["publish_date"])

# Load stock data
print("\nLoading stock data...")
stock_dir = "stock_prices/stocks/output"
stock_files = [f for f in os.listdir(stock_dir) if f.endswith("_stock_data.jsonl")]

all_stocks = []
for file in stock_files:
    ticker = file.split("_")[0].upper()
    data = load_jsonl(os.path.join(stock_dir, file))
    for entry in data:
        entry["ticker"] = ticker
    all_stocks.extend(data)

# Build stock DataFrame
stock_df = pd.DataFrame(all_stocks)
stock_df["date"] = pd.to_datetime(stock_df["Date"])
# Filter out future dates
current_date = pd.Timestamp.now()
stock_df = stock_df[stock_df["date"] <= current_date]
stock_df = stock_df[["ticker", "date", "Close"]]
stock_df = stock_df.rename(columns={"Close": "close"})

# Calculate daily returns per ticker
daily_close = stock_df.groupby(["date", "ticker"])["close"].last().reset_index()
daily_close["return"] = daily_close.groupby("ticker")["close"].pct_change()

# Average daily return across all tickers
daily_avg_return = daily_close.groupby("date")["return"].mean().reset_index()
daily_avg_return.rename(columns={"return": "avg_daily_return"}, inplace=True)

print("\nStock data summary:")
print("Date range in stock data:", daily_avg_return['date'].min(), "to", daily_avg_return['date'].max())
print("Number of unique dates in stock data:", daily_avg_return['date'].nunique())

# Merge sentiment and returns data
merged = pd.merge(daily_sentiment, daily_avg_return, 
                 left_on="publish_date", 
                 right_on="date", 
                 how="inner")

print("\nMerged data summary:")
print("Date range in merged data:", merged['publish_date'].min(), "to", merged['publish_date'].max())
print("Number of unique dates in merged data:", merged['publish_date'].nunique())
print("Number of rows in merged data:", len(merged))

# Create features with reduced window sizes
def create_features(df):
    # Lagged returns
    df['return_lag2'] = df['avg_daily_return'].shift(2)
    df['return_lag3'] = df['avg_daily_return'].shift(3)
    
    # Rolling statistics
    df['return_ma5'] = df['avg_daily_return'].rolling(window=5).mean()
    
    # Sentiment features
    df['sentiment_ma3'] = df['sentiment_ratio'].rolling(window=3).mean()
    
    # Target variable (next day's return)
    df['target'] = df['avg_daily_return'].shift(-1)
    
    return df

# Create features
feature_columns = ['sentiment_ratio', 'return_lag2', 'return_lag3',
                  'return_ma5', 'sentiment_ma3']

featured_df = create_features(merged)

# Drop rows with NaN values
featured_df = featured_df.dropna()

print("\nFinal data shape:", featured_df.shape)
print("\nSample of the data:")
print(featured_df[feature_columns].head())

# Prepare features and target
X = featured_df[feature_columns]
y = featured_df['target']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Create and train XGBoost model
print("\nTraining XGBoost model...")
model = xgb.XGBRegressor(
    objective='reg:squarederror',
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)

# Perform time series cross-validation
n_splits = 5
tscv = TimeSeriesSplit(n_splits=n_splits)
cv_scores = []

print("\nPerforming time series cross-validation...")
for train_idx, val_idx in tscv.split(X):
    X_train_cv, X_val_cv = X.iloc[train_idx], X.iloc[val_idx]
    y_train_cv, y_val_cv = y.iloc[train_idx], y.iloc[val_idx]
    
    # Train model on this fold
    model.fit(X_train_cv, y_train_cv)
    
    # Make predictions
    val_pred = model.predict(X_val_cv)
    
    # Calculate metrics
    val_rmse = np.sqrt(mean_squared_error(y_val_cv, val_pred))
    val_r2 = r2_score(y_val_cv, val_pred)
    
    cv_scores.append({
        'rmse': val_rmse,
        'r2': val_r2
    })

# Calculate average CV scores
avg_rmse = np.mean([score['rmse'] for score in cv_scores])
avg_r2 = np.mean([score['r2'] for score in cv_scores])

print("\nCross-validation Results:")
print(f"Average RMSE across {n_splits} folds: {avg_rmse:.4f}")
print(f"Average R² across {n_splits} folds: {avg_r2:.4f}")

# Train final model on all data
print("\nTraining final model on all data...")
model.fit(X, y)

# Make predictions
train_predictions = model.predict(X_train)
test_predictions = model.predict(X_test)

# Calculate metrics
train_rmse = np.sqrt(mean_squared_error(y_train, train_predictions))
test_rmse = np.sqrt(mean_squared_error(y_test, test_predictions))
train_r2 = r2_score(y_train, train_predictions)
test_r2 = r2_score(y_test, test_predictions)

print("\nFinal Model Performance:")
print(f"Training RMSE: {train_rmse:.4f}")
print(f"Testing RMSE: {test_rmse:.4f}")
print(f"Training R²: {train_r2:.4f}")
print(f"Testing R²: {test_r2:.4f}")

# Feature importance
importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
})
importance = importance.sort_values('importance', ascending=False)

print("\nFeature Importance:")
print(importance)

# Save predictions and actual values
results_df = pd.DataFrame({
    'date': featured_df.index[-len(test_predictions):],
    'actual': y_test,
    'predicted': test_predictions
})

output_path = os.path.join(output_dir, "daily_return_predictions.csv")
results_df.to_csv(output_path, index=False)
print(f"\nPredictions saved to: {output_path}")

# Save model
model_path = os.path.join(output_dir, "daily_return_model.json")
model.save_model(model_path)
print(f"Model saved to: {model_path}")