import yfinance as yf

def fetch_stock_price(symbol):
    """Fetch the current stock price for the given symbol using Yahoo Finance."""
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    if data.empty:
        print(f"No data found for symbol: {symbol}")
        return
    price = data['Close'][0]
    print(f"Current price of {symbol}: ${price:.2f}")

if __name__ == "__main__":
    symbol = input("Enter stock symbol (e.g., AAPL): ").strip().upper()
    fetch_stock_price(symbol)
