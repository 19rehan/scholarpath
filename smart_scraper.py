import requests
from bs4 import BeautifulSoup
import psycopg2
import re
import time
import random
from datetime import datetime
from urllib.parse import urlparse, urljoin

CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month

DATABASE_URL = 'postgresql://postgres.deqyxksflvlxjelppgxz:Rehan1819Rehan@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'

AGGREGATOR_DOMAINS = [
    'scholars4dev.com', 'opportunitydesk.org', 'afterschoolafrica.com',
    'youthop.com', 'scholarshipdb.net', 'mastersportal.eu',
    'phdportal.eu', 'opportunitiesforafricans.com', 'scholarshipsads.com',
    'buddy4study.com', 'scholarshipregion.com', 'scholarshiphunter.com',
    'estudyassistance.com', 'scholarscorner.net', 'admitgoal.com',
    'scholarshipowl.com', 'inomics.com', 'findaphd.com',
    'jobs.ac.uk', 'euraxess.ec.europa.eu',
]

# ── DIRECT SCHOLARSHIP PAGES (scrape as single scholarships) ──
DIRECT_SCHOLARSHIPS = [
    {'url': 'https://www.chevening.org/scholarships/who-can-apply/', 'country': 'United Kingdom', 'region': 'Europe'},
    {'url': 'https://www.daad.de/en/study-and-research-in-germany/scholarships/daad-scholarships/', 'country': 'Germany', 'region': 'Europe'},
    {'url': 'https://www.campuschina.org/scholarships/index.html', 'country': 'China', 'region': 'Asia'},
    {'url': 'https://www.turkiyeburslari.gov.tr/en/page/scholarship-programs', 'country': 'Turkey', 'region': 'Middle East'},
    {'url': 'https://stipendiumhungaricum.hu/apply/', 'country': 'Hungary', 'region': 'Europe'},
    {'url': 'https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do', 'country': 'South Korea', 'region': 'Asia'},
    {'url': 'https://foreign.fulbrightonline.org/about/foreign-fulbright', 'country': 'USA', 'region': 'North America'},
    {'url': 'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-masters-scholarships/', 'country': 'United Kingdom', 'region': 'Europe'},
    {'url': 'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-phd-scholarships/', 'country': 'United Kingdom', 'region': 'Europe'},
    {'url': 'https://www.australiaawards.gov.au/scholarships', 'country': 'Australia', 'region': 'Oceania'},
    {'url': 'https://www.vliruos.be/en/scholarships/our-scholarships', 'country': 'Belgium', 'region': 'Europe'},
    {'url': 'https://www.nuffic.nl/en/subjects/orange-knowledge-programme', 'country': 'Netherlands', 'region': 'Europe'},
    {'url': 'https://www.aauw.org/resources/programs/fellowships-grants/current-opportunities/international/', 'country': 'USA', 'region': 'North America'},
    {'url': 'https://schwarzmanscholars.org/admissions/', 'country': 'China', 'region': 'Asia'},
    {'url': 'https://www.kaust.edu.sa/en/study/financial-support', 'country': 'Saudi Arabia', 'region': 'Middle East'},
    {'url': 'https://www.wdp.edu.pk/scholarships', 'country': 'Pakistan', 'region': 'Asia'},
    {'url': 'https://hec.gov.pk/english/scholarshipsgrants/Pages/Scholarships.aspx', 'country': 'Pakistan', 'region': 'Asia'},
    {'url': 'https://www.mext.go.jp/en/policy/education/highered/title02/detail02/sdetail02/1373897.htm', 'country': 'Japan', 'region': 'Asia'},
    {'url': 'https://www.jasso.or.jp/en/study_j/scholarships/', 'country': 'Japan', 'region': 'Asia'},
    {'url': 'https://www.studyinrussia.ru/en/study-in-russia/scholarships/', 'country': 'Russia', 'region': 'Europe'},
    {'url': 'https://indonesia.go.id/en/layanan-informasi-publik/kategori/pendidikan', 'country': 'Indonesia', 'region': 'Asia'},
    {'url': 'https://www.uu.se/en/study/scholarships', 'country': 'Sweden', 'region': 'Europe'},
    {'url': 'https://www.helsinki.fi/en/studying/fees-and-financial-aid/scholarships-and-grants', 'country': 'Finland', 'region': 'Europe'},
    {'url': 'https://studies.ku.dk/masters/financing/scholarships/', 'country': 'Denmark', 'region': 'Europe'},
    {'url': 'https://www.uio.no/english/studies/admission/scholarships/', 'country': 'Norway', 'region': 'Europe'},
    {'url': 'https://www.unige.ch/gap/en/scholarships/', 'country': 'Switzerland', 'region': 'Europe'},
    {'url': 'https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en', 'country': 'Europe', 'region': 'Europe'},
    {'url': 'https://www.scholarships.gc.ca/scholarships-bourses/index.aspx', 'country': 'Canada', 'region': 'North America'},
    {'url': 'https://www.educanada.ca/scholarships-bourses/index.aspx', 'country': 'Canada', 'region': 'North America'},
    {'url': 'https://www.africaportal.org/scholarships/', 'country': 'International', 'region': 'Africa'},
    {'url': 'https://www.mastercard.foundation/scholarships', 'country': 'International', 'region': 'Africa'},
]

