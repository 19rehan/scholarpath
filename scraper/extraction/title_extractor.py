from bs4 import BeautifulSoup
from ..cleaning.garbage_filter import is_garbage_title, calculate_title_confidence
import re

def extract_clean_title(soup, url=''):
    candidates = []
    
    # Priority 1: Article/main heading
    for tag in ['h1', 'h2']:
        headers = soup.find_all(tag, limit=3)
        for h in headers:
            text = h.get_text(strip=True)
            if text and not is_garbage_title(text):
                confidence = calculate_title_confidence(text)
                candidates.append((text, confidence, 'heading'))
    
    # Priority 2: Meta title
    meta_title = soup.find('meta', property='og:title')
    if meta_title and meta_title.get('content'):
        text = meta_title['content'].strip()
        if not is_garbage_title(text):
            confidence = calculate_title_confidence(text)
            candidates.append((text, confidence, 'meta'))
    
    # Priority 3: Page title
    if soup.title and soup.title.string:
        text = soup.title.string.strip()
        text = clean_title_suffix(text)
        if not is_garbage_title(text):
            confidence = calculate_title_confidence(text)
            candidates.append((text, confidence, 'title'))
    
    # Sort by confidence
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    if candidates and candidates[0][1] >= 60:
        return candidates[0][0]
    
    return None

def clean_title_suffix(title):
    # Remove common website suffixes
    patterns = [
        r'\s*[|\-–—]\s*.*?(university|college|portal|website|scholarships?).*$',
        r'\s*[|\-–—]\s*[A-Z][a-zA-Z\s]+\.(com|org|net|edu).*$',
    ]
    
    for pattern in patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    return title.strip()