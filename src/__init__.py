from parser import DocumentParser
from cleaner import TextCleaner
from pathlib import Path
from typing import List
import json
from dataclasses import asdict

class DocumentPipeline:
    def __init__(self):
        self.parser = DocumentParser()
        self.cleaner = TextCleaner()
    
    def process_directory(self, input_dir: str, output_file: str = None) -> List[dict]:
        docs = self.parser.parse_directory(input_dir)
        cleaned_docs = []
        for doc in docs:
            cleaned = self.cleaner.clean(doc)
            cleaned_docs.append(cleaned)
            print(f"✓ Cleaned: {cleaned.filename} ({len(cleaned.pages)} pages)")
        
        if output_file:
            self._save_to_jsonl(cleaned_docs, output_file)
        
        return cleaned_docs
    
    def _save_to_jsonl(self, documents, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            for doc in documents:
                f.write(json.dumps(self._doc_to_dict(doc), ensure_ascii=False) + '\n')
        print(f"Saved {len(documents)} documents to {output_file}")
    
    def _doc_to_dict(self, doc):
        return {
            "doc_id": doc.doc_id,
            "filename": doc.filename,
            "title": doc.title,
            "author": doc.author,
            "pages": doc.pages,
            "tables": doc.tables
        }

# Quick test
if __name__ == "__main__":
    pipeline = DocumentPipeline()
    pipeline.process_directory("data/sample_docs", "data/cleaned_docs.jsonl")