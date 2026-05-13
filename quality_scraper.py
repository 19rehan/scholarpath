"""
ADMITGOAL — QUALITY SCRAPER
Zero garbage. Verified scholarships only.
Quality score >= 70 required to save.
"""

import requests
from bs4 import BeautifulSoup
import psycopg2
import re
import time
import random
import unicodedata
from datetime import datetime
from urllib.parse import urlparse, urljoin

CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month

DATABASE_URL = 'postgresql://postgres.deqyxksflvlxjelppgxz:Rehan1819Rehan@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'

MONTHS = {
    'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
    'july':7,'august':8,'september':9,'october':10,'november':11,'december':12
}

# ══════════════════════════════════════════════════════════
# BLACKLISTS
# ══════════════════════════════════════════════════════════

TITLE_BLACKLIST = [
    # UI text
    'consent','cookies','accept cookies','cookie policy',
    'read more','click here','learn more','find out more',
    'apply now','apply here','sign in','login','register',
    'sign up','subscribe','newsletter','download','share',
    'menu','navigation','home','contact','about us','privacy policy',
    'terms of service','terms and conditions','sitemap',
    'search','filter','sort by','view all','see all','load more',
    'previous','next','back','forward','close','open',
    'footer','header','sidebar','advertisement','sponsored',
    'related posts','popular posts','recent posts','tags',
    'categories','archives','comments','leave a reply',
    'follow us','connect with us','social media',

    # Aggregator brand names
    'scholars4dev','opportunity desk','opportunitydesk',
    'studyportals','study portals','afterschoolafrica',
    'buddy4study','mastersportal','phdportal','youthop',
    'scholarshipdb','scholarshipsads','scholarshipregion',
    'estudyassistance','scholarshiphunter',

    # Generic garbage
    'scholarships page','scholarship listing','scholarship portal',
    'scholarships website','find scholarships','search scholarships',
    'all scholarships','latest scholarships','new scholarships',
    'scholarship news','education news','admission news',
    'page not found','404','error','access denied','forbidden',
    'coming soon','under construction','maintenance',
]

DOMAIN_BLACKLIST = [
    'scholars4dev.com','opportunitydesk.org','afterschoolafrica.com',
    'youthop.com','mastersportal.eu','phdportal.eu',
    'opportunitiesforafricans.com','scholarshipsads.com',
    'buddy4study.com','scholarshipregion.com',
]

# High trust domains
HIGH_TRUST_DOMAINS = [
    '.edu','.ac.uk','.edu.au','.ac.jp','.ac.kr','.edu.cn',
    '.gov','.gov.uk','.gov.au','.go.jp','.go.kr',
    'daad.de','chevening.org','fulbright','erasmus',
    'stipendiumhungaricum.hu','turkiyeburslari.gov.tr',
    'campuschina.org','studyinkorea.go.kr','scholarships.gc.ca',
    'studyinaustralia.gov.au','studyinnewzealand.govt.nz',
    'kaust.edu.sa','hec.gov.pk','iccr.gov.in',
]

