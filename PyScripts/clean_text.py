# This script loads the jl files from multiple input paths
# The text is cleaned and then saved to a new jl file
# Stock data is not cleaned - it is processed in a separate script
# Run this script in project root using command: python PyScripts/clean_text.py

import json
import re
import os
from glob import glob

# === CONFIG ===
INPUT_PATHS = [
    'Investopedia/WebFocusedCrawlWork/items.jl',
    'WebFocusedCrawlWork/output/items.jl',
    'WebFocusedCrawlWork/items.jl'
]
OUTPUT_PATH = 'data/processed/cleaned_data.jsonl'

# === TEXT CLEANING ===
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# === MAIN PROCESS ===
def process_file(filepath):
    cleaned = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line)
                source = item.get("source", {})
                source_name = source.get("name", "") if isinstance(source, dict) else ""
                cleaned.append({
                    "title": clean_text(item.get("title")),
                    "description": clean_text(item.get("description")),
                    "content": clean_text(item.get("content")),
                    "author": item.get("author", ""),
                    "publishedAt": item.get("publishedAt", ""),
                    "source": source_name,
                    "url": item.get("url", "")
                })
            except json.JSONDecodeError:
                continue
    return cleaned

def main():
    all_cleaned = []
    for path in INPUT_PATHS:
        for filepath in glob(path):
            all_cleaned.extend(process_file(filepath))

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out_file:
            for entry in all_cleaned:
                out_file.write(json.dumps(entry) + '\n')

if __name__ == '__main__':
    main()
