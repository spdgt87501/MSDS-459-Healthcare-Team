# Merge LSTM predictions with sentiment data
# This script merges the LSTM predictions with the sentiment data on the 'week' column
# The 'week' column is the date of the week for the prediction and sentiment data
# The script calculates a correlation matrix to analyze the relationships between actual returns, LSTM-predicted returns, sentiment ratios, and article counts

import pandas as pd
import numpy as np
import os

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory (two levels up from script)
project_root = os.path.dirname(os.path.dirname(script_dir))
# Get the output directory
output_dir = os.path.join(script_dir, "output")

# Load both CSVs
print("Loading data files")
preds = pd.read_csv(os.path.join(project_root, "lstm_predictions.csv"), parse_dates=["week"])
sentiment = pd.read_csv(os.path.join(project_root, "weekly_market_sentiment_with_returns.csv"), parse_dates=["week"])

print(f"\nLoaded {len(preds)} LSTM predictions and {len(sentiment)} sentiment records")

# Merge on 'week'
merged = pd.merge(preds, sentiment, on="week", how="inner")
print(f"\nAfter merging: {len(merged)} records")

# Preview
print("\nPreview of merged data:")
print(merged.head())

# Check correlation matrix
print("\nCalculating correlation matrix.")
correlation_matrix = merged[[
    "actual_return", 
    "predicted_return", 
    "sentiment_ratio", 
    "article_count"
]].corr()

# Format correlation matrix for better readability
correlation_matrix = correlation_matrix.round(3)

print("\nCorrelation Matrix:")
print(correlation_matrix)

# Save merged file
print("\nSaving merged data.")
merged.to_csv(os.path.join(output_dir, "merged_lstm_sentiment.csv"), index=False)

# Save correlation matrix
print("Saving correlation matrix.")
correlation_matrix.to_csv(os.path.join(output_dir, "correlation_matrix.csv"))

print("\nAnalysis complete! Files saved in PyScripts/analysis/output/:")
print("- merged_lstm_sentiment.csv: Contains the merged data")
print("- correlation_matrix.csv: Contains the correlation analysis")