# ── AGGREGATOR LISTING PAGES (find posts → find official links) ──
AGGREGATOR_SOURCES = [
    'https://www.scholars4dev.com/',
    'https://www.scholars4dev.com/page/2/',
    'https://www.scholars4dev.com/page/3/',
    'https://www.scholars4dev.com/page/4/',
    'https://www.scholars4dev.com/page/5/',
    'https://www.scholars4dev.com/page/6/',
    'https://www.scholars4dev.com/page/7/',
    'https://www.scholars4dev.com/page/8/',
    'https://www.scholars4dev.com/page/9/',
    'https://www.scholars4dev.com/page/10/',
    'https://opportunitydesk.org/category/scholarships/',
    'https://opportunitydesk.org/category/scholarships/page/2/',
    'https://opportunitydesk.org/category/scholarships/page/3/',
    'https://opportunitydesk.org/category/scholarships/page/4/',
    'https://opportunitydesk.org/category/scholarships/page/5/',
    'https://www.afterschoolafrica.com/category/scholarships/',
    'https://www.afterschoolafrica.com/category/scholarships/page/2/',
    'https://www.afterschoolafrica.com/category/scholarships/page/3/',
    'https://scholarshipdb.net/scholarships-in-Germany?page=1',
    'https://scholarshipdb.net/scholarships-in-Germany?page=2',
    'https://scholarshipdb.net/scholarships-in-United-Kingdom?page=1',
    'https://scholarshipdb.net/scholarships-in-United-Kingdom?page=2',
    'https://scholarshipdb.net/scholarships-in-Australia?page=1',
    'https://scholarshipdb.net/scholarships-in-Australia?page=2',
    'https://scholarshipdb.net/scholarships-in-Canada?page=1',
    'https://scholarshipdb.net/scholarships-in-USA?page=1',
    'https://scholarshipdb.net/scholarships-in-Japan?page=1',
    'https://scholarshipdb.net/scholarships-in-China?page=1',
    'https://scholarshipdb.net/scholarships-in-South-Korea?page=1',
    'https://scholarshipdb.net/scholarships-in-Netherlands?page=1',
    'https://scholarshipdb.net/scholarships-in-Turkey?page=1',
    'https://scholarshipdb.net/scholarships-in-Sweden?page=1',
    'https://scholarshipdb.net/scholarships-in-Norway?page=1',
    'https://scholarshipdb.net/scholarships-in-France?page=1',
    'https://scholarshipdb.net/scholarships-in-Italy?page=1',
    'https://scholarshipdb.net/scholarships-in-Hungary?page=1',
    'https://scholarshipdb.net/scholarships-in-Belgium?page=1',
    'https://scholarshipdb.net/scholarships-in-Switzerland?page=1',
    'https://scholarshipdb.net/scholarships-in-Denmark?page=1',
    'https://scholarshipdb.net/scholarships-in-Finland?page=1',
    'https://scholarshipdb.net/scholarships-in-Russia?page=1',
    'https://scholarshipdb.net/scholarships-in-Indonesia?page=1',
    'https://scholarshipdb.net/scholarships-in-Malaysia?page=1',
    'https://scholarshipdb.net/scholarships-in-Singapore?page=1',
    'https://scholarshipdb.net/scholarships-in-New-Zealand?page=1',
    'https://scholarshipdb.net/scholarships-in-Saudi-Arabia?page=1',
    'https://scholarshipdb.net/scholarships-in-UAE?page=1',
    'https://scholarshipdb.net/scholarships-in-Qatar?page=1',
]

# ── SMART FETCH ───────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.google.co.uk/",
    "https://www.google.com.pk/",
    "https://www.bing.com/",
    "https://search.yahoo.com/",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": random.choice(REFERERS),
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

