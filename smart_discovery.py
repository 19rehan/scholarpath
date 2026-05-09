import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
import re
from datetime import datetime

# ─── HEADERS ──────────────────────────────────────────────
def get_headers():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    ]
    return {
        "User-Agent": random.choice(agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
    }

def smart_fetch(url, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(2, 4))
            r = requests.get(url, headers=get_headers(), timeout=15)
            if r.status_code == 200:
                return r
            time.sleep(random.uniform(3, 6))
        except Exception as e:
            time.sleep(4)
    return None

# ─── DATABASE ─────────────────────────────────────────────
def setup_db():
    conn = sqlite3.connect('scholarships.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scholarships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, description TEXT, country TEXT,
        deadline TEXT, link TEXT UNIQUE,
        source TEXT, scraped_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS university_scholarships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        university_name TEXT, country TEXT, region TEXT,
        scholarship_title TEXT, description TEXT,
        eligibility TEXT, gpa_required TEXT,
        ielts_required TEXT, deadline TEXT,
        funding_type TEXT, degree_level TEXT,
        apply_link TEXT UNIQUE, scraped_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS discovered_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE, domain TEXT,
        country TEXT, last_scraped TEXT,
        total_found INTEGER DEFAULT 0)''')
    conn.commit()
    return conn

def extract_ielts(text):
    for p in [r'ielts[:\s]*(\d+\.?\d*)', r'(\d+\.?\d*)\s*(?:in|for)?\s*ielts']:
        m = re.search(p, text, re.IGNORECASE)
        if m: return m.group(1)
    return "Required" if re.search(r'ielts', text, re.IGNORECASE) else "Not mentioned"

def extract_deadline(text):
    months = "january|february|march|april|may|june|july|august|september|october|november|december"
    for p in [
        rf'deadline[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'closing date[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'apply by[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'(\d{{1,2}}\s+(?:{months})\s+\d{{4}})',
        rf'((?:{months})\s+\d{{1,2}},?\s+\d{{4}})',
    ]:
        m = re.search(p, text, re.IGNORECASE)
        if m: return m.group(1).strip()
    return "See official website"

def extract_degree(text):
    levels = []
    if re.search(r'\bundergraduate|bachelor\b', text, re.IGNORECASE): levels.append("Bachelor")
    if re.search(r'\bmaster|postgraduate|msc|mba\b', text, re.IGNORECASE): levels.append("Master")
    if re.search(r'\bphd|doctoral\b', text, re.IGNORECASE): levels.append("PhD")
    return ", ".join(levels) if levels else "All levels"

def extract_funding(text):
    if re.search(r'full.?fund|fully.?fund|100%|full scholarship', text, re.IGNORECASE):
        return "Fully Funded"
    if re.search(r'partial|tuition only', text, re.IGNORECASE):
        return "Partial"
    if re.search(r'stipend|living allowance', text, re.IGNORECASE):
        return "Stipend"
    return "Check website"

def detect_country_from_domain(domain):
    tlds = {
        '.uk': 'UK', '.ac.uk': 'UK', '.edu.au': 'Australia',
        '.au': 'Australia', '.ca': 'Canada', '.de': 'Germany',
        '.fr': 'France', '.nl': 'Netherlands', '.se': 'Sweden',
        '.no': 'Norway', '.fi': 'Finland', '.dk': 'Denmark',
        '.ch': 'Switzerland', '.at': 'Austria', '.be': 'Belgium',
        '.it': 'Italy', '.es': 'Spain', '.pt': 'Portugal',
        '.pl': 'Poland', '.cz': 'Czech Republic', '.tr': 'Turkey',
        '.sa': 'Saudi Arabia', '.ae': 'UAE', '.qa': 'Qatar',
        '.jo': 'Jordan', '.cn': 'China', '.jp': 'Japan',
        '.kr': 'South Korea', '.my': 'Malaysia', '.sg': 'Singapore',
        '.th': 'Thailand', '.nz': 'New Zealand', '.za': 'South Africa',
        '.eg': 'Egypt', '.ma': 'Morocco', '.ng': 'Nigeria',
        '.br': 'Brazil', '.mx': 'Mexico', '.ar': 'Argentina',
        '.pk': 'Pakistan', '.in': 'India', '.bd': 'Bangladesh',
        '.edu': 'USA', '.edu.cn': 'China', '.edu.pk': 'Pakistan',
    }
    for tld, country in sorted(tlds.items(), key=lambda x: -len(x[0])):
        if domain.endswith(tld):
            return country
    return "International"

def save_scholarship(conn, uni_name, country, region, title,
                     desc, eligibility, ielts, deadline, funding, degree, link):
    if not title or len(title) < 8 or not link:
        return False
    try:
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO university_scholarships
            (university_name,country,region,scholarship_title,description,
             eligibility,gpa_required,ielts_required,deadline,funding_type,
             degree_level,apply_link,scraped_date)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (uni_name, country, region, title, desc[:400],
             eligibility[:300], "Check website", ielts, deadline,
             funding, degree, link, datetime.now().strftime("%Y-%m-%d")))
        c.execute('''INSERT OR IGNORE INTO scholarships
            (title,description,country,deadline,link,source,scraped_date)
            VALUES(?,?,?,?,?,?,?)''',
            (title, f"{uni_name} — {desc[:200]}", country, deadline,
             link, f"uni_{uni_name[:20].lower().replace(' ','_')}",
             datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        return True
    except:
        return False

# ══════════════════════════════════════════════════════════
# CORE ENGINE: GOOGLE SEARCH DISCOVERY
# Uses Google search to find scholarship pages from ANY
# university in the world automatically
# ══════════════════════════════════════════════════════════
def discover_via_google(conn, search_queries):
    """
    Searches Google for scholarship pages across the entire web.
    This discovers unis we never manually listed.
    """
    print("\n[DISCOVERY] Searching Google for scholarship pages worldwide...")
    discovered_urls = set()

    # Load already discovered
    c = conn.cursor()
    existing = c.execute("SELECT url FROM discovered_sources").fetchall()
    for row in existing:
        discovered_urls.add(row[0])

    new_sources = []

    for query in search_queries:
        print(f"\n  🔍 Google: {query}")
        # Use Google search URL
        google_url = f"https://www.google.com/search?q={query.replace(' ','+')}&num=20"
        r = smart_fetch(google_url)
        if not r:
            # Try Bing as backup
            bing_url = f"https://www.bing.com/search?q={query.replace(' ','+')}&count=20"
            r = smart_fetch(bing_url)
            if not r:
                print(f"  ✗ Could not reach search engine")
                continue

        soup = BeautifulSoup(r.text, 'lxml')

        # Extract all result links
        links = []
        # Google format
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Google wraps links
            if '/url?q=' in href:
                href = href.split('/url?q=')[1].split('&')[0]
            if href.startswith('http') and 'google' not in href:
                links.append(href)
            # Direct links too
            elif href.startswith('http') and not any(skip in href for skip in
                ['google','bing','facebook','twitter','youtube','instagram']):
                links.append(href)

        print(f"  Found {len(links)} result links")

        for url in links[:15]:
            if url not in discovered_urls:
                domain = url.split('/')[2] if len(url.split('/')) > 2 else url
                country = detect_country_from_domain(domain)
                try:
                    c.execute('''INSERT OR IGNORE INTO discovered_sources
                        (url, domain, country, last_scraped, total_found)
                        VALUES(?,?,?,?,0)''',
                        (url, domain, country, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit()
                    new_sources.append((url, domain, country))
                    discovered_urls.add(url)
                    print(f"  ✓ Discovered: {domain} ({country})")
                except:
                    pass

        time.sleep(random.uniform(5, 8))  # Polite Google delay

    return new_sources

# ══════════════════════════════════════════════════════════
# DEEP SCRAPER: Scrapes any discovered URL
# ══════════════════════════════════════════════════════════
def deep_scrape_url(conn, url, domain, country):
    r = smart_fetch(url)
    if not r:
        return 0

    soup = BeautifulSoup(r.text, 'lxml')
    for tag in soup.find_all(['nav','footer','script','style','aside']):
        tag.decompose()

    full_text = ' '.join(soup.get_text(separator=' ', strip=True).split())
    ielts = extract_ielts(full_text)
    deadline = extract_deadline(full_text)
    degree = extract_degree(full_text)
    funding = extract_funding(full_text)

    # Detect university name from page
    uni_name = domain
    title_tag = soup.find('title')
    if title_tag:
        uni_name = title_tag.get_text(strip=True)[:60]

    # Detect region
    region_map = {
        'UK': 'Europe', 'Germany': 'Europe', 'France': 'Europe',
        'Netherlands': 'Europe', 'Sweden': 'Europe', 'Norway': 'Europe',
        'Finland': 'Europe', 'Denmark': 'Europe', 'Switzerland': 'Europe',
        'Austria': 'Europe', 'Belgium': 'Europe', 'Italy': 'Europe',
        'Spain': 'Europe', 'Poland': 'Europe', 'Czech Republic': 'Europe',
        'Turkey': 'Middle East', 'Saudi Arabia': 'Middle East',
        'UAE': 'Middle East', 'Qatar': 'Middle East', 'Jordan': 'Middle East',
        'China': 'Asia', 'Japan': 'Asia', 'South Korea': 'Asia',
        'Malaysia': 'Asia', 'Singapore': 'Asia', 'Thailand': 'Asia',
        'Australia': 'Oceania', 'New Zealand': 'Oceania',
        'USA': 'North America', 'Canada': 'North America',
        'South Africa': 'Africa', 'Nigeria': 'Africa',
        'Egypt': 'Africa', 'Morocco': 'Africa',
        'Brazil': 'Latin America', 'Mexico': 'Latin America',
    }
    region = region_map.get(country, 'International')

    saved = 0
    seen = set()

    # Strategy 1: Headings with scholarship keywords
    for tag in soup.find_all(['h1','h2','h3','h4','h5']):
        text = tag.get_text(strip=True)
        if len(text) < 10 or text in seen:
            continue
        if any(kw in text.lower() for kw in
               ['scholarship','award','bursary','fellowship','grant',
                'funding','financial aid','stipend','prize','sponsorship']):
            seen.add(text)
            link = url
            a = tag.find('a', href=True) or tag.find_next('a', href=True)
            if a:
                href = a['href']
                if href.startswith('http'):
                    link = href
                elif href.startswith('/'):
                    link = f"https://{domain}{href}"

            desc_parts = []
            nxt = tag.find_next_sibling()
            for _ in range(3):
                if nxt and nxt.name in ['p','div','ul']:
                    desc_parts.append(nxt.get_text(strip=True))
                    nxt = nxt.find_next_sibling()
                else:
                    break
            desc = ' '.join(desc_parts)[:400] or f"Scholarship at {uni_name}"

            ok = save_scholarship(conn, uni_name, country, region,
                                  text, desc, f"International students",
                                  ielts, deadline, funding, degree, link)
            if ok:
                print(f"    ✓ {text[:65]}")
                saved += 1

    # Strategy 2: Anchor links with scholarship keywords
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        href = a['href']
        if len(text) < 12 or text in seen:
            continue
        if any(kw in text.lower() for kw in
               ['scholarship','award','bursary','fellowship','grant','funding']):
            seen.add(text)
            if not href.startswith('http'):
                href = f"https://{domain}{href}" if href.startswith('/') else url
            ok = save_scholarship(conn, uni_name, country, region,
                                  text, f"Scholarship at {uni_name}. Visit link for details.",
                                  "International students", ielts, deadline,
                                  funding, degree, href)
            if ok:
                print(f"    ✓ {text[:65]}")
                saved += 1

    # Strategy 3: Follow sub-links on same domain (go deeper)
    if saved == 0:
        print(f"    → Going deeper into sub-pages...")
        for a in soup.find_all('a', href=True):
            href = a['href']
            if any(kw in href.lower() for kw in
                   ['scholarship','award','funding','financial','bursary','fellowship']):
                if not href.startswith('http'):
                    href = f"https://{domain}{href}" if href.startswith('/') else url
                if domain in href and href not in seen:
                    seen.add(href)
                    sub_r = smart_fetch(href)
                    if sub_r:
                        sub_soup = BeautifulSoup(sub_r.text, 'lxml')
                        sub_text = ' '.join(sub_soup.get_text(separator=' ', strip=True).split())
                        for h in sub_soup.find_all(['h1','h2','h3']):
                            h_text = h.get_text(strip=True)
                            if len(h_text) > 10 and h_text not in seen:
                                if any(kw in h_text.lower() for kw in
                                       ['scholarship','award','fellowship','grant','funding']):
                                    seen.add(h_text)
                                    ok = save_scholarship(
                                        conn, uni_name, country, region,
                                        h_text, sub_text[:300],
                                        "International students",
                                        extract_ielts(sub_text),
                                        extract_deadline(sub_text),
                                        extract_funding(sub_text),
                                        extract_degree(sub_text), href)
                                    if ok:
                                        print(f"    ✓ (deep) {h_text[:60]}")
                                        saved += 1

    return saved

# ══════════════════════════════════════════════════════════
# SEARCH QUERIES — These discover unis from every corner
# of the world that no one has manually listed
# ══════════════════════════════════════════════════════════
DISCOVERY_QUERIES = [
    # By region
    "university scholarships international students Europe 2025 site:.edu OR site:.ac.uk OR site:.de OR site:.nl",
    "university scholarships international students Asia 2025 site:.edu.cn OR site:.ac.jp OR site:.ac.kr",
    "university scholarships Middle East international students 2025 site:.sa OR site:.ae OR site:.tr",
    "university scholarships Africa international students 2025 site:.ac.za OR site:.edu.eg",
    "university scholarships Australia New Zealand 2025 site:.edu.au OR site:.ac.nz",
    "university scholarships Canada 2025 site:.ca",
    "university scholarships Latin America 2025 site:.br OR site:.mx",

    # By funding type
    "fully funded scholarship international students 2025 apply now",
    "full scholarship international students no IELTS required 2025",
    "government scholarship 2025 international students apply",
    "tuition waiver scholarship international students 2025",

    # By degree
    "PhD scholarship fully funded international students 2025",
    "masters scholarship international students 2025 apply",
    "undergraduate scholarship international students 2025",

    # By country (hidden gems)
    "China scholarship council CSC 2025 apply international",
    "Turkey Burslari scholarship 2025 apply",
    "Korean government scholarship KGSP 2025",
    "Japanese MEXT scholarship 2025 international",
    "Hungary Stipendium scholarship 2025",
    "Romanian government scholarship 2025 international students",
    "Czech government scholarship 2025 international",
    "Polish government scholarship 2025 international",
    "Slovenian government scholarship 2025",
    "Slovak government scholarship 2025 international",
    "Estonian scholarship international students 2025",
    "Latvia scholarship international students 2025",
    "Lithuania scholarship international students 2025",
    "Kazakhstan scholarship international students 2025",
    "Malaysia scholarship international students 2025",
    "Thailand scholarship international students 2025",
    "Indonesia scholarship international students 2025",
    "Taiwan scholarship international students 2025",
    "Hong Kong scholarship international students 2025",
    "Egypt scholarship international students 2025",
    "Morocco scholarship international students 2025",
    "Jordan scholarship international students 2025",
    "Saudi Arabia scholarship international students 2025",
    "Qatar scholarship international students 2025",
    "UAE scholarship international students 2025",
    "Kuwait scholarship international students 2025",
    "Oman scholarship international students 2025",
    "Pakistan scholarship abroad 2025 apply",
    "India scholarship international students 2025",

    # Hidden university scholarships
    "small university scholarship international students Europe 2025",
    "private university scholarship developing countries 2025",
    "engineering scholarship international students 2025",
    "medical scholarship international students 2025",
    "computer science scholarship international students 2025",
    "business scholarship MBA international students 2025",
    "agriculture scholarship international students 2025",
    "arts scholarship international students 2025",

    # Aggregator sites we haven't hit yet
    "scholarship 2025 Pakistan India Bangladesh apply deadline",
    "new scholarship announced 2025 international",
    "scholarship portal 2025 worldwide students",
]

# ══════════════════════════════════════════════════════════
# SEED URLS — Starting points to crawl deeper
# These are scholarship listing pages, not individual unis
# From here we discover hundreds more
# ══════════════════════════════════════════════════════════
SEED_URLS = [
    # Aggregators
    ("https://www.scholars4dev.com/", "scholars4dev.com", "International"),
    ("https://www.scholars4dev.com/page/2/", "scholars4dev.com", "International"),
    ("https://www.scholars4dev.com/page/3/", "scholars4dev.com", "International"),
    ("https://www.scholars4dev.com/page/4/", "scholars4dev.com", "International"),
    ("https://www.scholars4dev.com/page/5/", "scholars4dev.com", "International"),
    ("https://scholarshipdb.net/scholarships", "scholarshipdb.net", "International"),
    ("https://scholarshipdb.net/scholarships?page=2", "scholarshipdb.net", "International"),
    ("https://scholarshipdb.net/scholarships?page=3", "scholarshipdb.net", "International"),
    ("https://www.afterschoolafrica.com/category/scholarships/", "afterschoolafrica.com", "Africa"),
    ("https://www.afterschoolafrica.com/category/scholarships/page/2/", "afterschoolafrica.com", "Africa"),
    ("https://www.opportunitiesforafricans.com/category/scholarships/", "opportunitiesforafricans.com", "Africa"),
    ("https://www.youthop.com/scholarships", "youthop.com", "International"),
    ("https://www.scholarshipsads.com/", "scholarshipsads.com", "International"),
    ("https://www.mastersportal.eu/scholarship/", "mastersportal.eu", "Europe"),
    ("https://www.phdportal.eu/scholarship/", "phdportal.eu", "Europe"),

    # Government portals
    ("https://www.campuschina.org/scholarships/index.html", "campuschina.org", "China"),
    ("https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do", "studyinkorea.go.kr", "South Korea"),
    ("https://www.studyinjapan.go.jp/en/smap_stopj-applications_scholarship.html", "studyinjapan.go.jp", "Japan"),
    ("https://www.turkiyeburslari.gov.tr/en", "turkiyeburslari.gov.tr", "Turkey"),
    ("https://www.daad.de/en/study-and-research-in-germany/scholarships/", "daad.de", "Germany"),
    ("https://www.chevening.org/scholarships/", "chevening.org", "UK"),
    ("https://cscuk.fcdo.gov.uk/scholarships/", "cscuk.fcdo.gov.uk", "UK"),
    ("https://foreign.fulbrightonline.org/", "fulbrightonline.org", "USA"),
    ("https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en", "eacea.ec.europa.eu", "Europe"),
    ("https://stipendiumhungaricum.hu/en/", "stipendiumhungaricum.hu", "Hungary"),
    ("https://www.scholarships.gc.ca/scholarships-bourses/index.aspx", "scholarships.gc.ca", "Canada"),
    ("https://www.studyinaustralia.gov.au/english/australian-scholarships", "studyinaustralia.gov.au", "Australia"),
    ("https://www.studyinnewzealand.govt.nz/how-to-apply/scholarships", "studyinnewzealand.govt.nz", "New Zealand"),
    ("https://www.studyineurope.eu/scholarships", "studyineurope.eu", "Europe"),
    ("https://www.estudyassistance.com/scholarships", "estudyassistance.com", "International"),

    # Region specific portals
    ("https://www.scholarshipsforpakistanis.com/", "scholarshipsforpakistanis.com", "Pakistan"),
    ("https://www.scholarshipsinpakistan.com/", "scholarshipsinpakistan.com", "Pakistan"),
    ("https://www.educationabroad.pk/scholarships/", "educationabroad.pk", "Pakistan"),
    ("https://propakistani.pk/scholarships/", "propakistani.pk", "Pakistan"),
    ("https://www.indiascholarships.net/", "indiascholarships.net", "India"),
    ("https://www.buddy4study.com/scholarships", "buddy4study.com", "India"),
]

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("   GLOBAL SCHOLARSHIP DISCOVERY ENGINE")
    print("   Finds scholarships from ANY university worldwide")
    print("=" * 60)

    conn = setup_db()
    total_saved = 0

    # PHASE 1: Scrape all seed URLs
    print(f"\n{'─'*60}")
    print(f"  PHASE 1: Scraping {len(SEED_URLS)} seed sources")
    print(f"{'─'*60}")

    for url, domain, country in SEED_URLS:
        print(f"\n→ {domain} ({country})")
        saved = deep_scrape_url(conn, url, domain, country)
        total_saved += saved
        print(f"  Saved: {saved}")
        time.sleep(random.uniform(2, 5))

    # PHASE 2: Google discovery — finds unis we never knew about
    print(f"\n{'─'*60}")
    print(f"  PHASE 2: Google discovery — finding unknown universities")
    print(f"{'─'*60}")

    # Run a subset of queries (full run takes hours)
    import random as rnd
    sample_queries = rnd.sample(DISCOVERY_QUERIES, min(20, len(DISCOVERY_QUERIES)))
    new_sources = discover_via_google(conn, sample_queries)

    # PHASE 3: Scrape all newly discovered URLs
    print(f"\n{'─'*60}")
    print(f"  PHASE 3: Scraping {len(new_sources)} newly discovered sources")
    print(f"{'─'*60}")

    for url, domain, country in new_sources:
        print(f"\n→ {url[:70]} ({country})")
        saved = deep_scrape_url(conn, url, domain, country)
        total_saved += saved
        print(f"  Saved: {saved}")
        time.sleep(random.uniform(3, 6))

    # PHASE 4: Also scrape previously discovered sources not scraped today
    print(f"\n{'─'*60}")
    print(f"  PHASE 4: Re-scraping previously discovered sources")
    print(f"{'─'*60}")

    c = conn.cursor()
    old_sources = c.execute(
        "SELECT url, domain, country FROM discovered_sources WHERE last_scraped < ? LIMIT 30",
        (datetime.now().strftime("%Y-%m-%d"),)
    ).fetchall()

    for url, domain, country in old_sources:
        print(f"\n→ {url[:70]}")
        saved = deep_scrape_url(conn, url, domain, country)
        total_saved += saved
        c.execute("UPDATE discovered_sources SET last_scraped=?, total_found=total_found+? WHERE url=?",
                  (datetime.now().strftime("%Y-%m-%d"), saved, url))
        conn.commit()
        time.sleep(random.uniform(2, 4))

    # Final summary
    c = conn.cursor()
    main_total = c.execute("SELECT COUNT(*) FROM scholarships").fetchone()[0]
    uni_total = c.execute("SELECT COUNT(*) FROM university_scholarships").fetchone()[0]
    sources_total = c.execute("SELECT COUNT(*) FROM discovered_sources").fetchone()[0]

    print(f"\n{'='*60}")
    print(f"  DISCOVERY COMPLETE")
    print(f"  New scholarships found  : {total_saved}")
    print(f"  Total in database       : {main_total}")
    print(f"  University table        : {uni_total}")
    print(f"  Sources discovered      : {sources_total}")
    print(f"{'='*60}")
    conn.close()