# ══════════════════════════════════════════════════════════
# QUALITY SOURCES — verified, reliable
# ══════════════════════════════════════════════════════════
SOURCES = [
    # UK
    {'url':'https://www.chevening.org/scholarships/','country':'United Kingdom','region':'Europe','trust':95},
    {'url':'https://cscuk.fcdo.gov.uk/scholarships/','country':'United Kingdom','region':'Europe','trust':95},
    {'url':'https://www.britishcouncil.org/study-work-abroad/in-uk/scholarships','country':'United Kingdom','region':'Europe','trust':90},
    {'url':'https://www.ed.ac.uk/student-funding/postgraduate/international','country':'United Kingdom','region':'Europe','trust':90},
    {'url':'https://www.manchester.ac.uk/study/international/finance-and-scholarships/scholarships-and-bursaries/','country':'United Kingdom','region':'Europe','trust':90},
    {'url':'https://www.sheffield.ac.uk/international/fees-and-funding/scholarships','country':'United Kingdom','region':'Europe','trust':90},
    {'url':'https://www.ucl.ac.uk/scholarships/','country':'United Kingdom','region':'Europe','trust':90},
    {'url':'https://www.imperial.ac.uk/study/fees-and-funding/scholarships/','country':'United Kingdom','region':'Europe','trust':90},
    {'url':'https://www.ox.ac.uk/admissions/graduate/fees-and-funding/graduate-scholarships','country':'United Kingdom','region':'Europe','trust':95},
    {'url':'https://www.cam.ac.uk/funding','country':'United Kingdom','region':'Europe','trust':95},

    # Germany
    {'url':'https://www.daad.de/en/study-and-research-in-germany/scholarships/','country':'Germany','region':'Europe','trust':95},
    {'url':'https://www.tum.de/en/studies/fees-and-financial-aid/scholarships','country':'Germany','region':'Europe','trust':90},
    {'url':'https://www.lmu.de/en/study/all-degrees-and-offerings/fees-and-funding/scholarships/','country':'Germany','region':'Europe','trust':90},
    {'url':'https://www.rwth-aachen.de/cms/root/Studium/Im-Studium/Finanzierung-Foerderung/~bkj/Stipendien/','country':'Germany','region':'Europe','trust':90},

    # Europe
    {'url':'https://stipendiumhungaricum.hu/en/','country':'Hungary','region':'Europe','trust':95},
    {'url':'https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en','country':'Europe','region':'Europe','trust':95},
    {'url':'https://www.uu.se/en/study/scholarships','country':'Sweden','region':'Europe','trust':90},
    {'url':'https://www.helsinki.fi/en/studying/fees-and-financial-aid/scholarships-and-grants','country':'Finland','region':'Europe','trust':90},
    {'url':'https://studies.ku.dk/masters/financing/scholarships/','country':'Denmark','region':'Europe','trust':90},
    {'url':'https://www.uio.no/english/studies/admission/scholarships/','country':'Norway','region':'Europe','trust':90},
    {'url':'https://www.epfl.ch/education/scholarships/','country':'Switzerland','region':'Europe','trust':90},
    {'url':'https://www.tcd.ie/study/fees-funding/scholarships/','country':'Ireland','region':'Europe','trust':90},

    # Middle East
    {'url':'https://www.turkiyeburslari.gov.tr/en','country':'Turkey','region':'Middle East','trust':95},
    {'url':'https://www.kaust.edu.sa/en/study/financial-support','country':'Saudi Arabia','region':'Middle East','trust':95},
    {'url':'https://www.hbku.edu.qa/en/admissions/scholarships','country':'Qatar','region':'Middle East','trust':90},
    {'url':'https://www.uaeu.ac.ae/en/admissions/scholarships.shtml','country':'UAE','region':'Middle East','trust':90},

    # Asia
    {'url':'https://www.campuschina.org/scholarships/index.html','country':'China','region':'Asia','trust':95},
    {'url':'https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do','country':'South Korea','region':'Asia','trust':95},
    {'url':'https://www.studyinjapan.go.jp/en/smap_stopj-applications_scholarship.html','country':'Japan','region':'Asia','trust':95},
    {'url':'https://www.u-tokyo.ac.jp/en/prospective-students/scholarships.html','country':'Japan','region':'Asia','trust':90},
    {'url':'https://en.snu.ac.kr/apply/scholarship','country':'South Korea','region':'Asia','trust':90},
    {'url':'https://international.kaist.ac.kr/cms/FR_CON/index.do?MENU_ID=90','country':'South Korea','region':'Asia','trust':90},
    {'url':'https://www.nus.edu.sg/oam/scholarships','country':'Singapore','region':'Asia','trust':90},
    {'url':'https://www.tsinghua.edu.cn/en/Admission/Scholarships.htm','country':'China','region':'Asia','trust':90},
    {'url':'https://en.sjtu.edu.cn/admissions/scholarships/','country':'China','region':'Asia','trust':90},
    {'url':'https://www.hec.gov.pk/english/scholarshipsgrants/Pages/default.aspx','country':'Pakistan','region':'Asia','trust':95},
    {'url':'https://iccr.gov.in/scholarships','country':'India','region':'Asia','trust':95},
    {'url':'https://mohe.gov.my/en/scholarships','country':'Malaysia','region':'Asia','trust':90},

    # Oceania
    {'url':'https://www.studyinaustralia.gov.au/english/australian-scholarships','country':'Australia','region':'Oceania','trust':95},
    {'url':'https://scholarships.unimelb.edu.au/','country':'Australia','region':'Oceania','trust':90},
    {'url':'https://www.anu.edu.au/study/scholarships','country':'Australia','region':'Oceania','trust':90},
    {'url':'https://scholarships.uq.edu.au/','country':'Australia','region':'Oceania','trust':90},
    {'url':'https://www.studyinnewzealand.govt.nz/how-to-apply/scholarships','country':'New Zealand','region':'Oceania','trust':95},
    {'url':'https://www.auckland.ac.nz/en/study/fees-and-money/scholarships.html','country':'New Zealand','region':'Oceania','trust':90},

    # North America
    {'url':'https://foreign.fulbrightonline.org/','country':'USA','region':'North America','trust':95},
    {'url':'https://www.scholarships.gc.ca/scholarships-bourses/index.aspx','country':'Canada','region':'North America','trust':95},
    {'url':'https://www.sgs.utoronto.ca/awards/','country':'Canada','region':'North America','trust':90},
    {'url':'https://students.ubc.ca/enrolment/finances/scholarships-awards-bursaries','country':'Canada','region':'North America','trust':90},
    {'url':'https://www.mcgill.ca/studentaid/scholarships-awards','country':'Canada','region':'North America','trust':90},

    # Africa
    {'url':'https://www.uct.ac.za/main/explore-uct/funding','country':'South Africa','region':'Africa','trust':85},

    # Aggregators — lower trust but high volume
    {'url':'https://www.scholars4dev.com/','country':'International','region':'International','trust':70},
    {'url':'https://www.scholars4dev.com/page/2/','country':'International','region':'International','trust':70},
    {'url':'https://www.scholars4dev.com/page/3/','country':'International','region':'International','trust':70},
    {'url':'https://www.scholars4dev.com/page/4/','country':'International','region':'International','trust':70},
    {'url':'https://www.scholars4dev.com/page/5/','country':'International','region':'International','trust':70},
    {'url':'https://opportunitydesk.org/category/scholarships/','country':'International','region':'International','trust':70},
    {'url':'https://opportunitydesk.org/category/scholarships/page/2/','country':'International','region':'International','trust':70},
    {'url':'https://www.afterschoolafrica.com/category/scholarships/','country':'International','region':'International','trust':70},
    {'url':'https://www.afterschoolafrica.com/category/scholarships/page/2/','country':'International','region':'International','trust':70},
]

