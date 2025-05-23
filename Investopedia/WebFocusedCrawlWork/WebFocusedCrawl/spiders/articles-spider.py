# Scrape Wikipedia, saving page html code to wikipages directory 
# Most Wikipedia pages have lots of text 
# We scrape the text data creating a JSON lines file items.jl
# with each line of JSON representing a Wikipedia page/document
# Subsequent text parsing of these JSON data will be needed
# This example is for a list of companies in the Materials sector
# Replace the urls list with appropriate Wikipedia URLs
# for your team's industry sector of interest

# ensure that NLTK has been installed along with the stopwords corpora
# pip install nltk
# python -m nltk.downloader stopwords

import scrapy
import os.path
from WebFocusedCrawl.items import WebfocusedcrawlItem  # item class 
import nltk  # used to remove stopwords from tags
import re  # regular expressions used to parse tags
import time

def remove_stopwords(tokens):
    stopword_list = nltk.corpus.stopwords.words('english')
    good_tokens = [token for token in tokens if token not in stopword_list]
    return good_tokens     

class ArticlesSpider(scrapy.Spider):
    name = "articles-spider"

    def start_requests(self):
        allowed_domains = ['investopedia.com'] 
        # list of Wikipedia URLs for topic of interest
        # top ten companies in the industry sector (Materials)

        import requests
        from bs4 import BeautifulSoup

        def get_links_by_class(url, target_class):
            #all_links = {}
            try:
                headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
                    }
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                soup = BeautifulSoup(response.content, 'html.parser', multi_valued_attributes=None)
                
                links = [a['href'] for a in soup.find_all('a', class_=target_class) if 'href' in a.attrs]
                #all_links[url] = links
                time.sleep(3)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {url}: {e}")
            except Exception as e:
                print(f"Error parsing {url}: {e}")
                    
            print(links)
            return links

        
        website_list = [
            "https://www.investopedia.com/search?q=lly"
            ,"https://www.investopedia.com/search?q=jnj"
            ,"https://www.investopedia.com/search?q=abbv"
            ,"https://www.investopedia.com/search?q=abt"
            ,"https://www.investopedia.com/search?q=mrk"
            ,"https://www.investopedia.com/search?q=isrg"
            ,"https://www.investopedia.com/search?q=tmo"
            ,"https://www.investopedia.com/search?q=amgn"
            ,"https://www.investopedia.com/search?q=bsx"
        ]
        target_class = "comp mntl-card-list-card--extendable mntl-universal-card mntl-document-card mntl-card card card--no-image"

        for url in website_list:
            print('---URL-FROM-WEBSITE_LIST---')
            print(url)
            extracted_links = get_links_by_class(url, target_class)

            for url in extracted_links:
                print(f"Links from {url}:")
                if extracted_links:
                    for link in extracted_links:
                        print(f"- {link}")
                else:
                    print("No links found for this class.")

            urls = extracted_links

            print('------URLS------')
            print(urls)
                
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)
                time.sleep(1)

    # scraping and parsing commands are designed for Wikipedia
    # revisions will likely be needed for other websites
    def parse(self, response):
        # first part: save wikipedia page html to wikipages directory
        page = response.url.split("/")[3]
        print('------PAGE------')
        print(page)
        page_dirname = 'investopediapages'
        filename = '%s.html' % page
        with open(os.path.join(page_dirname,filename), 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename) 

        # second part: extract text for the item for document corpus
        item = WebfocusedcrawlItem()
        item['url'] = response.url
        item['title'] = response.css('h1::text').extract_first()
        item['text'] = response.xpath('//div[@id="mntl-sc-page_1-0"]//text()')\
                           .extract()                                                             
        tags_list = [response.url.split("/")[2],
                     response.url.split("/")[3]]
        more_tags = [x.lower() for x in remove_stopwords(response.url\
                       	    .split("/")[2].split("_"))]
        for tag in more_tags:
            tag = re.sub('[^a-zA-Z]', '', tag)  # alphanumeric values only  
            tags_list.append(tag)
        item['tags'] = tags_list                 
        return item 
