from .blacklist import TITLE_BLACKLIST, SCHOLARSHIP_KEYWORDS
import re

def is_garbage_title(title):
    if not title or len(title.strip()) < 10:
        return True
    
    title_lower = title.lower().strip()
    
    # Check blacklist
    for blocked in TITLE_BLACKLIST:
        if blocked in title_lower:
            return True
    
    # Check if it's just a number or date
    if re.match(r'^[\d\s\-/]+$', title):
        return True
    
    # Check if too generic
    generic_only = ['scholarship', 'university', 'study', 'course', 'program']
    words = title_lower.split()
    if len(words) <= 2 and all(w in generic_only for w in words):
        return True
    
    return False

def has_scholarship_signal(text):
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SCHOLARSHIP_KEYWORDS)

def calculate_title_confidence(title):
    score = 50
    
    if not title:
        return 0
    
    title_lower = title.lower()
    
    # Good signals
    if any(kw in title_lower for kw in SCHOLARSHIP_KEYWORDS):
        score += 30
    
    if re.search(r'\d{4}', title):  # Year
        score += 10
    
    if len(title.split()) >= 3:
        score += 10
    
    # Bad signals
    if any(bad in title_lower for bad in TITLE_BLACKLIST):
        score -= 40
    
    if title.count('|') > 0 or title.count('-') > 2:
        score -= 10
    
    return max(0, min(100, score))