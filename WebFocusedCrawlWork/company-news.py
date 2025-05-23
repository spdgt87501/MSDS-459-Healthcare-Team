import finnhub
import json

# Your Finnhub API key
finnhub_client = finnhub.Client(api_key="d0em6bhr01qkbclc7uqgd0em6bhr01qkbclc7ur0")

# Top 10 healthcare company tickers
top10_healthcare_tickers = [
    'UNH',  # UnitedHealth Group
    'LLY',  # Eli Lilly
    'JNJ',  # Johnson & Johnson
    'MRK',  # Merck & Co.
    'ABBV', # AbbVie
    'NVO',  # Novo Nordisk (ADR)
    'PFE',  # Pfizer
    'ABT',  # Abbott Laboratories
    'TMO',  # Thermo Fisher Scientific
    'AMGN'  # Amgen
]

# Set your date range
_from = "2024-05-01"
to = "2024-05-08"

with open("items.jl", "a", encoding="utf-8") as f:  # 'a' for append mode
    for ticker in top10_healthcare_tickers:
        try:
            news_list = finnhub_client.company_news(ticker, _from=_from, to=to)
            for news in news_list:
                # Add ticker and source info for consistency
                news['ticker'] = ticker
                news['source'] = 'finnhub'
                f.write(json.dumps(news, ensure_ascii=False) + "\n")
            print(f"Appended {len(news_list)} news items for {ticker}")
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")

print("Done! Finnhub healthcare news appended to items.jl")
