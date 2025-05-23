# This script is used to process the stock prices and insert them into the database
# Run this script in /gelDB directory using command: python ../PyScripts/process_stocks.py

import os
import json
import datetime
import asyncio
import gel

STOCK_DIR = '../stock_prices/stocks/output'

async def insert_stock_prices(client):
    total_inserted = 0
    for filename in os.listdir(STOCK_DIR):
        if not filename.endswith('_stock_data.jsonl'):
            continue

        ticker = filename.split('_')[0].upper()
        
        filepath = os.path.join(STOCK_DIR, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)

                if 'Date' not in record or 'Close' not in record:
                    continue  # Skip invalid or incomplete rows

                try:
                    date = datetime.date.fromisoformat(record['Date'])
                    close = float(record['Close'])
                    open_ = float(record.get('Open', 0.0))
                    high = float(record.get('High', 0.0))
                    low = float(record.get('Low', 0.0))
                    volume = int(record.get('Volume', 0))

                    # Check if company exists
                    res = await client.query('''
                        SELECT Company { id } FILTER .stock_ticker = <str>$ticker
                    ''', ticker=ticker)

                    print(f"🔍 Company lookup result for {ticker}: {res}")

                    if not res:
                        print(f" No Company found for ticker: {ticker}")
                        continue
                    else:
                        print(f" Found Company for: {ticker}")

                    company_id = res[0].id

                    await client.query('''
                        INSERT StockPrice {
                            date := <cal::local_date>$date,
                            close := <float64>$close,
                            open := <float64>$open,
                            high := <float64>$high,
                            low := <float64>$low,
                            volume := <int64>$volume,
                            company := (SELECT Company FILTER .id = <uuid>$company_id)
                        }
                    ''',
                    date=date,
                    close=close,
                    open=open_,
                    high=high,
                    low=low,
                    volume=volume,
                    company_id=company_id)

                    total_inserted += 1
                except Exception as e:
                    print(f"Skipping bad record in {filename}: {e}")

    print(f"\n Total inserted: {total_inserted}")

async def main():
    client = gel.create_async_client()
    await insert_stock_prices(client)
    await client.aclose()

if __name__ == '__main__':
    asyncio.run(main())

