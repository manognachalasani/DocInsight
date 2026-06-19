# tests/test_parser.py
import os
import sys
    
print(os.getcwd())
sys.path.append('.')
from src.parser import DocumentParser
import json

parser = DocumentParser()
docs = parser.parse_directory("data/sample_docs")
print(f"Parsed {len(docs)} documents")
for doc in docs:
    print(f"  {doc.filename}: {len(doc.pages)} pages, {len(doc.tables)} tables")