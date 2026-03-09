import re
import spacy
from typing import Optional

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None


def preprocess_text(text: str) -> str:
    if not text:
        return ""
    
    text = text.lower()
    
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    text = re.sub(r'\s+', ' ', text)
    
    if nlp:
        doc = nlp(text)
        tokens = [token.text for token in doc if not token.is_stop and not token.is_punct and token.text.strip()]
        text = ' '.join(tokens)
    
    return text.strip()