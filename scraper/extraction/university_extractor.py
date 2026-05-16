import re
from urllib.parse import urlparse

def extract_university_name(soup, url):
    # From domain
    domain = urlparse(url).netloc
    
    # Remove common TLDs and subdomains
    domain_clean = re.sub(r'^(www\.|scholarship\.|apply\.)', '', domain)
    domain_clean = re.sub(r'\.(edu|ac\.uk|edu\.au|com|org|net).*$', '', domain_clean)
    
    # Check for university in text
    text = soup.get_text()
    
    uni_patterns = [
        r'([A-Z][a-z]+\s+University)',
        r'(University\s+of\s+[A-Z][a-z]+)',
    ]
    
    for pattern in uni_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    # Fallback to domain
    if 'university' in domain_clean or 'college' in domain_clean:
        return domain_clean.replace('-', ' ').replace('_', ' ').title()
    
    return None