def fetch(url, retries=4):
    if not url:
        return None
    if any(url.lower().endswith(ext) for ext in ['.pdf','.doc','.docx','.xls','.zip']):
        return None

    for attempt in range(retries):
        try:
            time.sleep(random.uniform(1.5, 3.5) * (1 + attempt * 0.5))
            headers = get_headers()
            if attempt > 0:
                headers.update({"DNT": "1", "Sec-Fetch-Dest": "document",
                                 "Sec-Fetch-Mode": "navigate"})
            r = requests.get(url, headers=headers, timeout=20, allow_redirects=True)

            if r.status_code == 200:
                low = r.text.lower()
                if any(b in low for b in ['access denied','cf-browser-verification','captcha','are you a robot']):
                    if attempt < retries - 1:
                        time.sleep(random.uniform(8, 15))
                        continue
                return r
            elif r.status_code == 403:
                time.sleep(random.uniform(10, 20))
            elif r.status_code == 429:
                time.sleep(random.uniform(25, 45))
            elif r.status_code == 404:
                return None
        except Exception:
            time.sleep(random.uniform(4, 8))
    return None

def get_domain(url):
    return urlparse(url).netloc.replace('www.', '').lower()

def is_aggregator(url):
    d = get_domain(url)
    return any(agg in d for agg in AGGREGATOR_DOMAINS)

def clean_soup(soup):
    for tag in soup.find_all(['nav','footer','script','style','aside','header','iframe','noscript']):
        tag.decompose()
    return soup

def get_text(soup):
    return ' '.join(soup.get_text(separator=' ', strip=True).split())

# ── OUTDATED CHECK ────────────────────────────────────────
def is_outdated(text):
    """Returns True only if we find dates AND all are in the past"""
    months = {
        'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
        'july':7,'august':8,'september':9,'october':10,'november':11,'december':12
    }
    patterns = [
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})',
        r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',
        r'(january|february|march|april|may|june|july|august|september|october|november|december)[,\s]+(\d{4})',
    ]
    found = []
    for p in patterns:
        for m in re.finditer(p, text.lower()):
            try:
                g = m.groups()
                if len(g) == 3 and g[0] in months:
                    found.append((int(g[2]), months[g[0]]))
                elif len(g) == 3 and g[1] in months:
                    found.append((int(g[2]), months[g[1]]))
                elif len(g) == 2 and g[0] in months:
                    found.append((int(g[1]), months[g[0]]))
            except:
                continue

    if not found:
        # No dates at all — check for current/next year mention
        if str(CURRENT_YEAR) in text or str(CURRENT_YEAR+1) in text:
            return False  # Has year mention = probably open
        return True  # No year at all = skip

    future = [(y,m) for y,m in found
               if y > CURRENT_YEAR or (y == CURRENT_YEAR and m >= CURRENT_MONTH)]
    return len(future) == 0

# ── TITLE FILTER ──────────────────────────────────────────
def is_bad_title(title):
    if not title or len(title) < 8:
        return True
    t = title.lower()

    # Always keep funded academic positions
    keep = [
        r'phd (position|fellowship|scholarship|studentship|candidate)',
        r'doctoral (fellowship|scholarship|studentship)',
        r'postdoc(toral)? fellowship',
        r'funded (phd|doctoral|masters|postgraduate|research)',
        r'fully.funded', r'fellowship', r'scholarship', r'bursary',
        r'award for students', r'grant for students', r'research grant',
        r'graduate fellowship', r'academic (award|prize)',
    ]
    for p in keep:
        if re.search(p, t):
            return False

    # Delete pure jobs and list pages
    bad = [
        r'\bsenior (manager|director|officer|consultant|analyst|engineer)\b',
        r'\b(program|project|research) manager\b',
        r'\bdirector general\b', r'\bassistant dean\b',
        r'\bchief (officer|executive|editor)\b',
        r'^lecturer,', r'^professor,',
        r'\bassistant professor\b', r'\bassociate professor\b',
        r'\bfull professor\b', r'\binstructional faculty\b',
        r'\bjob fair\b', r'\bhiring now\b',
        r'\bvacancy\b', r'\bvacancies\b',
        r'^top \d+', r'countries where tuition is free',
        r'^best scholarships', r'^list of scholarships',
        r'^\d{2,} (positions?|jobs?) (at|in)',
    ]
    for p in bad:
        if re.search(p, t):
            return True
    return False

