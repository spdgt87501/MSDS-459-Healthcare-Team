import yfinance as yf
import json
import os

tickers = [
    "JNJ", #Johnson & Johnson
    "UNH", #UnitedHealth Group
    "LLY", #Eli Lilly and Company
    "ABBV", #AbbVie Inc.
    "ABT", #Abbott Laboratories
    "ISRG", #Intuitive Surgical Inc.
    "MRK", #Merck & Co., Inc.
    "TMO", #Thermo Fisher Scientific Inc.
    "AMGN", #Amgen Inc.
    "BSX", #Boston Scientific Corporation
]

# Download historical data for the last 2 years
data = yf.download(tickers, period="2y", group_by='ticker')

output_dir = os.path.join("stocks", "output")
os.makedirs(output_dir, exist_ok=True)

for ticker in tickers:
    df = data[ticker].reset_index()
    output_path = os.path.join(output_dir, f"{ticker}_stock_data.jsonl")
    with open(output_path, "w") as f:
        for _, row in df.iterrows():
            # Convert timestamp to sting for json serialization
            row_dict = row.to_dict()
            if not isinstance(row_dict['Date'], str):
                row_dict['Date'] = row_dict['Date'].strftime('%Y-%m-%d')
            f.write(json.dumps(row_dict) + "\n")

print("Stock data saved to JSON files.")







