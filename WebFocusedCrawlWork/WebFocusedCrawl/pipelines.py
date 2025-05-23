# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from WebFocusedCrawl.items import WebfocusedcrawlItem  # item class 
from string import whitespace
import json
import os
from datetime import datetime

class WebfocusedcrawlPipeline(object):
    def process_item(self, item, spider):
        item['text'] = [line for line in item['text'] if line not in whitespace]
        item['text'] = ''.join(item['text'])
        return item

class JsonLinesPipeline:
    def __init__(self):
        # Create output directory if it doesn't exist
        self.output_dir = 'output'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Create a timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.filename = os.path.join(self.output_dir, f'articles_{timestamp}.jl')
        
    def open_spider(self, spider):
        self.file = open(self.filename, 'w', encoding='utf-8')
        
    def close_spider(self, spider):
        self.file.close()
        
    def process_item(self, item, spider):
        # Convert item to dict and write as JSON line
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line)
        return item
