# This script is used to test the database queries


import asyncio
import gel

# async def main():
#     client = gel.create_async_client()
#     results = await client.query('SELECT Company { name, stock_ticker };')
#     for row in results:
#         print(f"{row.name} ({row.stock_ticker})")
#     await client.aclose()

# asyncio.run(main())

async def main():
    client = gel.create_async_client()
    res = await client.query('''
        SELECT Company FILTER .stock_ticker = <str>$ticker
    ''', ticker='LLY')
    print(res)
    await client.aclose()

asyncio.run(main())