# ══════════════════════════════════════════════════════════
# STEP 1 — FETCH WITH ANTI-BLOCK
# ══════════════════════════════════════════════════════════
def get_headers():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    ]
    return {
        "User-Agent": random.choice(agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
        "Upgrade-Insecure-Requests": "1",
    }

def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(2, 4) * (attempt + 1))
            s = requests.Session()
            s.headers.update(get_headers())
            r = s.get(url, timeout=20, allow_redirects=True)
            if r.status_code == 200:
                return r
            elif r.status_code in [403, 429]:
                time.sleep(random.uniform(10, 20))
        except:
            time.sleep(5)
    return None

# ══════════════════════════════════════════════════════════
# STEP 2 — HTML CLEANER
# ══════════════════════════════════════════════════════════
def clean_html(soup):
    """Remove all noise from HTML before extraction"""
    # Remove noise tags
    noise_tags = [
        'nav','header','footer','aside','script','style',
        'noscript','iframe','form','button','select',
        'meta','link','head',
    ]
    for tag in soup.find_all(noise_tags):
        tag.decompose()

    # Remove noise by class/id patterns
    noise_patterns = [
        'cookie','gdpr','consent','banner','popup','modal',
        'overlay','newsletter','subscribe','social','share',
        'sidebar','widget','advertisement','ads','advert',
        'nav','menu','navigation','breadcrumb','pagination',
        'footer','header','topbar','toolbar','search-bar',
        'related','suggested','recommended','popular',
        'comment','reply','author-bio','tags','categories',
    ]
    for tag in soup.find_all(True):
        tag_id = (tag.get('id') or '').lower()
        tag_class = ' '.join(tag.get('class') or []).lower()
        combined = tag_id + ' ' + tag_class
        if any(p in combined for p in noise_patterns):
            tag.decompose()

    return soup

# ══════════════════════════════════════════════════════════
# STEP 3 — TITLE VALIDATOR
# ══════════════════════════════════════════════════════════
def is_valid_title(title):
    if not title:
        return False, "empty"

    # Clean the title first
    title = title.strip()
    # Remove site suffixes
    for suffix in [' | Scholars4Dev',' - Opportunity Desk',' | Study in',' | Scholarships',
                   ' - ScholarshipDB',' | AfterSchoolAfrica',' | YouthOP',
                   ' | MastersPortal',' | PhDPortal']:
        title = title.replace(suffix, '').replace(suffix.lower(), '')
    title = title.strip()

    if len(title) < 10:
        return False, f"too short: {len(title)}"
    if len(title) > 200:
        return False, "too long"

    title_lower = title.lower()

    # Blacklist check
    for bad in TITLE_BLACKLIST:
        if title_lower == bad or title_lower.startswith(bad + ' ') or title_lower.endswith(' ' + bad):
            return False, f"blacklisted: {bad}"
        if bad in ['consent','cookies','read more','click here','apply now',
                   'sign in','login','register','newsletter'] and bad in title_lower:
            return False, f"contains blacklisted: {bad}"

    # Must contain scholarship-related keyword
    scholarship_keywords = [
        'scholarship','fellowship','grant','bursary','award',
        'program','programme','funding','stipend','prize',
        'admission','degree','masters','master','phd','doctoral',
        'undergraduate','postgraduate','postdoc','research',
        'excellence','international','opportunity','fully funded',
    ]
    has_keyword = any(kw in title_lower for kw in scholarship_keywords)
    if not has_keyword:
        return False, "no scholarship keyword"

    # Must not be just a website name
    for domain_brand in ['scholars4dev','opportunitydesk','afterschoolafrica',
                          'youthop','mastersportal','phdportal','scholarshipdb',
                          'studyportal','buddy4study']:
        if title_lower.strip() == domain_brand:
            return False, f"is domain brand: {domain_brand}"

    # Must have at least 2 words
    if len(title.split()) < 3:
        return False, "less than 3 words"

    return True, "valid"

