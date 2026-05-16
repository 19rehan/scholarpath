import re

DEGREE_PATTERNS = {
    'Bachelor': [
        r'\bbach[ea]lor', r'\bundergraduate', r'\bBA\b', r'\bBS\b', r'\bBSc\b'
    ],
    'Master': [
        r'\bmaster', r'\bpostgraduate', r'\bMA\b', r'\bMS\b', r'\bMSc\b', r'\bMBA\b'
    ],
    'PhD': [
        r'\bphd\b', r'\bdoctoral', r'\bdoctorate'
    ]
}

def extract_degree_level(text):
    if not text:
        return None
    
    text_lower = text.lower()
    
    found_degrees = []
    
    for degree, patterns in DEGREE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                found_degrees.append(degree)
                break
    
    if not found_degrees:
        return None
    
    # Return comma-separated if multiple
    return ','.join(sorted(set(found_degrees)))