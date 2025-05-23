# articles-spider.py
"""
Scrapes Wikipedia company pages and CNBC Health & Science news articles.
Saves Wikipedia HTML to wikipages/ and outputs structured data to output/articles_*.jl.
Toggle Wikipedia scraping with the 'scrape_wikipedia' spider argument.
"""
import scrapy
import os
from WebFocusedCrawl.items import WebfocusedcrawlItem
import nltk
import re
from datetime import datetime
import dateparser

def remove_stopwords(tokens):
    stopword_list = nltk.corpus.stopwords.words('english')
    return [token for token in tokens if token not in stopword_list]

class ArticlesSpider(scrapy.Spider):
    name = "articles-spider"
    allowed_domains = ['cnbc.com', 'wikipedia.org']
    custom_settings = {
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'items.jl',  # Save to project dir
        'FEED_EXPORT_ENCODING': 'utf-8',
        'MAX_DAYS_OLD': 10
    }

    def start_requests(self):
        # Define common browser headers
        cnbc_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.cnbc.com/'
        }
        # CNBC Health and Science News
        cnbc_urls = [
            "https://www.cnbc.com/health-and-science/"
        ]
        for url in cnbc_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_cnbc,
                meta={
                    'source': 'cnbc',
                    'max_days_old': self.custom_settings['MAX_DAYS_OLD']
                },
                headers=cnbc_headers
            )
        # Wikipedia company pages (optional)
        if getattr(self, 'scrape_wikipedia', False):
            wikipedia_urls = [
                "https://en.wikipedia.org/wiki/Eli_Lilly_and_Company",
                "https://en.wikipedia.org/wiki/UnitedHealth_Group",
                "https://en.wikipedia.org/wiki/Johnson_%26_Johnson",
                "https://en.wikipedia.org/wiki/AbbVie",
                "https://en.wikipedia.org/wiki/Abbott_Laboratories",
                "https://en.wikipedia.org/wiki/Merck_%26_Co.",
                "https://en.wikipedia.org/wiki/Intuitive_Surgical",
                "https://en.wikipedia.org/wiki/Thermo_Fisher_Scientific",
                "https://en.wikipedia.org/wiki/Amgen",
                "https://en.wikipedia.org/wiki/Boston_Scientific"
            ]
            for url in wikipedia_urls:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_wikipedia,
                    meta={'source': 'wikipedia'}
                )

    def parse_cnbc(self, response):
        """Parse CNBC health and science news landing page."""
        item = WebfocusedcrawlItem()
        item['url'] = response.url
        item['source'] = 'cnbc'
        item['title'] = 'CNBC Health and Science News'
        articles = []
        for article in response.css('div.Card-titleContainer'):
            article_data = {
                'headline': article.css('a::text').get(),
                'url': response.urljoin(article.css('a::attr(href)').get()),
                'timestamp': article.css('span::text').get(),
                'category': 'Health and Science',
                'author': article.css('div.Card-author::text').get(),
                'summary': article.css('div.Card-description::text').get()
            }
            if article_data['timestamp']:
                article_data['timestamp'] = dateparser.parse(article_data['timestamp']).isoformat() if article_data['timestamp'] else datetime.now().isoformat()
            if article_data['author']:
                article_data['author'] = article_data['author'].strip()
            if article_data['summary']:
                article_data['summary'] = article_data['summary'].strip()
            articles.append(article_data)
            if article_data['url']:
                yield scrapy.Request(
                    url=article_data['url'],
                    callback=self.parse_cnbc_article,
                    meta={'article_data': article_data},
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Referer': response.url
                    }
                )
        item['articles'] = articles
        item['text'] = [article['headline'] for article in articles]
        item['tags'] = ['health', 'science', 'news', 'cnbc']
        item['timestamp'] = datetime.now().isoformat()
        return item

    def parse_cnbc_article(self, response):
        article_data = response.meta['article_data']
        item = WebfocusedcrawlItem()
        content = response.css('div.ArticleBody-articleBody p::text').getall()
        author = response.css('div.Author-authorName::text').get()
        related_articles = []
        for related in response.css('div.RelatedContent-item'):
            related_data = {
                'headline': related.css('a::text').get(),
                'url': response.urljoin(related.css('a::attr(href)').get())
            }
            related_articles.append(related_data)
        metadata = {
            'author': author,
            'publish_date': response.css('time::attr(datetime)').get(),
            'read_time': response.css('div.ArticleHeader-readTime::text').get(),
            'keywords': response.css('meta[name="keywords"]::attr(content)').get()
        }
        article_data.update({
            'content': ' '.join(content),
            'full_text': response.css('div.ArticleBody-articleBody::text').getall(),
            'related_articles': related_articles,
            'metadata': metadata
        })
        item['url'] = article_data['url']
        item['source'] = 'cnbc'
        item['title'] = article_data['headline']
        item['text'] = article_data['full_text']
        item['author'] = article_data['author']
        item['timestamp'] = article_data['timestamp']
        item['tags'] = ['health', 'science', 'news', 'cnbc']
        item['content'] = article_data['content']
        item['summary'] = article_data['summary']
        item['related_articles'] = article_data['related_articles']
        item['metadata'] = article_data['metadata']
        item['category'] = 'Health and Science'
        return item

    def parse_wikipedia(self, response):
        """Parse Wikipedia company pages and save HTML."""
        page = response.url.split("/")[4]
        page_dirname = 'wikipages'
        if not os.path.exists(page_dirname):
            os.makedirs(page_dirname)
        filename = f'{page}.html'
        filepath = os.path.join(page_dirname, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                f.write(response.body)
            self.log(f'Saved file {filename}')
        item = WebfocusedcrawlItem()
        item['url'] = response.url
        item['title'] = response.css('h1::text').get()
        item['text'] = response.xpath('//div[@id="mw-content-text"]//text()').getall()
        tags_list = [response.url.split("/")[2], response.url.split("/")[3]]
        more_tags = [re.sub('[^a-zA-Z]', '', x.lower()) for x in remove_stopwords(response.url.split("/")[4].split("_"))]
        tags_list.extend(more_tags)
        item['tags'] = tags_list
        item['source'] = 'wikipedia'
        item['timestamp'] = datetime.now().isoformat()
        return item