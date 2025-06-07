import pandas as pd
import numpy as np
import os

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")

# Load XGBoost predictions
print("Loading XGBoost predictions")
preds = pd.read_csv(os.path.join(output_dir, "daily_return_predictions.csv"), parse_dates=["date"])

# Load sentiment + return features from the same predictions file
print("Loading sentiment and return data")
merged = pd.read_csv(os.path.join(output_dir, "daily_return_predictions.csv"), parse_dates=["date"])

# Compute correlation
correlation_data = merged[[
    "actual",
    "predicted"
]].rename(columns={
    "actual": "actual_return",
    "predicted": "xgb_predicted_return"
})

# Compute correlation
correlation_matrix = correlation_data.corr().round(3)

# Show matrix
print("\nCorrelation Matrix:")
print(correlation_matrix)

# Save outputs
correlation_data.to_csv(os.path.join(output_dir, "xgb_correlation_data.csv"), index=False)
correlation_matrix.to_csv(os.path.join(output_dir, "xgb_correlation_matrix.csv"))

print("\nAnalysis complete!")
print("- xgb_correlation_data.csv: correlation data")
print("- xgb_correlation_matrix.csv: correlation matrix")

# Additional analysis
print("\nPrediction Statistics:")
print(f"Mean Absolute Error: {np.mean(np.abs(correlation_data['actual_return'] - correlation_data['xgb_predicted_return'])):.4f}")
print(f"Root Mean Square Error: {np.sqrt(np.mean((correlation_data['actual_return'] - correlation_data['xgb_predicted_return'])**2)):.4f}")
print(f"R-squared: {correlation_matrix.iloc[0,1]**2:.4f}")