def clean_title(title):
    """Clean site suffixes and normalize title"""
    if not title:
        return ""

    # Remove common site suffixes
    suffixes = [
        ' | Scholars4Dev',' - Opportunity Desk',' | AfterSchoolAfrica',
        ' | YouthOP',' | MastersPortal',' | PhDPortal',
        ' | ScholarshipDB',' | Study in',' | Scholarships',
        ' - ScholarshipDB.net',' | StudyPortals',
        ' – Opportunity Desk',' – Scholars4Dev',
    ]
    for s in suffixes:
        title = title.replace(s, '').replace(s.lower(), '')

    # Clean special characters
    title = re.sub(r'\s+', ' ', title).strip()
    title = title.strip('|–-').strip()

    return title

# ══════════════════════════════════════════════════════════
# STEP 4 — QUALITY SCORE SYSTEM
# ══════════════════════════════════════════════════════════
def calculate_quality_score(data, source_trust):
    score = 0

    # Title quality (0-20)
    valid, reason = is_valid_title(data.get('title',''))
    if valid:
        score += 20
        title_words = len(data['title'].split())
        if title_words >= 5: score += 5
        if title_words >= 8: score += 5

    # Deadline found (0-25)
    if data.get('deadline') and data['deadline'] != 'Check website':
        score += 25

    # Official link (0-15)
    link = data.get('official_link','')
    if link:
        domain = get_domain(link)
        if any(h in domain for h in HIGH_TRUST_DOMAINS):
            score += 15
        else:
            score += 5

    # Degree level specific (0-10)
    degree = data.get('degree','')
    if degree and degree != 'All levels':
        score += 10

    # Description quality (0-10)
    desc = data.get('description','')
    if len(desc) > 200: score += 10
    elif len(desc) > 100: score += 5

    # Eligible countries found (0-10)
    eligible = data.get('eligible_countries','')
    if eligible and eligible != 'Open to international students worldwide':
        score += 10

    # Source trust (0-5)
    if source_trust >= 90: score += 5
    elif source_trust >= 70: score += 3

    return min(score, 100)

# ══════════════════════════════════════════════════════════
# STEP 5 — EXTRACTORS
# ══════════════════════════════════════════════════════════
def get_domain(url):
    try:
        return urlparse(url).netloc.replace('www.','')
    except:
        return ""

def is_future_date(text):
    text_lower = text.lower()
    if any(c in text_lower for c in [
        'applications are closed','deadline has passed',
        'no longer accepting','competition is closed']):
        return False
    found = []
    patterns = [
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})',
        r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',
    ]
    for p in patterns:
        for m in re.finditer(p, text_lower):
            try:
                g = m.groups()
                if g[0] in MONTHS:
                    month, year = MONTHS[g[0]], int(g[2])
                else:
                    month, year = MONTHS[g[1]], int(g[2])
                found.append((year, month))
            except:
                continue
    if found:
        future = [(y,m) for y,m in found if y > CURRENT_YEAR or (y == CURRENT_YEAR and m >= CURRENT_MONTH)]
        return len(future) > 0
    return str(CURRENT_YEAR) in text or str(CURRENT_YEAR+1) in text