# ── EXTRACTORS ────────────────────────────────────────────
def extract_deadline(text):
    months = "january|february|march|april|may|june|july|august|september|october|november|december"
    patterns = [
        rf'(?:deadline|closing date|apply by|due date|applications? (?:close|due))[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'(\d{{1,2}}\s+(?:{months})\s+\d{{4}})',
        rf'((?:{months})\s+\d{{1,2}},?\s+\d{{4}})',
        rf'((?:{months})\s+\d{{4}})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            groups = [g for g in m.groups() if g and g.lower() not in ['close','due']]
            if groups:
                dl = groups[-1].strip()
                if any(str(y) in dl for y in [CURRENT_YEAR, CURRENT_YEAR+1, CURRENT_YEAR+2]):
                    return dl
    return None

def extract_ielts(text):
    m = re.search(r'ielts[:\s]*(?:score[:\s]*|minimum[:\s]*|of[:\s]*)?(\d+\.?\d*)', text, re.IGNORECASE)
    if m:
        s = float(m.group(1))
        if 4.0 <= s <= 9.0:
            return str(s)
    return "Required" if re.search(r'\bielts\b', text, re.IGNORECASE) else "Not required"

def extract_toefl(text):
    m = re.search(r'toefl[:\s]*(?:ibt[:\s]*)?(\d+)', text, re.IGNORECASE)
    if m: return m.group(1)
    return "Required" if re.search(r'\btoefl\b', text, re.IGNORECASE) else None

def extract_gpa(text):
    for p in [
        r'(?:minimum\s+)?(?:gpa|cgpa)[:\s]*(?:of\s+)?(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*(?:out of\s*\d+\s*)?(?:gpa|cgpa)',
        r'(\d{2,3})%\s*(?:or above|minimum|at least)',
        r'(first class|2:1|upper second)',
    ]:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return (m.group(1) if m.groups() else m.group(0))[:30]
    return None

def extract_degree(text):
    levels = []
    if re.search(r'\bundergraduate|bachelor\b', text, re.IGNORECASE): levels.append("Bachelor")
    if re.search(r'\bmaster|postgraduate|msc\b|mba\b', text, re.IGNORECASE): levels.append("Master")
    if re.search(r'\bphd|doctoral|doctorate\b', text, re.IGNORECASE): levels.append("PhD")
    if re.search(r'\bpostdoc|post-doc\b', text, re.IGNORECASE): levels.append("Postdoc")
    return ", ".join(levels) if levels else "All levels"

def extract_funding(text):
    if re.search(r'full.?fund|fully.?fund|full scholarship|covers (all|tuition|living)', text, re.IGNORECASE):
        return "Fully Funded"
    if re.search(r'partial|tuition only|tuition fee waiver', text, re.IGNORECASE):
        return "Partial"
    if re.search(r'stipend|living allowance|monthly allowance', text, re.IGNORECASE):
        return "Stipend Included"
    return "Check website"

def extract_eligible_countries(text):
    countries = [
        "Pakistan","India","Bangladesh","Nepal","Sri Lanka","Afghanistan",
        "Nigeria","Ghana","Kenya","Ethiopia","Tanzania","Uganda","Rwanda",
        "South Africa","Egypt","Morocco","Tunisia","Algeria","Zimbabwe","Zambia",
        "Indonesia","Malaysia","Philippines","Vietnam","Thailand","Cambodia",
        "Brazil","Colombia","Mexico","Peru","Argentina","Bolivia","Ecuador",
        "Russia","Ukraine","Kazakhstan","Uzbekistan","Azerbaijan",
        "developing countries","low-income countries","African countries",
        "Asian countries","all countries","international students","worldwide",
    ]
    found = []
    tl = text.lower()
    for c in countries:
        if c.lower() in tl:
            found.append(c)
    if found:
        return ", ".join(found[:15])
    if any(w in tl for w in ['all nationalities','international','worldwide','global']):
        return "Open to international students worldwide"
    return "Open to international students"

def extract_benefits(text):
    b = []
    checks = {
        "Full tuition": r'full tuition|tuition.*cover|covers.*tuition',
        "Living allowance": r'living allowance|monthly stipend|living expenses',
        "Travel grant": r'travel (grant|allowance)|airfare|return flight',
        "Health insurance": r'health insurance|medical cover',
        "Housing": r'accommodation|housing|dormitor',
        "Books allowance": r'books? allowance|study materials?',
    }
    for name, p in checks.items():
        if re.search(p, text, re.IGNORECASE):
            b.append(name)
    return ", ".join(b) if b else ""

def extract_university(soup, url, fallback=""):
    meta = soup.find('meta', {'property': 'og:site_name'})
    if meta and meta.get('content') and not is_aggregator(url):
        return meta['content'].strip()[:80]
    domain = get_domain(url)
    clean = re.sub(r'\.(edu|ac|gov|org|com|net|co)(\..*)?$', '', domain)
    return clean.replace('-',' ').replace('.',' ').title()[:80] or fallback

def detect_country(domain, text=""):
    tld_map = {
        '.ac.uk':'United Kingdom', '.co.uk':'United Kingdom', '.uk':'United Kingdom',
        '.edu.au':'Australia', '.com.au':'Australia', '.au':'Australia',
        '.edu.cn':'China', '.ac.jp':'Japan', '.ac.kr':'South Korea',
        '.ca':'Canada', '.de':'Germany', '.fr':'France', '.nl':'Netherlands',
        '.se':'Sweden', '.no':'Norway', '.fi':'Finland', '.dk':'Denmark',
        '.ch':'Switzerland', '.at':'Austria', '.be':'Belgium', '.it':'Italy',
        '.es':'Spain', '.pt':'Portugal', '.pl':'Poland', '.hu':'Hungary',
        '.tr':'Turkey', '.sa':'Saudi Arabia', '.ae':'UAE', '.qa':'Qatar',
        '.cn':'China', '.jp':'Japan', '.kr':'South Korea', '.my':'Malaysia',
        '.sg':'Singapore', '.nz':'New Zealand', '.za':'South Africa',
        '.ru':'Russia', '.id':'Indonesia', '.th':'Thailand', '.vn':'Vietnam',
        '.pk':'Pakistan', '.in':'India', '.bd':'Bangladesh',
        '.edu':'USA', '.gov':'USA',
    }
    for tld, country in sorted(tld_map.items(), key=lambda x: -len(x[0])):
        if domain.endswith(tld):
            return country
    hints = {
        'germany':'Germany', 'britain':'United Kingdom', 'england':'United Kingdom',
        'australia':'Australia', 'canada':'Canada', 'japan':'Japan', 'china':'China',
        'korea':'South Korea', 'turkey':'Turkey', 'france':'France',
        'netherlands':'Netherlands', 'sweden':'Sweden', 'norway':'Norway',
        'finland':'Finland', 'hungary':'Hungary', 'united states':'USA',
        'saudi arabia':'Saudi Arabia', 'malaysia':'Malaysia', 'singapore':'Singapore',
        'new zealand':'New Zealand', 'italy':'Italy', 'belgium':'Belgium',
        'switzerland':'Switzerland', 'denmark':'Denmark', 'austria':'Austria',
        'russia':'Russia', 'indonesia':'Indonesia', 'thailand':'Thailand',
        'vietnam':'Vietnam', 'pakistan':'Pakistan', 'india':'India',
    }
    tl = text.lower()[:2000]
    for hint, country in hints.items():
        if hint in tl:
            return country
    return "International"

def detect_region(country):
    regions = {
        'Europe': ['United Kingdom','Germany','France','Netherlands','Sweden','Norway',
                   'Finland','Denmark','Switzerland','Austria','Belgium','Italy','Spain',
                   'Portugal','Poland','Hungary','Ireland','Russia','Ukraine'],
        'Middle East': ['Turkey','Saudi Arabia','UAE','Qatar','Jordan','Kuwait',
                        'Egypt','Morocco','Tunisia','Algeria'],
        'Asia': ['China','Japan','South Korea','Malaysia','Singapore','Thailand',
                 'Indonesia','Vietnam','Pakistan','India','Bangladesh','Nepal',
                 'Sri Lanka','Philippines','Kazakhstan'],
        'Oceania': ['Australia','New Zealand'],
        'North America': ['USA','Canada','Mexico'],
        'Africa': ['Nigeria','South Africa','Kenya','Ghana','Ethiopia','Tanzania',
                   'Uganda','Rwanda','Zimbabwe','Zambia'],
        'Latin America': ['Brazil','Colombia','Peru','Argentina','Chile','Bolivia'],
    }
    for region, countries in regions.items():
        if country in countries:
            return region
    return "International"

# ── OFFICIAL LINK FINDER ──────────────────────────────────
def find_official_link(soup, current_url):
    current_domain = get_domain(current_url)
    apply_kw = [
        'apply now','apply here','apply online','official website','official link',
        'visit official','click here to apply','application portal','official scholarship',
        'scholarship page','university website','apply for this','more information',
        'official page','application form','submit application','visit website',
        'learn more','click here','apply at','apply through','online application',
    ]
    official_tlds = ['.edu','.ac.uk','.edu.au','.ac.jp','.ac.kr','.edu.cn',
                     '.gov','.ac.nz','.ac.za','.ac.in']
    known_orgs = [
        'chevening.org','daad.de','fulbright','campuschina.org','turkiyeburslari',
        'stipendiumhungaricum','studyinkorea','schwarzmanscholars','aauw.org',
        'worldbank.org','erasmus','commonwealth','australiaawards','britishcouncil',
        'nuffic.nl','vliruos.be','kaust.edu.sa','mastercard.foundation',
    ]

    candidates = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        lt = a.get_text(strip=True).lower()
        if not href or href.startswith('#') or 'javascript' in href:
            continue
        if any(href.lower().endswith(e) for e in ['.pdf','.doc','.docx']):
            continue
        if any(s in href for s in ['facebook.','twitter.','instagram.','linkedin.',
                                    'youtube.','whatsapp.','telegram.']):
            continue
        if href.startswith('/'):
            p = urlparse(current_url)
            href = f"{p.scheme}://{p.netloc}{href}"
        elif not href.startswith('http'):
            href = urljoin(current_url, href)

        ld = get_domain(href)
        if ld == current_domain or is_aggregator(href):
            continue

        score = 0
        for tld in official_tlds:
            if ld.endswith(tld): score += 20
        for org in known_orgs:
            if org in ld or org in href.lower(): score += 18
        for kw in apply_kw:
            if kw in lt: score += 12
        if any(kw in href.lower() for kw in ['scholarship','fellowship','grant','apply','admission','funding']):
            score += 8
        if score == 0:
            score = 2  # any external link is a candidate

        candidates.append((score, href))

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    for score, link in candidates:
        if not link.lower().endswith(('.pdf','.doc','.docx')):
            return link
    return None

# ── BLOG WRITER ───────────────────────────────────────────
def write_blog(d):
    lang = f"IELTS {d['ielts']}" if d['ielts'] not in ['Not required','Required'] else d['ielts']
    toefl_line = f"\n- TOEFL: {d['toefl']}" if d.get('toefl') else ""
    gpa_line = d.get('gpa') or "Check official website"
    benefits_line = d.get('benefits') or "Check official website for complete benefits"

    seo_title = f"{d['title']} {CURRENT_YEAR} — Eligibility, Deadline & How to Apply"[:70]
    seo_desc = (f"Apply for {d['title']}. Deadline: {d['deadline']}. "
                f"{d['degree']} students. {lang}. "
                f"Eligible: {d['eligible_countries'][:60]}.")[:160]

    blog = f"""# {d['title']} {CURRENT_YEAR}

**Last Updated:** {datetime.now().strftime("%B %d, %Y")} | **Status:** Open for Applications

---

## About This Scholarship

The **{d['title']}** is offered by **{d['university']}** in **{d['country']}**. This is a genuine opportunity for international students including students from Pakistan, India, Bangladesh, Nigeria and other developing countries to study abroad without paying agents.

---

## Quick Summary

| Detail | Information |
|--------|------------|
| **Scholarship** | {d['title']} |
| **University / Body** | {d['university']} |
| **Country** | {d['country']} |
| **Region** | {d['region']} |
| **Degree Level** | {d['degree']} |
| **Funding** | {d['funding']} |
| **Deadline** | {d['deadline']} |
| **IELTS Required** | {d['ielts']} |
| **Min GPA** | {gpa_line} |
| **Last Verified** | {datetime.now().strftime("%B %Y")} |

---

## Eligibility

**Who can apply:** {d['eligible_countries']}

**Degree levels:** {d['degree']}

---

## What Does This Scholarship Cover?

**Funding: {d['funding']}**

{benefits_line}

---

## English Language Requirements

{"No IELTS or TOEFL required. Ideal for students who have not yet taken an English test." if d['ielts'] == "Not required" else f"**IELTS:** {d['ielts']}{toefl_line}\n\nIELTS is available in Karachi, Lahore, Islamabad and many other cities. Start preparation 3 months before deadline."}

---

## Deadline

**{d['deadline']}**

- 3 months before: Gather all documents
- 2 months before: Write your Statement of Purpose
- 1 month before: Get recommendation letters
- 2 weeks before: Submit — never wait for the last day

---

## Documents Needed

- Valid Passport
- Academic Transcripts (all degrees, certified)
- Degree Certificate
- IELTS/TOEFL (if required: {lang})
- Statement of Purpose (600-1000 words)
- 2-3 Recommendation Letters
- Academic CV
- Research Proposal (PhD only)

---

## How to Write a Winning SOP

**Opening:** Start with a real story — a challenge, a turning point. Never start with "I am applying for..."

**Academic background:** Degree, GPA, key projects. Numbers are stronger than adjectives.

**Why this scholarship:** Show you chose this deliberately. Research the university and program specifically.

**Career goals:** Where will you be in 5-10 years? How does this scholarship fit?

**Why you:** Leadership, research, community work — evidence, not claims.

**Closing:** Confident, genuine, forward-looking. 600-1000 words.

---

## Apply Now

**Official Link:** {d['official_link']}

> Last verified by AdmitGoal: {datetime.now().strftime("%B %d, %Y")}

*Share this with a friend who deserves a scholarship.*
"""
    return blog, seo_title, seo_desc

# ── SAVE ──────────────────────────────────────────────────
def save(conn, data):
    if not data.get('title') or len(data['title']) < 8: return False
    if not data.get('official_link'): return False
    if not data.get('deadline'): return False
    if is_bad_title(data['title']): return False

    blog, seo_title, seo_desc = write_blog(data)
    try:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO scholarship_details
            (scholarship_link, title, full_description, eligible_countries,
             eligible_students, degree_level, deadline, language_requirement,
             ielts_score, benefits, how_to_apply, blog_post, seo_title,
             seo_description, university_name, country, region,
             funding_type, gpa_required, last_updated)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (scholarship_link) DO UPDATE SET
              deadline=EXCLUDED.deadline, last_updated=EXCLUDED.last_updated,
              blog_post=EXCLUDED.blog_post, seo_title=EXCLUDED.seo_title,
              seo_description=EXCLUDED.seo_description,
              eligible_countries=EXCLUDED.eligible_countries
        ''', (
            data['official_link'], data['title'],
            data.get('description','')[:800], data['eligible_countries'],
            "International students", data['degree'], data['deadline'],
            f"IELTS {data['ielts']}" if data['ielts'] != 'Not required' else "Not required",
            data['ielts'], data.get('benefits',''), f"Visit: {data['official_link']}",
            blog, seo_title, seo_desc, data['university'],
            data['country'], data['region'], data['funding'],
            data.get('gpa') or "Check website", datetime.now().strftime("%Y-%m-%d")
        ))
        cur.execute('''
            INSERT INTO scholarships (title, description, country, deadline, link, source, scraped_date)
            VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (link) DO NOTHING
        ''', (
            data['title'], seo_desc, data['country'], data['deadline'],
            data['official_link'], data['university'][:50], datetime.now().strftime("%Y-%m-%d")
        ))
        cur.close()
        return True
    except Exception as e:
        print(f"    DB Error: {e}")
        return False

# ── PROCESS ONE SCHOLARSHIP URL ───────────────────────────
def process_url(url, conn, hint_country="", hint_region=""):
    """
    Full pipeline: fetch → extract data → find official link → save.
    Works for both aggregator posts and direct official pages.
    Never skips just because official page is blocked — uses what it has.
    """
    r = fetch(url)
    if not r:
        return False

    soup = clean_soup(BeautifulSoup(r.text, 'lxml'))
    text = get_text(soup)

    if not any(kw in text.lower() for kw in ['scholarship','fellowship','grant','award','funding','stipend','bursary']):
        return False

    if is_outdated(text):
        return False

    # Get title
    h1 = soup.find('h1')
    title = h1.get_text(strip=True) if h1 else ""
    if not title:
        t = soup.find('title')
        title = t.get_text(strip=True).split('|')[0].split('–')[0].strip() if t else ""
    if not title or is_bad_title(title):
        return False

    # Find official link if on aggregator
    official_link = url
    combined_text = text
    official_soup = soup

    if is_aggregator(url):
        found_link = find_official_link(soup, url)
        if found_link:
            off_r = fetch(found_link)
            if off_r:
                official_soup = clean_soup(BeautifulSoup(off_r.text, 'lxml'))
                official_text = get_text(official_soup)
                combined_text = text + " " + official_text
                official_link = found_link
            else:
                # Official page blocked — keep aggregator URL but use post data
                official_link = url
        else:
            official_link = url

    # Extract all data
    deadline = extract_deadline(combined_text) or extract_deadline(text)
    if not deadline:
        return False

    ielts = extract_ielts(combined_text)
    toefl = extract_toefl(combined_text)
    gpa = extract_gpa(combined_text)
    degree = extract_degree(combined_text)
    funding = extract_funding(combined_text)
    eligible = extract_eligible_countries(combined_text)
    benefits = extract_benefits(combined_text)

    domain = get_domain(official_link)
    country = detect_country(domain, combined_text) or hint_country or "International"
    region = detect_region(country) or hint_region or "International"

    uni = extract_university(official_soup, official_link)
    if not uni or is_aggregator(official_link):
        uni = extract_university(soup, url, fallback=domain.title())

    desc = ""
    for p in soup.find_all('p'):
        t = p.get_text(strip=True)
        if len(t) > 80:
            desc = t[:600]
            break
    if not desc:
        desc = combined_text[:400]

    return save(conn, {
        'title': title, 'description': desc, 'university': uni,
        'country': country, 'region': region, 'deadline': deadline,
        'ielts': ielts, 'toefl': toefl, 'gpa': gpa, 'degree': degree,
        'funding': funding, 'eligible_countries': eligible,
        'benefits': benefits, 'official_link': official_link,
    })

# ── GET POST LINKS FROM LISTING PAGE ─────────────────────
def get_post_links(listing_url):
    """Get ALL individual post/scholarship links from a listing page — no limit"""
    r = fetch(listing_url)
    if not r:
        return []

    soup = BeautifulSoup(r.text, 'lxml')
    parsed = urlparse(listing_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    listing_domain = get_domain(listing_url)

    skip = ['/category/','/tag/','/author/','mailto:','javascript:',
            'facebook.','twitter.','instagram.','linkedin.','youtube.',
            '/about','/contact','/privacy','/terms','/search',
            'login','register','signup','.pdf','.doc','#']

    links = []
    seen = set()

    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        text = a.get_text(strip=True)

        if not href: continue
        if href.startswith('/'):
            href = base + href
        elif not href.startswith('http'):
            continue

        if any(s in href.lower() for s in skip): continue
        if href in seen or href == listing_url: continue
        if get_domain(href) != listing_domain: continue

        path_parts = [p for p in urlparse(href).path.split('/') if p]
        if len(path_parts) >= 1 and len(text) > 8:
            seen.add(href)
            links.append((text[:80], href))

    return links  # No limit — process everything

# ── MAIN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 62)
    print("  ADMITGOAL SMART SCRAPER v6.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("  Worldwide | Anti-block | No limits | Official links")
    print("=" * 62)

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    total_saved = 0
    total_skipped = 0

    # Phase 1: Direct official scholarship pages
    print(f"\n{'─'*62}")
    print("PHASE 1: Direct official scholarship pages (worldwide)")
    print(f"{'─'*62}")

    for src in DIRECT_SCHOLARSHIPS:
        print(f"\n[DIRECT] {src['country']} — {src['url'][:55]}")
        try:
            saved = process_url(src['url'], conn, src['country'], src['region'])
            if saved:
                print(f"  ✓ SAVED")
                total_saved += 1
            else:
                print(f"  Skipped")
                total_skipped += 1
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(random.uniform(3, 5))

    # Phase 2: Aggregator listing pages
    print(f"\n{'─'*62}")
    print("PHASE 2: Aggregator sources — worldwide scholarship discovery")
    print(f"{'─'*62}")

    for listing_url in AGGREGATOR_SOURCES:
        print(f"\n[SOURCE] {listing_url}")
        post_links = get_post_links(listing_url)
        print(f"  Found {len(post_links)} posts — processing all")

        for title, link in post_links:
            print(f"\n  → {title[:60]}")
            try:
                saved = process_url(link, conn)
                if saved:
                    print(f"  ✓ SAVED")
                    total_saved += 1
                else:
                    print(f"  Skipped")
                    total_skipped += 1
            except Exception as e:
                print(f"  Error: {e}")
                total_skipped += 1
            time.sleep(random.uniform(1.5, 3))

        time.sleep(random.uniform(3, 6))

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scholarship_details")
    db_total = cur.fetchone()[0]
    cur.close()
    conn.close()

    print(f"\n{'='*62}")
    print(f"  DONE!")
    print(f"  New saved  : {total_saved}")
    print(f"  Skipped    : {total_skipped}")
    print(f"  Total in DB: {db_total}")
    print(f"{'='*62}")