# Reads the output of map_to_gel.py
#  Connects to Gel async
# Inserts entities & relations into the Gel database
# Run this script in /gelDB directory using command: python ../PyScripts/ingest_gel.py

import json
import datetime
import asyncio
import gel
import os
import sys

# This is needed for asyncio bug in Python 3.10 on Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def insert_entities(client, entity_file):
    with open(entity_file, 'r', encoding='utf-8') as ef:
        for line in ef:
            obj = json.loads(line)
            await client.query('''
                INSERT Entity {
                    name := <str>$name,
                    label := <str>$label
                }
            ''', name=obj['name'], label=obj['label'])

async def insert_relations(client, relation_file):
    with open(relation_file, 'r', encoding='utf-8') as rf:
        for line in rf:
            rel = json.loads(line)
            if not rel.get('company'):
                continue

            date_str = rel.get('date')
            date_obj = None
            if date_str:
                try:
                    date_obj = datetime.date.fromisoformat(date_str.split('T')[0])
                except ValueError:
                    pass

            ticker = rel.get("company", "").strip().upper()
            print(f"Inserting relation for ticker: '{ticker}'")

            # Debug lookup
            res = await client.query('''
                SELECT Company FILTER .stock_ticker = <str>$ticker
            ''', ticker=ticker)

            await client.query('''
                INSERT Relation {
                    subject := <str>$subject,
                    relation := <str>$relation,
                    object := <str>$object,
                    sentence := <str>$sentence,
                    url := <str>$url,
                    date := <optional cal::local_date>$date,
                    company := (
                        SELECT Company
                        FILTER .stock_ticker = <str>$ticker
                        LIMIT 1
                    )
                }
            ''',
            subject=rel['subject'],
            relation=rel['relation'],
            object=rel['object'],
            sentence=rel['sentence'],
            url=rel['url'],
            date=date_obj,
            ticker=ticker)

async def insert_news_articles(client, article_file):
    with open(article_file, 'r', encoding='utf-8') as af:
        for line in af:
            item = json.loads(line)

            title = item.get("title") or "Untitled"
            url = item.get("url")
            pub_date_str = item.get("publishedAt")
            content = item.get("content", "")
            sentiment = float(item.get("sentiment", 0.0))

            pub_date = None
            if pub_date_str:
                try:
                    pub_date = datetime.datetime.fromisoformat(pub_date_str).replace(tzinfo=None)
                except ValueError:
                    pass

            tickers = [c["ticker"] for c in item.get("companies", [])]
            
            exists = await client.query('''
                select exists (
                    select NewsArticle filter .url = <str>$url
                )
            ''', url=url)
            if exists[0]:
                print(f" Skipping duplicate: {url}")
                continue

            await client.query('''
                insert NewsArticle {
                    title := <str>$title,
                    url := <str>$url,
                    publication_date := <optional datetime>$pub_date,
                    sentiment_score := <float32>$sentiment,
                    content := <str>$content,
                    mentions_companies := distinct (
                        for t in array_unpack(<array<str>>$tickers)
                        union (
                            select Company filter .stock_ticker = t
                        )
                    )
                }
            ''', title=title, url=url, pub_date=pub_date, sentiment=sentiment, content=content, tickers=tickers)


async def main():
    os.environ["GEL_PROJECT_PATH"] = os.path.abspath(os.path.dirname(__file__) + '/../gelDB')
    client = gel.create_async_client()
    await insert_entities(client, '../data/processed/gel_entities.jsonl')
    await insert_relations(client, '../data/processed/gel_relations.jsonl')
    await insert_news_articles(client, '../data/processed/entities_extracted.jsonl')

    await client.aclose()

if __name__ == '__main__':
    asyncio.run(main())

