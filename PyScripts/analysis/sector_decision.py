# This script loads the latest sentiment data and the stock data
# It then makes a prediction using the LSTM model on the last 4 weeks of data
# It then makes a decision based on the predicted return and the sentiment ratio
# This file was run on WSL2 - Ubuntu 22.04 LTS using a 4060Ti GPU

import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import json
import os
import datetime

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory (two levels up from script)
project_root = os.path.dirname(os.path.dirname(script_dir))

# Define paths relative to project structure
MODEL_PATH = os.path.join(script_dir, "output", "lstm_model.h5")
SCALER_PATH = os.path.join(script_dir, "output", "scaler_params.npy")
STOCK_DIR = os.path.join(project_root, "stock_prices", "stocks", "output")
SENTIMENT_FILE = os.path.join(script_dir, "output", "weekly_market_sentiment_with_returns.csv")

# Verify paths exist
print("Verifying paths...")
if not os.path.exists(MODEL_PATH):
    print(f" Warning: Model file not found at {MODEL_PATH}")
if not os.path.exists(SCALER_PATH):
    print(f" Warning: Scaler parameters not found at {SCALER_PATH}")
if not os.path.exists(STOCK_DIR):
    print(f" Warning: Stock directory not found at {STOCK_DIR}")
if not os.path.exists(SENTIMENT_FILE):
    print(f" Warning: Sentiment file not found at {SENTIMENT_FILE}")

print("\nUsing the following paths:")
print(f"Model path: {MODEL_PATH}")
print(f"Scaler path: {SCALER_PATH}")
print(f"Stock data directory: {STOCK_DIR}")
print(f"Sentiment file: {SENTIMENT_FILE}")

# === CONFIG ===
LOOKBACK = 4  # Match the lookback period used in training

# === LOAD MODEL AND SCALER ===
try:
    model = load_model(MODEL_PATH)
    print("\n Model loaded successfully")
    
    # Load scaler parameters
    scaler_params = np.load(SCALER_PATH, allow_pickle=True).item()
    scaler = MinMaxScaler()
    scaler.scale_ = scaler_params['scale_']
    scaler.min_ = scaler_params['min_']
    scaler.data_min_ = scaler_params['data_min_']
    scaler.data_max_ = scaler_params['data_max_']
    scaler.data_range_ = scaler_params['data_range_']
    scaler.n_samples_seen_ = scaler_params['n_samples_seen_']
    print(" Scaler parameters loaded successfully")
except Exception as e:
    print(f"\n Error loading model or scaler: {str(e)}")
    exit(1)

# === LOAD AND PREPARE STOCK DATA ===
def load_all_stock_data():
    all_stocks = []
    for file in os.listdir(STOCK_DIR):
        if file.endswith("_stock_data.jsonl"):
            ticker = file.split("_")[0].upper()
            with open(os.path.join(STOCK_DIR, file), 'r') as f:
                for line in f:
                    row = json.loads(line)
                    row["ticker"] = ticker
                    all_stocks.append(row)
    return pd.DataFrame(all_stocks)

try:
    stock_df = load_all_stock_data()
    print(f" Loaded stock data for {len(stock_df['ticker'].unique())} tickers")
except Exception as e:
    print(f" Error loading stock data: {str(e)}")
    exit(1)

stock_df["date"] = pd.to_datetime(stock_df["Date"])
stock_df["close"] = stock_df["Close"]
stock_df = stock_df[["ticker", "date", "close"]]

# Weekly sector average return
stock_df["week"] = stock_df["date"].dt.to_period("W").apply(lambda r: r.start_time)
weekly_close = stock_df.groupby(["ticker", "week"])["close"].last().reset_index()
weekly_close["return"] = weekly_close.groupby("ticker")["close"].pct_change()
weekly_avg = weekly_close.groupby("week")["return"].mean().reset_index()
weekly_avg.rename(columns={"return": "hc_sector_return"}, inplace=True)

# Drop NaN and scale
returns = weekly_avg["hc_sector_return"].dropna().values.reshape(-1, 1)
X_input = scaler.transform(returns[-LOOKBACK:]).reshape(1, LOOKBACK, 1)

# === MAKE PREDICTION ===
pred_scaled = model.predict(X_input)
predicted_return = scaler.inverse_transform(pred_scaled)[0][0]

# === LOAD LATEST SENTIMENT ===
try:
    sentiment_df = pd.read_csv(SENTIMENT_FILE)
    latest_sentiment = sentiment_df.iloc[-1]
    sentiment_ratio = latest_sentiment.get("sentiment_ratio", None)
    print(f" Loaded sentiment data from {SENTIMENT_FILE}")
except Exception as e:
    print(f" Error loading sentiment data: {str(e)}")
    sentiment_ratio = None

# === DECISION LOGIC ===
print("\nAnalysis Results:")
print(f"Predicted Return: {predicted_return:.4f}")
print(f"Sentiment Ratio: {sentiment_ratio if sentiment_ratio is not None else 'N/A'}")

if sentiment_ratio is not None:
    if predicted_return > 0 and sentiment_ratio > 0.7:
        print("\n Action: Recommend BUY (model and sentiment agree)")
    elif predicted_return > 0:
        print("\n Action: Model is positive, but sentiment is weak")
    else:
        print("\n Action: Do NOT buy (model negative)")
else:
    print("\n Sentiment data missing — cannot complete decision.")

# === LOG RESULTS TO CSV ===

# Create output directory if it doesn't exist
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)

# Create log entry
log_entry = {
    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "predicted_return": predicted_return,
    "sentiment_ratio": sentiment_ratio,
    "decision": "BUY" if predicted_return > 0 and sentiment_ratio and sentiment_ratio > 0.7 else "NO_BUY",
    "model_positive": predicted_return > 0,
    "sentiment_strong": sentiment_ratio > 0.7 if sentiment_ratio is not None else None
}

# Define log file path
log_file = os.path.join(output_dir, "prediction_logs.csv")

# Write to CSV
log_df = pd.DataFrame([log_entry])
if os.path.exists(log_file):
    log_df.to_csv(log_file, mode='a', header=False, index=False)
else:
    log_df.to_csv(log_file, index=False)

print(f"\n✅ Results logged to {log_file}")
