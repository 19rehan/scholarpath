import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
import re
from datetime import datetime

def get_headers():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    ]
    return {
        "User-Agent": random.choice(agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

def smart_fetch(url, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(2, 4))
            r = requests.get(url, headers=get_headers(), timeout=15)
            if r.status_code == 200:
                return r
            print(f"  ⚠ Status {r.status_code} attempt {attempt+1}")
            time.sleep(random.uniform(3, 6))
        except Exception as e:
            print(f"  ✗ Error: {e}")
            time.sleep(4)
    return None

def setup_database():
    conn = sqlite3.connect('scholarships.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            country TEXT,
            deadline TEXT,
            link TEXT UNIQUE,
            source TEXT,
            scraped_date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS university_scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            university_name TEXT,
            country TEXT,
            scholarship_title TEXT,
            description TEXT,
            eligibility TEXT,
            gpa_required TEXT,
            ielts_required TEXT,
            deadline TEXT,
            funding_type TEXT,
            degree_level TEXT,
            department TEXT,
            apply_link TEXT UNIQUE,
            scraped_date TEXT
        )
    ''')
    conn.commit()
    return conn

def extract_ielts(text):
    patterns = [
        r'ielts[:\s]*(\d+\.?\d*)',
        r'ielts.*?(\d+\.?\d+)',
        r'(\d+\.?\d*)\s*(?:in|for)?\s*ielts',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    if re.search(r'ielts', text, re.IGNORECASE):
        return "Required - check website"
    return "Not mentioned"

def extract_gpa(text):
    patterns = [
        r'gpa[:\s]*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*gpa',
        r'grade point[:\s]*(\d+\.?\d*)',
        r'(\d{2,3})%?\s*(?:or above|minimum|at least)',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return "Check website"

def extract_deadline(text):
    months = "january|february|march|april|may|june|july|august|september|october|november|december"
    patterns = [
        rf'deadline[:\s]*(\d{{1,2}}\s+(?:{months})\s+\d{{4}})',
        rf'deadline[:\s]*((?:{months})\s+\d{{1,2}},?\s+\d{{4}})',
        rf'closing date[:\s]*((?:{months})\s+\d{{1,2}},?\s+\d{{4}})',
        rf'apply by[:\s]*((?:{months})\s+\d{{1,2}},?\s+\d{{4}})',
        rf'(\d{{1,2}}\s+(?:{months})\s+\d{{4}})',
        rf'((?:{months})\s+\d{{4}})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return "See official website"

def extract_degree_level(text):
    levels = []
    if re.search(r'\bundergraduate|bachelor\b', text, re.IGNORECASE):
        levels.append("Undergraduate")
    if re.search(r'\bpostgraduate|master\b', text, re.IGNORECASE):
        levels.append("Postgraduate")
    if re.search(r'\bphd|doctoral|doctorate\b', text, re.IGNORECASE):
        levels.append("PhD")
    return ", ".join(levels) if levels else "All levels"

def extract_funding(text):
    if re.search(r'full.?fund|fully.?fund|100%', text, re.IGNORECASE):
        return "Fully Funded"
    if re.search(r'partial|50%|tuition only', text, re.IGNORECASE):
        return "Partially Funded"
    if re.search(r'stipend|living allowance', text, re.IGNORECASE):
        return "Stipend Included"
    return "Check website"

def save_university_scholarship(conn, uni_name, country, title, desc,
                                 eligibility, gpa, ielts, deadline,
                                 funding, degree, dept, link):
    if not title or len(title) < 10 or not link:
        return False
    try:
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO university_scholarships
            (university_name, country, scholarship_title, description,
             eligibility, gpa_required, ielts_required, deadline,
             funding_type, degree_level, department, apply_link, scraped_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (uni_name, country, title, desc, eligibility, gpa, ielts,
              deadline, funding, degree, dept, link,
              datetime.now().strftime("%Y-%m-%d")))
        # Also add to main scholarships table for website display
        c.execute('''
            INSERT OR IGNORE INTO scholarships
            (title, description, country, deadline, link, source, scraped_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, desc[:300], country, deadline, link,
              f"university_{uni_name.lower().replace(' ','_')}",
              datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        return True
    except Exception as e:
        print(f"  ✗ Save error: {e}")
        return False

# ─── UNIVERSITY SCHOLARSHIP PAGES ─────────────────────────
# These are direct scholarship pages from real universities
UNIVERSITIES = [
    # UK Universities
    {
        "name": "University of Edinburgh",
        "country": "UK",
        "urls": [
            "https://www.ed.ac.uk/student-funding/postgraduate/international/global/global-research",
            "https://www.ed.ac.uk/student-funding/postgraduate/international",
        ]
    },
    {
        "name": "University of Manchester",
        "country": "UK",
        "urls": [
            "https://www.manchester.ac.uk/study/international/finance-and-scholarships/scholarships-and-bursaries/",
        ]
    },
    {
        "name": "University of Sheffield",
        "country": "UK",
        "urls": [
            "https://www.sheffield.ac.uk/international/fees-and-funding/scholarships",
        ]
    },
    {
        "name": "University of Birmingham",
        "country": "UK",
        "urls": [
            "https://www.birmingham.ac.uk/international/students/finance/scholarships",
        ]
    },
    # Australia
    {
        "name": "University of Melbourne",
        "country": "Australia",
        "urls": [
            "https://scholarships.unimelb.edu.au/",
        ]
    },
    {
        "name": "University of Queensland",
        "country": "Australia",
        "urls": [
            "https://scholarships.uq.edu.au/",
        ]
    },
    {
        "name": "UNSW Sydney",
        "country": "Australia",
        "urls": [
            "https://www.unsw.edu.au/study/scholarships",
        ]
    },
    # Canada
    {
        "name": "University of Toronto",
        "country": "Canada",
        "urls": [
            "https://www.sgs.utoronto.ca/awards/",
        ]
    },
    {
        "name": "University of British Columbia",
        "country": "Canada",
        "urls": [
            "https://students.ubc.ca/enrolment/finances/scholarships-awards-bursaries",
        ]
    },
    # Germany
    {
        "name": "DAAD Germany",
        "country": "Germany",
        "urls": [
            "https://www.daad.de/en/study-and-research-in-germany/scholarships/",
        ]
    },
    # USA
    {
        "name": "Fulbright Program",
        "country": "USA",
        "urls": [
            "https://foreign.fulbrightonline.org/",
        ]
    },
    # New Zealand
    {
        "name": "University of Auckland",
        "country": "New Zealand",
        "urls": [
            "https://www.auckland.ac.nz/en/study/fees-and-money/scholarships.html",
        ]
    },
    # Norway (free tuition)
    {
        "name": "University of Oslo",
        "country": "Norway",
        "urls": [
            "https://www.uio.no/english/studies/admission/scholarships/",
        ]
    },
    # Netherlands
    {
        "name": "University of Amsterdam",
        "country": "Netherlands",
        "urls": [
            "https://www.uva.nl/en/education/master-s/scholarships--tuition/scholarships-and-loans/scholarships-and-loans.html",
        ]
    },
    # Ireland
    {
        "name": "Trinity College Dublin",
        "country": "Ireland",
        "urls": [
            "https://www.tcd.ie/study/fees-funding/scholarships/",
        ]
    },
]

def scrape_university(conn, uni):
    print(f"\n[UNI] {uni['name']} ({uni['country']})")
    saved = 0

    for url in uni['urls']:
        print(f"  → {url[:70]}")
        response = smart_fetch(url)
        if not response:
            print("  ✗ Could not fetch")
            continue

        soup = BeautifulSoup(response.text, 'lxml')

        # Remove noise
        for tag in soup.find_all(['nav','footer','script','style','aside','header']):
            tag.decompose()

        full_text = soup.get_text(separator=' ', strip=True)
        full_text = ' '.join(full_text.split())

        # Find scholarship sections
        scholarship_sections = []

        # Method 1: Find by heading keywords
        for heading in soup.find_all(['h1','h2','h3','h4','h5']):
            text = heading.get_text(strip=True)
            if any(kw in text.lower() for kw in
                   ['scholarship','award','bursary','fellowship','grant','funding','prize']):
                # Get surrounding content
                section_text = text
                next_elem = heading.find_next_sibling()
                for _ in range(5):
                    if next_elem and next_elem.name in ['p','ul','div','table']:
                        section_text += " " + next_elem.get_text(separator=' ', strip=True)
                        next_elem = next_elem.find_next_sibling()
                    else:
                        break

                # Find apply link
                apply_link = url
                parent = heading.parent
                if parent:
                    a = parent.find('a', href=True)
                    if a:
                        href = a['href']
                        if href.startswith('http'):
                            apply_link = href
                        elif href.startswith('/'):
                            domain = '/'.join(url.split('/')[:3])
                            apply_link = domain + href

                scholarship_sections.append({
                    "title": text,
                    "text": section_text,
                    "link": apply_link
                })

        # Method 2: Find scholarship links directly
        for a in soup.find_all('a', href=True):
            link_text = a.get_text(strip=True)
            href = a['href']
            if any(kw in link_text.lower() for kw in
                   ['scholarship','award','bursary','fellowship','grant']):
                if len(link_text) > 15:
                    if not href.startswith('http'):
                        domain = '/'.join(url.split('/')[:3])
                        href = domain + href if href.startswith('/') else url + '/' + href
                    scholarship_sections.append({
                        "title": link_text,
                        "text": link_text,
                        "link": href
                    })

        print(f"  Found {len(scholarship_sections)} scholarship mentions")

        # Process each scholarship found
        seen_titles = set()
        for section in scholarship_sections[:20]:
            title = section['title']
            if title in seen_titles or len(title) < 10:
                continue
            seen_titles.add(title)

            text = section['text']
            link = section['link']

            # Extract all details
            ielts = extract_ielts(full_text)
            gpa = extract_gpa(full_text)
            deadline = extract_deadline(text + " " + full_text[:2000])
            degree = extract_degree_level(text + " " + full_text[:2000])
            funding = extract_funding(text + " " + full_text[:2000])

            # Build description
            desc = text[:400] if len(text) > 50 else f"Scholarship offered by {uni['name']} for international students."

            # Eligibility snippet
            eligibility = f"International students applying to {uni['name']}"
            for kw in ['open to','eligible','must be','applicants must','requirements']:
                idx = full_text.lower().find(kw)
                if idx != -1:
                    eligibility = full_text[idx:idx+200]
                    break

            ok = save_university_scholarship(
                conn,
                uni['name'], uni['country'],
                title, desc, eligibility,
                gpa, ielts, deadline,
                funding, degree, "",
                link
            )
            if ok:
                print(f"  ✓ {title[:60]}")
                print(f"    Deadline: {deadline} | IELTS: {ielts} | Funding: {funding}")
                saved += 1

    return saved

# ─── MAIN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("   UNIVERSITY SCHOLARSHIP SCRAPER")
    print(f"   Targeting {len(UNIVERSITIES)} universities")
    print("=" * 55)

    conn = setup_database()
    total_saved = 0

    for uni in UNIVERSITIES:
        saved = scrape_university(conn, uni)
        total_saved += saved
        time.sleep(random.uniform(3, 6))

    # Final count
    c = conn.cursor()
    main_total = c.execute("SELECT COUNT(*) FROM scholarships").fetchone()[0]
    uni_total = c.execute("SELECT COUNT(*) FROM university_scholarships").fetchone()[0]

    print(f"\n{'=' * 55}")
    print(f"  University scholarships saved : {total_saved}")
    print(f"  Total in main table          : {main_total}")
    print(f"  Total in university table    : {uni_total}")
    print(f"{'=' * 55}")

    conn.close()