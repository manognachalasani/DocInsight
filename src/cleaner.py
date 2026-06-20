import re
import unicodedata
from typing import List
from parser import ParsedDocument
import copy

class TextCleaner:
    def __init__(self, language: str = "fr"):
        self.language = language
        self.boilerplate_patterns = [

            # ==========================================
            # Page Numbers (English & French)
            # ==========================================
            r"\bPage\s+\d+\s+(?:of|sur)\s+\d+\b",   # Page 3 of 20 / Page 3 sur 20
            r"^\s*Page\s+\d+\s*$",                  # Page 5
            r"^\s*\d+\s*$",                         # Standalone page number

            # ==========================================
            # Confidentiality Labels
            # ==========================================
            r"\bConfidential\b",
            r"\bConfidentiel\b",
            r"\bStrictly Confidential\b",
            r"\bStrictement confidentiel\b",

            # ==========================================
            # Internal Distribution Labels
            # ==========================================
            r"\bFor Internal Use Only\b",
            r"\bInternal Use Only\b",
            r"\bUsage interne uniquement\b",
            r"\bRéservé à un usage interne\b",

            # ==========================================
            # Draft Watermarks
            # ==========================================
            r"\bDRAFT\b",
            r"\bDraft\b",
            r"\bBROUILLON\b",
            r"\bBrouillon\b",

            # ==========================================
            # Generic Generated/Printed Footer
            # (Only the timestamp itself, not document content)
            # ==========================================
            r"\bDocument généré le\s+.*",
            r"\bGenerated on\s+.*",
            r"\bPrinted on\s+.*",

            # ==========================================
            # Decorative Horizontal Separators
            # ==========================================
            r"^[-=_]{5,}$",
        ]
        
    def clean(self, document: ParsedDocument) -> ParsedDocument:
        """
        Returns a cleaned copy of the document without modifying the original.
        """
        # Create a deep copy so nested lists are also copied
        cleaned_document = copy.deepcopy(document)

        cleaned_pages = []
        for page in cleaned_document.pages:
            page = self.normalize_unicode(page)
            page = self.remove_headers_footers(page)
            page = self.remove_boilerplate(page)
            page = self.fix_hyphenation(page)
            page = self.normalize_whitespace(page)

            if page.strip():
                cleaned_pages.append(page)

        cleaned_document.pages = cleaned_pages

        # Clean tables
        cleaned_tables = []
        for table in cleaned_document.tables:
            table = self.normalize_unicode(table)
            table = self.normalize_whitespace(table)
            cleaned_tables.append(table)

        cleaned_document.tables = cleaned_tables

        return cleaned_document
    
    def normalize_unicode(self, text: str) -> str:
        # NFKD normalization for French accents
        text = unicodedata.normalize('NFKD', text)
        # Fix common encoding issues
        text = text.replace('\u2019', "'")  # Right single quote
        text = text.replace('\u2018', "'")  # Left single quote
        text = text.replace('\u201c', '"')  # Left double quote
        text = text.replace('\u201d', '"')  # Right double quote
        text = text.replace('\u00a0', ' ')  # Non-breaking space
        return text
    
    def remove_headers_footers(self, text: str) -> str:
        lines = text.split('\n')
        # Remove first and last line if they look like headers/footers
        if lines and re.match(r'^\s*\d+\s*$', lines[0].strip()):
            lines = lines[1:]
        if lines and re.match(r'^\s*\d+\s*$', lines[-1].strip()):
            lines = lines[:-1]
        return '\n'.join(lines)
    
    def remove_boilerplate(self, text: str) -> str:
        for pattern in self.boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text
    
    def fix_hyphenation(self, text: str) -> str:
        # Fix French hyphenation: "dévelop-\npement" -> "développement"
        text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
        return text
    
    def normalize_whitespace(self, text: str) -> str:
        # Collapse multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Collapse multiple spaces
        text = re.sub(r' {2,}', ' ', text)
        # Fix spaces before French punctuation
        if self.language == "fr":
            text = re.sub(r' ([;:!?])', r'\1', text)
            text = re.sub(r'(\S)  +(\S)', r'\1 \2', text)
        return text.strip()
    
    def detect_language(self, text: str) -> str:
        # Simple heuristic for French detection
        french_indicators = ['le ', 'la ', 'les ', 'des ', 'une ', 'un ', 'du ', 'de ', 'et ', 'est ', 'dans ', 'pour ', 'sur ']
        text_lower = text.lower()
        score = sum(1 for word in french_indicators if word in text_lower)
        return "fr" if score > 3 else "en"