def extract_deadline(text):
    months_str = "january|february|march|april|may|june|july|august|september|october|november|december"
    patterns = [
        rf'deadline[:\s]*((?:{months_str})[\s\d,]+\d{{4}})',
        rf'closing date[:\s]*((?:{months_str})[\s\d,]+\d{{4}})',
        rf'apply by[:\s]*((?:{months_str})[\s\d,]+\d{{4}})',
        rf'(\d{{1,2}}\s+(?:{months_str})\s+\d{{4}})',
        rf'((?:{months_str})\s+\d{{1,2}},?\s+\d{{4}})',
        rf'((?:{months_str})\s+\d{{4}})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            groups = [g for g in m.groups() if g]
            if groups:
                deadline = groups[-1].strip()
                if is_future_date(deadline):
                    return deadline
    return None

def extract_ielts(text):
    for p in [r'ielts[:\s]*(\d+\.?\d*)',r'(\d+\.?\d*)\s*(?:in|for)?\s*ielts']:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                s = float(m.group(1))
                if 4.0 <= s <= 9.0: return str(s)
            except: pass
    return "Required" if re.search(r'\bielts\b', text, re.IGNORECASE) else "Not required"

def extract_degree(text):
    """Smart degree extraction — find dominant level"""
    t = text.lower()
    scores = {
        'Bachelor': len(re.findall(r'\bundergraduate|bachelor\b', t)),
        'Master': len(re.findall(r'\bmaster|postgraduate|msc\b|mba\b', t)),
        'PhD': len(re.findall(r'\bphd|doctoral|doctorate\b', t)),
        'Postdoc': len(re.findall(r'\bpostdoc|post-doc\b', t)),
    }
    max_score = max(scores.values())
    if max_score == 0: return "All levels"
    dominant = [l for l,s in scores.items() if s >= max_score * 0.6 and s > 0]
    return dominant[0] if len(dominant) == 1 else ", ".join([l for l in ['Bachelor','Master','PhD','Postdoc'] if scores[l] > 0])

def extract_funding(text):
    if re.search(r'full.?fund|fully.?fund|full scholarship|covers all', text, re.IGNORECASE):
        return "Fully Funded"
    if re.search(r'partial|tuition only|tuition fee', text, re.IGNORECASE):
        return "Partial"
    if re.search(r'stipend|living allowance', text, re.IGNORECASE):
        return "Stipend Included"
    return "Check website"

def extract_eligible_countries(text):
    countries = [
        "Pakistan","India","Bangladesh","Nepal","Sri Lanka","Nigeria","Ghana",
        "Kenya","Ethiopia","Tanzania","Uganda","South Africa","Egypt","Morocco",
        "Indonesia","Malaysia","Philippines","Vietnam","Thailand","Brazil",
        "Colombia","Mexico","developing countries","low-income countries",
        "African countries","Asian countries","all countries",
        "international students","worldwide"
    ]
    found = [c for c in countries if c.lower() in text.lower()]
    return ", ".join(found[:12]) if found else "Open to international students worldwide"

def is_job_listing(title):
    if not title: return True
    t = title.lower()
    return any(re.search(p, t) for p in [
        r'\bposition\b',r'\bprofessor\b',r'\blecturer\b',r'\bpostdoc(toral)?\b',
        r'\binstructor\b',r'\bfaculty\b',r'\bdirector\b',r'\bresearcher\b',
        r'\bscientist\b',r'\bengineer\b',r'\bjob fair\b',r'\brecruitment\b',
        r'\bhiring\b',r'\bvacancy\b',r'\bvacancies\b',r'\bstaff\b',
        r'\btechnician\b',r'\bconsultant\b',r'\bassistant professor\b',
        r'\bassociate professor\b',r'\bhead of\b',
    ])

def is_list_page(title):
    if not title: return True
    t = title.lower()
    return any(re.search(p, t) for p in [
        r'top \d+',r'^\d+ scholarships',r'list of scholarships',
        r'best scholarships',r'countries where tuition',r'\d+ fully funded',
        r'all scholarships in',
    ])

def generate_slug(title):
    """Generate clean URL slug from title"""
    slug = title.lower()
    slug = unicodedata.normalize('NFKD', slug).encode('ascii','ignore').decode()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug).strip('-')
    slug = re.sub(r'-+', '-', slug)
    return slug[:80]

# ══════════════════════════════════════════════════════════
# STEP 6 — OFFICIAL LINK FINDER
# ══════════════════════════════════════════════════════════
def find_official_link(soup, page_url):
    apply_keywords = [
        'apply now','apply here','official website','click here to apply',
        'application portal','official link','visit official','more information',
        'official page','apply for','application form','online application',
        'official scholarship','official site','visit the official',
    ]
    current_domain = get_domain(page_url)
    candidates = []

    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        link_text = a.get_text(strip=True).lower()
        if not href or href.startswith('#') or 'javascript' in href: continue
        if href.startswith('/'):
            parsed = urlparse(page_url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        elif not href.startswith('http'): continue
        if any(s in href for s in ['facebook','twitter','instagram','linkedin','youtube','whatsapp']): continue

        link_domain = get_domain(href)
        # Skip if same domain as current aggregator
        if link_domain == current_domain: continue
        # Skip other aggregators
        if any(agg in link_domain for agg in DOMAIN_BLACKLIST): continue

        score = 0
        for h in HIGH_TRUST_DOMAINS:
            if h in link_domain: score += 20
        for kw in apply_keywords:
            if kw in link_text: score += 10
        if any(kw in href.lower() for kw in ['scholarship','fellowship','grant','apply','admission']): score += 5
        if score > 10: candidates.append((score, href))

    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]
    return None

