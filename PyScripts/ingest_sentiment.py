import json
import asyncio
import gel

INPUT_FILES = [
    "../CNBC_items_with_predictions.jl",
    "../Investopedia_articles_with_predictions.jl",
    "../NewsAPI_Items_with_predictions.jl"
]

async def backfill_sentiment(client):
    updated = 0
    skipped = 0

    for file in INPUT_FILES:
        print(f"\n📁 Processing file: {file}")
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                url = item.get("url")
                raw = item.get("predicted_label")

                if not url or raw is None:
                    print(f"⚠️ Skipping article - missing URL or predicted_label")
                    skipped += 1
                    continue

                try:
                    score = float(str(raw).strip())
                    if score not in [0.0, 1.0]:
                        print(f"⚠️ Skipping article - sentiment score {score} is not 0 or 1")
                        skipped += 1
                        continue
                except (TypeError, ValueError) as e:
                    print(f"❌ Error converting sentiment for URL: {url}")
                    print(f"   Error: {str(e)}")
                    skipped += 1
                    continue

                # Try exact match on full URL
                result = await client.query('''
                    SELECT NewsArticle {
                        url,
                        sentiment_score
                    }
                    FILTER .url = <str>$url
                ''', url=url)

                if not result:
                    print(f"🔍 No exact match found in DB for URL: {url}")
                    skipped += 1
                    continue

                current_score = result[0].sentiment_score
                print(f"✅ Match: {url}")
                print(f"   Current score: {current_score}, New: {score}")

                if current_score == score:
                    print(f"   ↪ No update needed")
                    skipped += 1
                    continue

                await client.query('''
                    UPDATE NewsArticle
                    FILTER .url = <str>$url
                    SET {
                        sentiment_score := <float32>$score
                    }
                ''', url=url, score=score)

                print(f"   ✅ Updated")
                updated += 1

    print(f"\nSummary:")
    print(f"✅ Successfully updated: {updated} articles")
    print(f"⚠️ Skipped: {skipped} articles")

async def main():
    client = gel.create_async_client()
    await backfill_sentiment(client)
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())

