# This script loads the jl files from multiple input paths
# The text is cleaned and then saved to a new jl file
# Stock data is not cleaned - it is processed in a separate script
# Run this script in project root using command: python PyScripts/clean_text.py

import json
import re
import os
from glob import glob
from dateutil import parser
from datetime import datetime
import logging

# === CONFIG ===
INPUT_PATHS = [
    'Investopedia/WebFocusedCrawlWork/items.jl',
    'WebFocusedCrawlWork/output/items.jl',
    'WebFocusedCrawlWork/items.jl'
]
OUTPUT_PATH = 'data/processed/cleaned_data.jsonl'

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/processed/cleaning.log'),
        logging.StreamHandler()
    ]
)

# === TEXT CLEANING ===
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_date_from_url(url):
    """Extract date from URL patterns like '...-YYYY-MM-DD-...' or '...-YYYYMMDD-...'"""
    try:
        # Look for date patterns in URL
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{4}\d{2}\d{2})',    # YYYYMMDD
            r'(\d{4}/\d{2}/\d{2})'   # YYYY/MM/DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, url)
            if match:
                date_str = match.group(1)
                # Convert YYYYMMDD to YYYY-MM-DD if needed
                if len(date_str) == 8:
                    date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                return parser.parse(date_str).isoformat()
        return None
    except Exception as e:
        logging.warning(f"Error parsing date from URL {url}: {str(e)}")
        return None

def extract_date_from_text(text):
    """Extract date from article text content"""
    try:
        # Look for common date patterns in text
        text_date_patterns = [
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
            r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}',
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}'
        ]
        
        for pattern in text_date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return parser.parse(match.group(0)).isoformat()
        return None
    except Exception as e:
        logging.warning(f"Error parsing date from text: {str(e)}")
        return None

def extract_source_from_url(url):
    """Extract source name from URL (e.g., 'investopedia.com' -> 'investopedia')"""
    try:
        # Remove protocol and www if present
        domain = re.sub(r'^https?://(www\.)?', '', url)
        # Get the first part of the domain
        source = domain.split('.')[0]
        return source.capitalize()  # Capitalize first letter
    except Exception as e:
        logging.warning(f"Error extracting source from URL {url}: {str(e)}")
        return ""

# === MAIN PROCESS ===
def process_file(filepath):
    cleaned = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line)
                url = item.get("url", "")
                
                # Try to get source from item first, then from URL
                source = item.get("source", {})
                source_name = source.get("name", "") if isinstance(source, dict) else ""
                if not source_name:
                    source_name = extract_source_from_url(url)
                
                # Try to get date from URL first, then from text content
                text = item.get("text", "")
                
                publication_date = extract_date_from_url(url)
                if not publication_date:
                    publication_date = extract_date_from_text(text)
                
                if publication_date:
                    logging.info(f"Successfully extracted date {publication_date} from {'URL' if extract_date_from_url(url) else 'text'}: {url}")
                else:
                    logging.warning(f"No date found for URL: {url}")

                cleaned.append({
                    "title": clean_text(item.get("title")),
                    "description": clean_text(item.get("description")),
                    "content": clean_text(item.get("content")),
                    "author": item.get("author", ""),
                    "publication_date": publication_date,
                    "source": source_name,
                    "url": url
                })

            except json.JSONDecodeError:
                logging.error(f"Failed to parse JSON from line in {filepath}")
                continue
            except Exception as e:
                logging.error(f"Error processing item in {filepath}: {str(e)}")
                continue
    return cleaned

def main():
    all_cleaned = []
    for path in INPUT_PATHS:
        for filepath in glob(path):
            logging.info(f"Processing file: {filepath}")
            all_cleaned.extend(process_file(filepath))

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out_file:
        for entry in all_cleaned:
            out_file.write(json.dumps(entry) + '\n')
    
    logging.info(f"Processed {len(all_cleaned)} articles. Output saved to {OUTPUT_PATH}")

if __name__ == '__main__':
    main()
