# Use NewsAPI to get top healthcare headlines
# Saves output to a JSON file for later scraping

# Requirements:
# pip install newsapi-python requests python-dateutil

from newsapi import NewsApiClient
import json
from datetime import datetime, timedelta
import os

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

# NewsAPI configuration
API_KEY = "1a7e8b8708b94a628df79af9ef87a2c9"  
COMPANIES = [
    "Eli Lilly", "UnitedHealth", "Johnson & Johnson", "AbbVie", "Abbott Laboratories",
    "Merck", "Intuitive Surgical", "Thermo Fisher Scientific", "Amgen", "Boston Scientific"
]
TICKERS = ["LLY", "UNH", "JNJ", "ABBV", "ABT", "MRK", "ISRG", "TMO", "AMGN", "BSX"]
KEYWORDS = ["healthcare", "pharma", "biotech"]
QUERY = "healthcare OR pharma OR biotech OR medical OR drug OR medicine"
#DOMAINS = "finance.yahoo.com,reuters.com"

# Calculate date range (last 29 days to avoid API cutoff)
end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=API_KEY)

# Fetch news articles
articles = newsapi.get_everything(
    q=QUERY,
    from_param=start_date,
    to=end_date,
    language="en",
    sort_by="relevancy",
    page_size=100
)

print(articles)

results = []
urls = []
for article in articles.get('articles', []):
    # Add company/ticker tags based on content
    tags = [ticker for ticker, company in zip(TICKERS, COMPANIES)
            if company in article.get("title", "") or company in article.get("content", "") or
            ticker in article.get("title", "") or ticker in article.get("content", "")]
    tags.append("healthcare")
    article['tags'] = tags
    results.append(article)
    if article.get('url'):
        urls.append(article['url'])

# Write results to a new JL file with timestamp in the name
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
api_jl_path = f'output/api_{timestamp}.jl'
with open(api_jl_path, 'w', encoding='utf-8') as f:
    for article in results:
        f.write(json.dumps(article, ensure_ascii=False) + '\n')

# Append each article as a JSON line to items.jl
with open('output/items.jl', 'a', encoding='utf-8') as f:
    for article in results:
        f.write(json.dumps(article, ensure_ascii=False) + '\n')

# Write URLs to a new JL file (one JSON string per line)
with open('output/newsapi_healthcare_urls.jl', 'w', encoding='utf-8') as f:
    for url in urls:
        f.write(json.dumps(url) + '\n')

print(f"Saved {len(results)} articles to {api_jl_path} and appended to output/items.jl")
print(f"Saved {len(urls)} URLs to output/newsapi_healthcare_urls.jl")

custom_settings = {
    'FEED_FORMAT': 'jsonlines',
    'FEED_URI': '../output/items.jl',  # Save to WebFocusedCrawlWork/output/
    'FEED_EXPORT_ENCODING': 'utf-8',
    'MAX_DAYS_OLD': 10
}