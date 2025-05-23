# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class WebfocusedcrawlItem(scrapy.Item):
    # Common fields for all sources
    url = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    tags = scrapy.Field()
    source = scrapy.Field()
    
    # News article specific fields
    articles = scrapy.Field()  # List of article data dictionaries
    author = scrapy.Field()    # Article author
    timestamp = scrapy.Field() # Article timestamp
    summary = scrapy.Field()   # Article summary
    content = scrapy.Field()   # Full article content
    metadata = scrapy.Field()  # Article metadata
    
    # Company specific fields
    company = scrapy.Field()   # Company information (name, ticker)
    
    # CNBC specific fields
    trending = scrapy.Field()  # Trending articles
    categories = scrapy.Field() # Available categories
    related_articles = scrapy.Field() # Related articles
    
    # Yahoo Finance specific fields
    stocks = scrapy.Field()    # Yahoo Finance stocks data
    
    # Additional fields
    category = scrapy.Field()  # Article category

