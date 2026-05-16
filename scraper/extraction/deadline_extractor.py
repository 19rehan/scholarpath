import re
from datetime import datetime
from dateutil import parser

def extract_deadline(soup, text=''):
    search_text = text if text else soup.get_text()
    
    patterns = [
        r'deadline[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        r'apply\s+by[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        r'closing\s+date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'([A-Za-z]+\s+\d{1,2},\s+\d{4})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, search_text, re.IGNORECASE)
        for match in matches:
            try:
                date = parser.parse(match, fuzzy=True)
                if date > datetime.now():
                    return date.strftime('%Y-%m-%d')
            except:
                continue
    
    return None
