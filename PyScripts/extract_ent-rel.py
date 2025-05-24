# This script extracts entities and relations from the text
# It is used to extract the entities and relations from the text
# It is called by the map_to_gel.py script
# Run this script in project root using command: python PyScripts/extract_ent-rel.py

import json
import re
import spacy

# === Load spaCy model ===
nlp = spacy.load("en_core_web_sm")

# === Config ===
INPUT_FILE = 'data/processed/cleaned_data.jsonl'
OUTPUT_FILE = 'data/processed/entities_extracted.jsonl'

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

# === Helper: Match company from text ===
def find_company(text):
    found = []
    for name, ticker in COMPANY_KEYWORDS.items():
        if name in text:
            found.append({"name": name, "ticker": ticker})
    return found

# === Entity Extraction ===
def extract_entities(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ in {"ORG", "PRODUCT", "GPE", "PERSON"}:
            entities.append({"text": ent.text, "label": ent.label_})
    return entities

# === Dependency-Based Relation Extraction ===
def extract_relations(text):
    doc = nlp(text)
    relations = []
    for sent in doc.sents:
        subj = ""
        obj = ""
        verb = ""
        for token in sent:
            if "subj" in token.dep_:
                subj = token.text
                verb = token.head.lemma_
                for child in token.head.children:
                    if "obj" in child.dep_:
                        obj = child.text
        if subj and verb and obj:
            relations.append({"subject": subj, "relation": verb, "object": obj, "sentence": sent.text})
    return relations

def main():
    results = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            full_text = f"{item['title']} {item['description']} {item['content']}"
            entities = extract_entities(full_text)
            companies = find_company(full_text)
            relations = extract_relations(full_text)
            results.append({
                "url": item["url"],
                "entities": entities,
                "companies": companies,
                "relations": relations,
                "publishedAt": item["publishedAt"],
                "title": item["title"],
                "description": item["description"],
                "content": item["content"]
            })

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        for entry in results:
            out.write(json.dumps(entry) + '\n')

if __name__ == '__main__':
    main()
