# This script maps the entities and relations to the GEL format
# It is used to ingest the data into the GEL database
# It is called by the ingest_gel.py script


import json
import re
from collections import defaultdict

# === Config ===
INPUT_FILE = 'data/processed/entities_extracted.jsonl'
OUTPUT_ENTITIES = 'data/processed/gel_entities.jsonl'
OUTPUT_RELATIONS = 'data/processed/gel_relations.jsonl'

# === Known companies ===
COMPANY_KEYWORDS = {
    "eli lilly": "LLY",
    "united health": "UNH",
    "johnson & johnson": "JNJ",
    "abbvie": "ABBV",
    "abbott": "ABT",
    "merck": "MRK",
    "intuitive surgical": "ISRG",
    "thermo fisher": "TMO",
    "amgen": "AMGN",
    "boston scientific": "BSX"
}

# === Data holders ===
entity_set = set()
relations = []

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        url = item.get("url", "")
        date = item.get("publishedAt", "")

        title = item.get("title", "")
        description = item.get("description", "")
        content = item.get("content", "")
        text_blob = " ".join([title, description, content]).lower()

        comp_ticker = None

        # Prefer matching company name from the companies list if available
        companies = item.get("companies", [])
        if companies:
            name = companies[0].get("name", "").lower()
            for key, ticker in COMPANY_KEYWORDS.items():
                if key in name:
                    comp_ticker = ticker
                    break

        # Fallback to substring match in the full text blob
        if not comp_ticker:
            for name, ticker in COMPANY_KEYWORDS.items():
                if name in text_blob:
                    comp_ticker = ticker
                    break

        print(f"Matched company: {comp_ticker} from text: {text_blob[:120]}")

        for ent in item.get("entities", []):
            entity_set.add((ent["text"], ent["label"]))

        for rel in item.get("relations", []):
            relations.append({
                "subject": rel["subject"],
                "relation": rel["relation"],
                "object": rel["object"],
                "sentence": rel.get("sentence", ""),
                "company": comp_ticker,
                "date": date,
                "url": url,
                "title": title,
                "description": description,
                "content": content
            })

# === Output entities ===
with open(OUTPUT_ENTITIES, 'w', encoding='utf-8') as ef:
    for name, label in sorted(entity_set):
        ef.write(json.dumps({"name": name, "label": label}) + '\n')

# === Output relations ===
with open(OUTPUT_RELATIONS, 'w', encoding='utf-8') as rf:
    for rel in relations:
        rf.write(json.dumps(rel) + '\n')

