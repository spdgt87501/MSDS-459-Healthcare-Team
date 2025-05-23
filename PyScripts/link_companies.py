# This script links the companies to the GEL database

import json
import asyncio
import gel

# === Known companies ===
TOP_COMPANIES = [
    {"name": "Eli Lilly", "ticker": "LLY"},
    {"name": "United Health", "ticker": "UNH"},
    {"name": "Johnson & Johnson", "ticker": "JNJ"},
    {"name": "Abbvie", "ticker": "ABBV"},
    {"name": "Abbott Labs", "ticker": "ABT"},
    {"name": "Merck & Co", "ticker": "MRK"},
    {"name": "Intuitive Surgical", "ticker": "ISRG"},
    {"name": "Thermo Fisher Sci", "ticker": "TMO"},
    {"name": "Amgen", "ticker": "AMGN"},
    {"name": "Boston Scientific", "ticker": "BSX"},
]

async def insert_companies(client):
    for company in TOP_COMPANIES:
        await client.query('''
            INSERT Company {
                name := <str>$name,
                stock_ticker := <str>$ticker
            }
            UNLESS CONFLICT ON .stock_ticker
        ''', name=company["name"], ticker=company["ticker"])

async def main():
    client = gel.create_async_client()
    await insert_companies(client)
    await client.aclose()

if __name__ == '__main__':
    asyncio.run(main())

