# This file was run on WSL2 - Ubuntu 22.04 LTS using a 4060Ti GPU

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import os

# Get the script's directory and output path
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load the data
print("Loading data...")
weekly_avg = pd.read_csv("healthcare_sector_returns.csv")
print(f"Loaded {len(weekly_avg)} weeks of data")

# Drop initial NaN from return calculation
weekly_avg_clean = weekly_avg.dropna().reset_index(drop=True)
print(f"After cleaning: {len(weekly_avg_clean)} weeks of data")

# Normalize return values
scaler = MinMaxScaler(feature_range=(0, 1))
returns_scaled = scaler.fit_transform(weekly_avg_clean[["hc_sector_return"]])

# Prepare LSTM sequences
def create_sequences(data, lookback=4):
    X, y = [], []
    for i in range(len(data) - lookback):
        X.append(data[i:i + lookback])
        y.append(data[i + lookback])
    return np.array(X), np.array(y)

lookback = 4  # using 4 weeks to predict the next
X, y = create_sequences(returns_scaled, lookback=lookback)
print(f"Created {len(X)} sequences for training")

# Train/test split (80/20)
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]
print(f"Training set size: {len(X_train)}, Test set size: {len(X_test)}")

# Define LSTM model
print("\nBuilding LSTM model...")
model = Sequential()
model.add(LSTM(32, input_shape=(lookback, 1)))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mean_squared_error'])

# Train model
print("Training model")
history = model.fit(X_train, y_train, epochs=50, batch_size=4, verbose=1)

# Save the model
model_path = os.path.join(output_dir, "lstm_model.h5")
model.save(model_path)
print(f"\n✅ Model saved to: {model_path}")

# Save the scaler parameters
scaler_path = os.path.join(output_dir, "scaler_params.npy")
np.save(scaler_path, {
    'scale_': scaler.scale_,
    'min_': scaler.min_,
    'data_min_': scaler.data_min_,
    'data_max_': scaler.data_max_,
    'data_range_': scaler.data_range_,
    'n_samples_seen_': scaler.n_samples_seen_
})
print(f"✅ Scaler parameters saved to: {scaler_path}")

# Predict on test set
print("\nMaking predictions")
y_pred = model.predict(X_test)

# Inverse scale the predictions
y_pred_inv = scaler.inverse_transform(y_pred)
y_test_inv = scaler.inverse_transform(y_test)

# Combine predictions for display
results = pd.DataFrame({
    "week": weekly_avg_clean["week"].iloc[-len(y_test):].reset_index(drop=True),
    "actual_return": y_test_inv.flatten(),
    "predicted_return": y_pred_inv.flatten()
})

# Display results
print("\nPrediction Results:")
print(results.head())
print("\nResults Summary:")
print(results.describe())

# Save results
results_path = os.path.join(output_dir, "lstm_predictions.csv")
results.to_csv(results_path, index=False)
print(f"\nResults saved to: {results_path}")