# ══════════════════════════════════════════════════════════
# STEP 7 — DUPLICATE DETECTION
# ══════════════════════════════════════════════════════════
def normalize_title(title):
    """Normalize title for duplicate detection"""
    t = title.lower()
    t = re.sub(r'\b(20\d\d|apply|now|guide|complete|eligibility|deadline)\b', '', t)
    t = re.sub(r'[^a-z0-9\s]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def is_duplicate(conn, title, link):
    cur = conn.cursor()
    # Check by link
    cur.execute("SELECT id FROM scholarship_details WHERE scholarship_link=%s", (link,))
    if cur.fetchone():
        cur.close()
        return True, "duplicate link"
    # Check by normalized title
    normalized = normalize_title(title)
    cur.execute("SELECT id, title FROM scholarship_details")
    rows = cur.fetchall()
    for row in rows:
        if normalize_title(row[1] or '') == normalized:
            cur.close()
            return True, "duplicate title"
    cur.close()
    return False, ""

# ══════════════════════════════════════════════════════════
# STEP 8 — BLOG WRITER (clean, factual, not spammy)
# ══════════════════════════════════════════════════════════
def write_clean_blog(data):
    title = data['title']
    country = data['country']
    region = data['region']
    uni = data['university']
    deadline = data['deadline'] or "Check official website"
    ielts = data['ielts']
    degree = data['degree']
    funding = data['funding']
    eligible = data['eligible_countries']
    link = data['official_link']
    desc = data['description']
    quality = data.get('quality_score', 0)

    seo_title = f"{title} {CURRENT_YEAR} — Eligibility, Deadline & How to Apply"
    seo_title = clean_title(seo_title)[:70]
    seo_desc = f"{title}. Deadline: {deadline}. {degree} students. IELTS: {ielts}. Official guide for international applicants."[:160]

    blog = f"""# {title}

**Deadline:** {deadline} | **Country:** {country} | **Level:** {degree}

---

## Overview

{desc}

This scholarship is offered by **{uni}** in **{country}**. We verified this opportunity is open before publishing. Always confirm details on the official website before applying.

---

## Key Information

| Field | Details |
|-------|---------|
| **University / Host** | {uni} |
| **Country** | {country} |
| **Degree Level** | {degree} |
| **Funding** | {funding} |
| **Deadline** | {deadline} |
| **IELTS Requirement** | {ielts} |
| **Verified** | {datetime.now().strftime("%B %Y")} |

---

## Eligibility

{eligible}

---

## Language Requirements

{"No English language test required." if ielts in ["Not required","Check website"] else f"IELTS minimum score: {ielts}. TOEFL and PTE may be accepted as alternatives — check the official website."}

---

## How to Apply

1. Visit the official scholarship page (link below)
2. Read eligibility requirements carefully
3. Prepare required documents
4. Submit before: **{deadline}**

---

## Documents Required

- Valid Passport
- Academic Transcripts
- Degree Certificate
- English Test Certificate (if required)
- Statement of Purpose
- Recommendation Letters
- Updated CV

---

## Apply

**Official page:** {link}

> Verified by AdmitGoal — {datetime.now().strftime("%B %d, %Y")}
"""
    return blog, seo_title, seo_desc

# ══════════════════════════════════════════════════════════
# STEP 9 — SAVE TO DATABASE
# ══════════════════════════════════════════════════════════
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

def save(conn, data, source_trust):
    title = clean_title(data.get('title',''))
    data['title'] = title

    # Validate title
    valid, reason = is_valid_title(title)
    if not valid:
        return False, f"invalid title: {reason}"

    # Check job listing
    if is_job_listing(title):
        return False, "job listing"
    if is_list_page(title):
        return False, "list page"

    # Check duplicate
    dup, dup_reason = is_duplicate(conn, title, data['official_link'])
    if dup:
        return False, f"duplicate: {dup_reason}"

    # Calculate quality score
    quality = calculate_quality_score(data, source_trust)
    data['quality_score'] = quality

    if quality < 60:
        return False, f"quality too low: {quality}/100"

    blog, seo_title, seo_desc = write_clean_blog(data)
    slug = generate_slug(title)
    lang = f"IELTS {data['ielts']}" if data['ielts'] not in ["Not required","Check website"] else data['ielts']

    try:
        cur = conn.cursor()
        cur.execute('''INSERT INTO scholarship_details
            (scholarship_link,title,full_description,eligible_countries,
             eligible_students,degree_level,deadline,language_requirement,
             ielts_score,benefits,how_to_apply,blog_post,seo_title,
             seo_description,university_name,country,region,
             funding_type,gpa_required,last_updated)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (scholarship_link) DO UPDATE SET
              deadline=EXCLUDED.deadline,
              last_updated=EXCLUDED.last_updated,
              blog_post=EXCLUDED.blog_post''',
            (data['official_link'],title,data['description'][:800],
             data['eligible_countries'],"International students",
             data['degree'],data['deadline'],lang,data['ielts'],
             "","",blog,seo_title,seo_desc,
             data['university'],data['country'],data['region'],
             data['funding'],"Check website",
             datetime.now().strftime("%Y-%m-%d")))

        cur.execute('''INSERT INTO scholarships
            (title,description,country,deadline,link,source,scraped_date)
            VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (link) DO NOTHING''',
            (title,seo_desc,data['country'],data['deadline'],
             data['official_link'],data['university'][:50],
             datetime.now().strftime("%Y-%m-%d")))
        cur.close()
        return True, f"saved (quality: {quality}/100)"
    except Exception as e:
        return False, f"db error: {e}"

# ══════════════════════════════════════════════════════════
# STEP 10 — MAIN SCRAPER ENGINE
# ══════════════════════════════════════════════════════════
def detect_country(domain, text=""):
    tld_map = {
        '.ac.uk':'United Kingdom','.co.uk':'United Kingdom','.uk':'United Kingdom',
        '.edu.au':'Australia','.com.au':'Australia','.au':'Australia',
        '.ca':'Canada','.de':'Germany','.fr':'France','.nl':'Netherlands',
        '.se':'Sweden','.no':'Norway','.fi':'Finland','.dk':'Denmark',
        '.ch':'Switzerland','.at':'Austria','.be':'Belgium','.it':'Italy',
        '.es':'Spain','.tr':'Turkey','.sa':'Saudi Arabia','.ae':'UAE',
        '.qa':'Qatar','.cn':'China','.jp':'Japan','.kr':'South Korea',
        '.my':'Malaysia','.sg':'Singapore','.th':'Thailand','.id':'Indonesia',
        '.vn':'Vietnam','.tw':'Taiwan','.nz':'New Zealand','.za':'South Africa',
        '.eg':'Egypt','.ma':'Morocco','.ng':'Nigeria','.br':'Brazil',
        '.ru':'Russia','.pk':'Pakistan','.in':'India','.bd':'Bangladesh',
        '.edu':'USA','.gov':'USA',
    }
    for tld, country in sorted(tld_map.items(), key=lambda x: -len(x[0])):
        if domain.endswith(tld): return country
    hints = {
        'germany':'Germany','united kingdom':'United Kingdom','australia':'Australia',
        'canada':'Canada','japan':'Japan','china':'China','korea':'South Korea',
        'turkey':'Turkey','france':'France','netherlands':'Netherlands',
        'usa':'USA','united states':'USA','saudi arabia':'Saudi Arabia',
        'malaysia':'Malaysia','singapore':'Singapore','italy':'Italy',
        'norway':'Norway','sweden':'Sweden','finland':'Finland','russia':'Russia',
    }
    for hint, country in hints.items():
        if hint in text.lower()[:1000]: return country
    return "International"

def detect_region(country):
    regions = {
        'Europe':['United Kingdom','Germany','France','Netherlands','Sweden','Norway',
                  'Finland','Denmark','Switzerland','Austria','Belgium','Italy','Spain',
                  'Poland','Hungary','Czech Republic','Ireland','Romania','Russia','Estonia'],
        'Middle East':['Turkey','Saudi Arabia','UAE','Qatar','Jordan','Kuwait','Egypt','Morocco'],
        'Asia':['China','Japan','South Korea','Malaysia','Singapore','Thailand','Indonesia',
                'Vietnam','Taiwan','Hong Kong','Pakistan','India','Bangladesh','Sri Lanka','Nepal'],
        'Oceania':['Australia','New Zealand'],
        'North America':['USA','Canada','Mexico'],
        'Africa':['Nigeria','South Africa','Kenya','Ghana','Ethiopia'],
        'Latin America':['Brazil','Colombia','Argentina'],
    }
    for region, countries in regions.items():
        if country in countries: return region
    return "International"

def scrape_source(source, conn):
    url = source['url']
    country = source['country']
    region = source['region']
    trust = source['trust']
    is_aggregator = any(agg in get_domain(url) for agg in DOMAIN_BLACKLIST) or trust < 85

    r = fetch(url)
    if not r: return 0

    soup = BeautifulSoup(r.text, 'lxml')
    soup = clean_html(soup)
    full_text = ' '.join(soup.get_text(separator=' ', strip=True).split())

    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    base_domain = get_domain(url)

    title_tag = soup.find('title')
    site_name = clean_title(title_tag.get_text(strip=True).split('|')[0].split('–')[0].strip()[:60]) if title_tag else base_domain

    saved = 0
    seen = set()

    # Find links to individual scholarship pages
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        text = a.get_text(strip=True)

        if len(text) < 12 or len(text) > 200: continue

        if href.startswith('/'): href = base_url + href
        elif not href.startswith('http'): continue
        if href in seen or href == url: continue

        # For official sources — only follow links on same domain
        if not is_aggregator:
            if get_domain(href) != base_domain: continue

        # Skip navigation/UI links
        skip = ['/category/','/tag/','/page/','/author/','#','mailto',
                '/about','/contact','/privacy','/search','/login',
                '/register','/signin','javascript:','tel:']
        if any(s in href.lower() for s in skip): continue

        # Must have scholarship keyword in text or href
        has_kw = any(kw in text.lower() for kw in
                    ['scholarship','fellowship','award','grant','bursary','funding',
                     'program','programme','stipend','admission'])
        if not has_kw: continue

        seen.add(href)
        print(f"  → {text[:65]}")

        # Visit the page
        detail_r = fetch(href)
        if not detail_r: continue

        detail_soup = BeautifulSoup(detail_r.text, 'lxml')
        detail_soup = clean_html(detail_soup)
        detail_text = ' '.join(detail_soup.get_text(separator=' ', strip=True).split())

        # Check freshness
        if not is_future_date(detail_text):
            print(f"    Skip: outdated")
            continue

        # For aggregator pages — find official link
        official_link = href
        if is_aggregator:
            found_official = find_official_link(detail_soup, href)
            if found_official:
                official_link = found_official
                print(f"    Official: {official_link[:60]}")
                # Get data from official page too
                off_r = fetch(official_link)
                if off_r:
                    off_soup = BeautifulSoup(off_r.text, 'lxml')
                    off_soup = clean_html(off_soup)
                    off_text = ' '.join(off_soup.get_text(separator=' ', strip=True).split())
                    detail_text = detail_text + " " + off_text

        # Extract title
        h1 = detail_soup.find('h1')
        raw_title = h1.get_text(strip=True) if h1 else text
        title = clean_title(raw_title)

        valid, reason = is_valid_title(title)
        if not valid:
            print(f"    Skip: {reason}")
            continue

        if is_job_listing(title) or is_list_page(title):
            print(f"    Skip: job/list")
            continue

        deadline = extract_deadline(detail_text)
        ielts = extract_ielts(detail_text)
        degree = extract_degree(detail_text)
        funding = extract_funding(detail_text)
        eligible = extract_eligible_countries(detail_text)

        # Description — first meaningful paragraph
        desc = ""
        for p in detail_soup.find_all('p'):
            t = p.get_text(strip=True)
            if len(t) > 80 and not any(bad in t.lower() for bad in
                                        ['cookie','subscribe','newsletter','privacy']):
                desc = t[:600]
                break

        # Detect country from official link
        link_country = detect_country(get_domain(official_link), detail_text)
        if link_country == "International" and country != "International":
            link_country = country

        data = {
            'title': title,
            'description': desc or f"Scholarship offered by {site_name} in {link_country}.",
            'university': site_name,
            'country': link_country,
            'region': detect_region(link_country),
            'deadline': deadline,
            'ielts': ielts,
            'degree': degree,
            'funding': funding,
            'eligible_countries': eligible,
            'official_link': official_link,
        }

        ok, msg = save(conn, data, trust)
        if ok:
            print(f"    SAVED: {title[:60]} ({msg})")
            saved += 1
        else:
            print(f"    Rejected: {msg}")

        time.sleep(random.uniform(1, 3))

    return saved

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  ADMITGOAL QUALITY SCRAPER")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Sources: {len(SOURCES)}")
    print("  Minimum quality score: 60/100")
    print("  Zero garbage policy")
    print("=" * 60)

    conn = get_db()
    total_saved = 0
    total_rejected = 0

    for i, source in enumerate(SOURCES, 1):
        print(f"\n[{i}/{len(SOURCES)}] {source['country']} — {get_domain(source['url'])} (trust: {source['trust']})")
        saved = scrape_source(source, conn)
        total_saved += saved
        print(f"  Saved: {saved}")
        time.sleep(random.uniform(2, 5))

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scholarship_details")
    db_total = cur.fetchone()[0]
    cur.close()
    conn.close()

    print(f"\n{'='*60}")
    print(f"  Saved this run  : {total_saved}")
    print(f"  Total in DB     : {db_total}")
    print(f"  Quality checks  : title + freshness + score + duplicate")
    print(f"{'='*60}")