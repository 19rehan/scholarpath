import requests
from bs4 import BeautifulSoup
import psycopg2
import os
import time
import random
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres.deqyxksflvlxjelppgxz:Rehan1819Rehan@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'
)

AGGREGATOR_DOMAINS = [
    'scholars4dev.com', 'scholarshipdb.net', 'opportunitydesk.org',
    'afterschoolafrica.com', 'youthop.com', 'mastersportal.eu',
    'phdportal.eu', 'opportunitiesforafricans.com', 'scholarships4dev.com',
    'scholarshipscorner.website', 'scholarshipsads.com', 'admitgoal.com'
]

def is_aggregator(url):
    domain = urlparse(url).netloc.lower().replace('www.', '')
    return any(agg in domain for agg in AGGREGATOR_DOMAINS)

def get_headers():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    ]
    return {
        "User-Agent": random.choice(agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
    }

def fetch(url, retries=3):
    # Never fetch PDFs
    if url.lower().endswith('.pdf'):
        return None
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

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

def is_open(text):
    text_lower = text.lower()
    closed = [
        'applications are closed', 'deadline has passed',
        'no longer accepting', 'competition is closed',
        'this position has been filled', 'closed for applications',
        'applications have closed', 'deadline passed'
    ]
    for c in closed:
        if c in text_lower:
            return False

    months = {
        'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
        'july':7,'august':8,'september':9,'october':10,'november':11,'december':12
    }
    patterns = [
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})',
        r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',
        r'deadline[:\s]*(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',
    ]
    found_dates = []
    for pattern in patterns:
        for m in re.finditer(pattern, text_lower):
            try:
                g = m.groups()
                if g[0] in months:
                    month, year = months[g[0]], int(g[2])
                elif len(g) == 2 and g[0] in months:
                    month, year = months[g[0]], int(g[1])
                else:
                    month, year = months[g[1]], int(g[2])
                found_dates.append((year, month))
            except:
                continue

    if found_dates:
        future_dates = [(y, m) for y, m in found_dates if y > CURRENT_YEAR or (y == CURRENT_YEAR and m >= CURRENT_MONTH)]
        if future_dates:
            return True
        max_year = max(y for y, m in found_dates)
        if max_year < CURRENT_YEAR - 1:
            return False
        return False

    if str(CURRENT_YEAR + 1) in text:
        return True
    if str(CURRENT_YEAR) in text:
        return True
    return False

def is_job_not_scholarship(title):
    """Return True if this is a pure job listing, not a scholarship/funded position"""
    if not title:
        return True
    t = title.lower()

    # KEEP these even if they sound like jobs — they are funded academic positions
    funded_keep = [
        r'phd (position|fellowship|scholarship|candidate|student)',
        r'doctoral (fellowship|scholarship|position|candidate)',
        r'postdoc(toral)? (fellowship|scholarship)',
        r'funded (phd|doctoral|masters)',
        r'fully.funded',
        r'fellowship',
        r'scholarship',
        r'bursary',
        r'grant for',
        r'award for',
        r'stipend for students',
    ]
    for p in funded_keep:
        if re.search(p, t):
            return False  # Keep it

    # DELETE pure job listings
    job_patterns = [
        r'senior (scientist|researcher|manager|engineer|director|officer|analyst|consultant)',
        r'(scientific|research|program|project) manager',
        r'director (general|of )',
        r'assistant dean',
        r'chief (officer|executive|scientist|editor)',
        r'^lecturer,?\s',
        r'^associate lecturer',
        r'^professor,?\s',
        r'assistant professor',
        r'associate professor',
        r'full professor',
        r'instructional faculty',
        r'faculty position',
        r'job fair',
        r'hiring now',
        r'\bvacancy\b',
        r'\bvacancies\b',
        r'open (call for)? (staff|employees|applicants for position)',
        r'^\d{2,} positions? (at|in)',  # "152 positions at X"
        r'^top \d+',
        r'countries where tuition is free',
        r'^best scholarships',
        r'^list of scholarships',
    ]
    for p in job_patterns:
        if re.search(p, t):
            return True

    return False

def extract_deadline(text):
    months = "january|february|march|april|may|june|july|august|september|october|november|december"
    patterns = [
        rf'deadline[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'closing date[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'apply by[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'applications? (close|due)[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'(\d{{1,2}}\s+(?:{months})\s+\d{{4}})',
        rf'((?:{months})\s+\d{{1,2}},?\s+\d{{4}})',
        rf'((?:{months})\s+\d{{4}})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            groups = [g for g in m.groups() if g and g.lower() not in ['close', 'due']]
            if groups:
                return groups[-1].strip()
    return None

def extract_ielts(text):
    patterns = [
        r'ielts[:\s]*(?:score[:\s]*)?(\d+\.?\d*)',
        r'ielts[:\s]*(?:minimum[:\s]*)?(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*(?:in|for)?\s*ielts',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            score = float(m.group(1))
            if 4.0 <= score <= 9.0:
                return str(score)
    if re.search(r'\bielts\b', text, re.IGNORECASE):
        return "Required"
    return "Not required"

def extract_pte(text):
    m = re.search(r'pte[:\s]*(\d+)', text, re.IGNORECASE)
    if m: return m.group(1)
    return "Required" if re.search(r'\bpte\b', text, re.IGNORECASE) else None

def extract_toefl(text):
    m = re.search(r'toefl[:\s]*(?:ibt[:\s]*)?(\d+)', text, re.IGNORECASE)
    if m: return m.group(1)
    return "Required" if re.search(r'\btoefl\b', text, re.IGNORECASE) else None

def extract_gpa(text):
    patterns = [
        r'(?:minimum\s+)?gpa[:\s]*(?:of\s+)?(\d+\.?\d*)',
        r'cgpa[:\s]*(?:of\s+)?(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*(?:out of\s*)?\d*\s*gpa',
        r'(\d{2,3})%\s*(?:or above|minimum|at least)',
        r'first class|2:1|upper second',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            result = m.group(0) if not m.groups() else m.group(1)
            return result[:30]
    return None

def extract_degree(text):
    levels = []
    if re.search(r'\bundergraduate|bachelor\'?s?\b', text, re.IGNORECASE):
        levels.append("Bachelor")
    if re.search(r'\bmaster\'?s?|postgraduate|msc\b|mba\b', text, re.IGNORECASE):
        levels.append("Master")
    if re.search(r'\bphd|doctoral|doctorate\b', text, re.IGNORECASE):
        levels.append("PhD")
    if re.search(r'\bpostdoc|post-doc\b', text, re.IGNORECASE):
        levels.append("Postdoc")
    return levels

def extract_funding(text):
    if re.search(r'full.?fund|fully.?fund|full scholarship|covers all', text, re.IGNORECASE):
        return "Fully Funded"
    if re.search(r'partial|50%|tuition only|tuition fee waiver', text, re.IGNORECASE):
        return "Partial"
    if re.search(r'stipend|living allowance|monthly allowance', text, re.IGNORECASE):
        return "Stipend Included"
    return "Check website"

def extract_eligible_countries(text):
    all_countries = [
        "Pakistan", "India", "Bangladesh", "Nepal", "Sri Lanka",
        "Afghanistan", "Nigeria", "Ghana", "Kenya", "Ethiopia",
        "Tanzania", "Uganda", "Rwanda", "Zimbabwe", "Zambia",
        "South Africa", "Egypt", "Morocco", "Tunisia", "Algeria",
        "Indonesia", "Malaysia", "Philippines", "Vietnam", "Thailand",
        "Cambodia", "Myanmar", "China", "Mongolia",
        "Brazil", "Colombia", "Peru", "Argentina", "Mexico",
    ]
    found = []
    text_lower = text.lower()
    for country in all_countries:
        if country.lower() in text_lower:
            found.append(country)
    if found:
        return found
    if any(w in text_lower for w in ['all nationalities', 'all countries', 'international', 'worldwide', 'global']):
        return ["Open to international students worldwide"]
    return ["Check official website for eligible countries"]

def extract_benefits(text):
    benefits = []
    patterns = {
        "Full tuition fee": r'full tuition|tuition fee.*cover|covers.*tuition',
        "Living allowance": r'living allowance|monthly stipend|living expenses',
        "Travel grant": r'travel (grant|allowance|cost)|airfare|flight',
        "Health insurance": r'health insurance|medical (cover|insurance)',
        "Housing": r'accommodation|housing|dormitor',
        "Books allowance": r'book(s)? allowance|study material',
    }
    for benefit, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            benefits.append(benefit)
    return benefits if benefits else None

def extract_official_link(soup, current_url, source_is_aggregator):
    """
    If source is aggregator: find the external official link they point to.
    If source is already official: return current_url.
    """
    if not source_is_aggregator:
        return current_url

    # Priority 1: buttons/links with apply text pointing to external domain
    apply_keywords = [
        'apply now', 'apply here', 'apply online', 'official website',
        'official link', 'visit official', 'click here to apply',
        'application portal', 'submit application', 'apply for this',
        'more information', 'learn more', 'visit website', 'official page'
    ]

    current_domain = urlparse(current_url).netloc.replace('www.', '')
    candidates = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        link_text = a.get_text(strip=True).lower()

        # Skip non-links
        if any(skip in href for skip in ['#', 'javascript:', 'mailto:', 'facebook.com',
                                          'twitter.com', 'instagram.com', 'linkedin.com',
                                          'youtube.com', '.pdf', '.doc', '.docx']):
            continue

        # Make absolute
        if href.startswith('/'):
            parsed = urlparse(current_url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        elif not href.startswith('http'):
            continue

        href_domain = urlparse(href).netloc.replace('www.', '')

        # Must be external (not same aggregator domain)
        if href_domain == current_domain:
            continue

        # Must not be another aggregator
        if is_aggregator(href):
            continue

        score = 0

        # High score for apply/official keywords in link text
        for kw in apply_keywords:
            if kw in link_text:
                score += 15

        # High score for official domains
        official_tlds = ['.edu', '.ac.uk', '.edu.au', '.ac.jp', '.ac.kr',
                         '.edu.cn', '.gov', '.ac.nz', '.ac.za']
        for tld in official_tlds:
            if href_domain.endswith(tld):
                score += 10

        # Score for known scholarship orgs
        known_orgs = ['chevening.org', 'daad.de', 'fulbright', 'campuschina',
                      'turkiyeburslari', 'stipendiumhungaricum', 'studyinkorea',
                      'schwarzmanscholars.org', 'aauw.org', 'commonwealthscholarships',
                      'australiaawards', 'erasmus', 'worldbank.org', 'oecd.org']
        for org in known_orgs:
            if org in href_domain:
                score += 8

        # Any external link gets base score
        if score == 0:
            score = 1

        candidates.append((score, href))

    if candidates:
        candidates.sort(reverse=True)
        best = candidates[0][1]
        # Don't return PDFs or OECD DAC lists or irrelevant docs
        if '.pdf' not in best.lower():
            return best

    return None  # No good official link found — skip this scholarship

def detect_country(domain, text=""):
    tld_map = {
        '.ac.uk': 'United Kingdom', '.co.uk': 'United Kingdom', '.uk': 'United Kingdom',
        '.edu.au': 'Australia', '.com.au': 'Australia', '.au': 'Australia',
        '.ca': 'Canada', '.de': 'Germany', '.fr': 'France',
        '.nl': 'Netherlands', '.se': 'Sweden', '.no': 'Norway',
        '.fi': 'Finland', '.dk': 'Denmark', '.ch': 'Switzerland',
        '.at': 'Austria', '.be': 'Belgium', '.it': 'Italy',
        '.es': 'Spain', '.pt': 'Portugal', '.pl': 'Poland',
        '.cz': 'Czech Republic', '.hu': 'Hungary', '.ro': 'Romania',
        '.tr': 'Turkey', '.sa': 'Saudi Arabia', '.ae': 'UAE',
        '.qa': 'Qatar', '.cn': 'China', '.jp': 'Japan', '.kr': 'South Korea',
        '.my': 'Malaysia', '.sg': 'Singapore', '.nz': 'New Zealand',
        '.za': 'South Africa', '.edu': 'USA', '.gov': 'USA',
    }
    for tld, country in sorted(tld_map.items(), key=lambda x: -len(x[0])):
        if domain.endswith(tld):
            return country

    country_hints = {
        'germany': 'Germany', 'uk': 'United Kingdom', 'britain': 'United Kingdom',
        'australia': 'Australia', 'canada': 'Canada', 'japan': 'Japan',
        'china': 'China', 'korea': 'South Korea', 'turkey': 'Turkey',
        'france': 'France', 'netherlands': 'Netherlands', 'sweden': 'Sweden',
        'norway': 'Norway', 'finland': 'Finland', 'hungary': 'Hungary',
        'usa': 'USA', 'united states': 'USA', 'america': 'USA',
        'saudi arabia': 'Saudi Arabia', 'malaysia': 'Malaysia',
        'singapore': 'Singapore', 'new zealand': 'New Zealand',
        'italy': 'Italy', 'belgium': 'Belgium', 'switzerland': 'Switzerland',
    }
    text_lower = text.lower()[:800]
    for hint, c in country_hints.items():
        if hint in text_lower:
            return c
    return "International"

def detect_region(country):
    regions = {
        'Europe': ['United Kingdom','Germany','France','Netherlands','Sweden',
                   'Norway','Finland','Denmark','Switzerland','Austria','Belgium',
                   'Italy','Spain','Portugal','Poland','Czech Republic','Hungary',
                   'Romania','Ireland','Luxembourg'],
        'Middle East': ['Turkey','Saudi Arabia','UAE','Qatar','Jordan',
                        'Kuwait','Egypt','Morocco','Tunisia','Algeria'],
        'Asia': ['China','Japan','South Korea','Malaysia','Singapore',
                 'Thailand','Indonesia','Vietnam','Pakistan','India',
                 'Bangladesh','Sri Lanka','Nepal','Philippines'],
        'Oceania': ['Australia','New Zealand'],
        'North America': ['USA','Canada','Mexico'],
        'Africa': ['Nigeria','South Africa','Kenya','Ghana','Ethiopia',
                   'Tanzania','Uganda','Rwanda','Zimbabwe'],
        'Latin America': ['Brazil','Colombia','Peru','Argentina','Chile'],
    }
    for region, countries in regions.items():
        if country in countries:
            return region
    return "International"

def write_blog(data):
    title = data['title']
    country = data['country']
    region = data['region']
    uni = data['university_name']
    deadline = data['deadline'] or "Check official website"
    ielts = data['ielts_score']
    pte = data['pte_score']
    toefl = data['toefl_score']
    gpa = data['gpa_required']
    degree_levels = data['degree_levels']
    funding = data['funding_type']
    benefits = data['benefits']
    eligible_countries = data['eligible_countries']
    official_link = data['scholarship_link']

    lang_parts = []
    if ielts and ielts != "Not required":
        lang_parts.append(f"IELTS {ielts}")
    if pte:
        lang_parts.append(f"PTE {pte}")
    if toefl:
        lang_parts.append(f"TOEFL {toefl}")
    lang_str = " / ".join(lang_parts) if lang_parts else "No English test required"

    countries_str = ", ".join(eligible_countries[:10]) if isinstance(eligible_countries, list) else str(eligible_countries)
    benefits_str = "\n".join([f"- {b}" for b in benefits]) if isinstance(benefits, list) and benefits else "- Check official website for complete benefits"
    degree_str = ", ".join(degree_levels) if isinstance(degree_levels, list) and degree_levels else "All levels"

    seo_title = f"{title} {CURRENT_YEAR} — Complete Guide, Eligibility & How to Apply"[:70]
    seo_desc = (f"Apply for {title} {CURRENT_YEAR}. Deadline: {deadline}. "
                f"Open for {degree_str} students. {lang_str}. "
                f"Eligible: {countries_str[:80]}.")[:160]

    blog = f"""# {title} {CURRENT_YEAR}

**Last Updated:** {datetime.now().strftime("%B %d, %Y")} | **Status:** Open for Applications

---

## About This Scholarship

The **{title}** is offered by **{uni}** in **{country}**, {region}. This is a genuine opportunity for international students who want to pursue world-class education abroad.

---

## Quick Summary

| Detail | Information |
|--------|------------|
| **Scholarship Name** | {title} |
| **Host University** | {uni} |
| **Country** | {country} |
| **Degree Level** | {degree_str} |
| **Funding Type** | {funding} |
| **Deadline** | {deadline} |
| **IELTS Required** | {ielts or "Not required"} |
| **TOEFL Required** | {toefl or "Not required"} |
| **Minimum GPA** | {gpa or "Check official website"} |

---

## Eligibility

**Countries:** {countries_str}

**Degree Level:** {degree_str}

---

## What Does It Cover?

**Funding: {funding}**

{benefits_str}

---

## English Language Requirements

{f"IELTS: {ielts}" if ielts and ielts != 'Not required' else "No English test specifically required — verify on official website."}
{f"TOEFL: {toefl}" if toefl else ""}
{f"PTE: {pte}" if pte else ""}

---

## Deadline

**{deadline}** — Always verify on the official website.

---

## How to Apply

1. Visit the official link below
2. Check full eligibility criteria
3. Prepare documents: passport, transcripts, SOP, recommendation letters
4. Submit before **{deadline}**

---

## Apply Now

**Official Link:** {official_link}

> Last verified by AdmitGoal: {datetime.now().strftime("%B %d, %Y")}

---

*Share this with a friend who is looking for scholarships.*
"""
    return blog, seo_title, seo_desc

def save(conn, data):
    if not data.get('title') or len(data['title']) < 10:
        return False
    if not data.get('scholarship_link'):
        return False
    if not data.get('deadline'):
        return False

    blog, seo_title, seo_desc = write_blog(data)

    degree_str = ", ".join(data['degree_levels']) if isinstance(data['degree_levels'], list) else str(data['degree_levels'])
    countries_str = ", ".join(data['eligible_countries']) if isinstance(data['eligible_countries'], list) else str(data['eligible_countries'])
    benefits_str = ", ".join(data['benefits']) if isinstance(data['benefits'], list) and data['benefits'] else ""

    lang_parts = []
    if data.get('ielts_score') and data['ielts_score'] != "Not required":
        lang_parts.append(f"IELTS {data['ielts_score']}")
    if data.get('pte_score'):
        lang_parts.append(f"PTE {data['pte_score']}")
    if data.get('toefl_score'):
        lang_parts.append(f"TOEFL {data['toefl_score']}")
    lang_str = " / ".join(lang_parts) if lang_parts else "No English test required"

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
              deadline=EXCLUDED.deadline,
              last_updated=EXCLUDED.last_updated,
              blog_post=EXCLUDED.blog_post,
              seo_title=EXCLUDED.seo_title,
              seo_description=EXCLUDED.seo_description,
              eligible_countries=EXCLUDED.eligible_countries
        ''', (
            data['scholarship_link'],
            data['title'],
            data.get('description', '')[:800],
            countries_str,
            "International students",
            degree_str,
            data['deadline'],
            lang_str,
            data.get('ielts_score', 'Not required'),
            benefits_str,
            f"Visit: {data['scholarship_link']}",
            blog,
            seo_title,
            seo_desc,
            data['university_name'],
            data['country'],
            data['region'],
            data['funding_type'],
            data.get('gpa_required', 'Check website'),
            datetime.now().strftime("%Y-%m-%d")
        ))
        cur.execute('''
            INSERT INTO scholarships
            (title, description, country, deadline, link, source, scraped_date)
            VALUES(%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (link) DO NOTHING
        ''', (
            data['title'],
            seo_desc,
            data['country'],
            data['deadline'],
            data['scholarship_link'],
            data['university_name'][:50],
            datetime.now().strftime("%Y-%m-%d")
        ))
        cur.close()
        return True
    except Exception as e:
        print(f"    DB Error: {e}")
        return False

def scrape_scholarship_page(url, source_is_aggregator, conn):
    r = fetch(url)
    if not r:
        return False

    soup = BeautifulSoup(r.text, 'lxml')
    for tag in soup.find_all(['nav', 'footer', 'script', 'style', 'aside', 'header']):
        tag.decompose()

    full_text = ' '.join(soup.get_text(separator=' ', strip=True).split())

    if not any(kw in full_text.lower() for kw in ['scholarship', 'fellowship', 'grant', 'award', 'funding', 'stipend']):
        return False

    if not is_open(full_text):
        return False

    # Extract title
    title = None
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text(strip=True)
    if not title:
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True).split('|')[0].split('–')[0].strip()

    if not title or len(title) < 10:
        return False

    # Skip list pages
    list_indicators = ['top 10', 'top 20', 'top 50', 'top 100', 'list of',
                       'best scholarships', '10 scholarships', '20 scholarships']
    if any(ind in title.lower() for ind in list_indicators):
        return False

    # Skip job listings
    if is_job_not_scholarship(title):
        print(f"    Skip (job listing): {title[:50]}")
        return False

    deadline = extract_deadline(full_text)
    if not deadline:
        return False

    # Get official link
    official_link = extract_official_link(soup, url, source_is_aggregator)
    if not official_link:
        if source_is_aggregator:
            print(f"    Skip (no official link found)")
            return False
        else:
            official_link = url

    # Don't save if official link is a PDF
    if official_link.lower().endswith('.pdf'):
        return False

    ielts = extract_ielts(full_text)
    pte = extract_pte(full_text)
    toefl = extract_toefl(full_text)
    gpa = extract_gpa(full_text)
    degree_levels = extract_degree(full_text)
    funding = extract_funding(full_text)
    eligible_countries = extract_eligible_countries(full_text)
    benefits = extract_benefits(full_text)

    parsed_official = urlparse(official_link)
    domain = parsed_official.netloc
    country = detect_country(domain, full_text)
    region = detect_region(country)

    uni_name = "Check official website"
    meta_site = soup.find('meta', {'property': 'og:site_name'})
    if meta_site:
        uni_name = meta_site.get('content', '')[:80]
    elif domain:
        uni_name = domain.replace('www.', '').replace('-', ' ').title()[:80]

    desc = ""
    for p in soup.find_all('p'):
        t = p.get_text(strip=True)
        if len(t) > 80:
            desc = t[:600]
            break
    if not desc:
        desc = full_text[:500]

    data = {
        'title': title,
        'description': desc,
        'university_name': uni_name,
        'country': country,
        'region': region,
        'degree_levels': degree_levels if degree_levels else ['All levels'],
        'deadline': deadline,
        'ielts_score': ielts,
        'pte_score': pte,
        'toefl_score': toefl,
        'gpa_required': gpa,
        'funding_type': funding,
        'eligible_countries': eligible_countries,
        'benefits': benefits or [],
        'scholarship_link': official_link,
    }

    return save(conn, data)

# ── SOURCES ───────────────────────────────────────────────
LISTING_PAGES = [
    # Aggregators — will follow external official links
    ("https://www.scholars4dev.com/", True),
    ("https://www.scholars4dev.com/page/2/", True),
    ("https://www.scholars4dev.com/page/3/", True),
    ("https://www.scholars4dev.com/page/4/", True),
    ("https://www.scholars4dev.com/page/5/", True),
    ("https://www.scholars4dev.com/page/6/", True),
    ("https://www.scholars4dev.com/page/7/", True),
    ("https://www.scholars4dev.com/page/8/", True),
    ("https://opportunitydesk.org/category/scholarships/", True),
    ("https://opportunitydesk.org/category/scholarships/page/2/", True),
    ("https://opportunitydesk.org/category/scholarships/page/3/", True),
    ("https://opportunitydesk.org/category/scholarships/page/4/", True),
    ("https://opportunitydesk.org/category/scholarships/page/5/", True),
    ("https://afterschoolafrica.com/scholarships/", True),
    ("https://afterschoolafrica.com/scholarships/page/2/", True),
    ("https://afterschoolafrica.com/scholarships/page/3/", True),
    ("https://scholarshipdb.net/scholarships-in-Germany?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-United-Kingdom?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-China?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-Turkey?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-South-Korea?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-Japan?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-Australia?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-Canada?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-Netherlands?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-Norway?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-Sweden?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-Finland?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-Hungary?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-France?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-Italy?page=1", True),
    ("https://scholarshipdb.net/scholarships-in-USA?page=1", True),

    # Official sources — use their own URL directly
    ("https://www.chevening.org/scholarships/", False),
    ("https://www.daad.de/en/study-and-research-in-germany/scholarships/", False),
    ("https://www.campuschina.org/scholarships/index.html", False),
    ("https://www.turkiyeburslari.gov.tr/en", False),
    ("https://stipendiumhungaricum.hu/en/", False),
    ("https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do", False),
    ("https://cscuk.fcdo.gov.uk/scholarships/", False),
    ("https://www.australiaawards.gov.au/scholarships", False),
    ("https://www.aauw.org/resources/programs/fellowships-grants/current-opportunities/international/", False),
    ("https://foreign.fulbrightonline.org/about/foreign-fulbright", False),
    ("https://www.vliruos.be/en/scholarships/", False),
    ("https://www.nuffic.nl/en/subjects/orange-knowledge-programme/", False),
]

def get_individual_links(listing_url, is_aggregator_source):
    r = fetch(listing_url)
    if not r:
        return []

    soup = BeautifulSoup(r.text, 'lxml')
    links = []
    seen = set()

    parsed = urlparse(listing_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    listing_domain = parsed.netloc.replace('www.', '')

    skip_patterns = [
        '/category/', '/tag/', '/page/', '/author/', '#',
        'javascript', 'mailto', 'facebook', 'twitter',
        'instagram', 'linkedin', 'youtube',
        '/about', '/contact', '/privacy', '/terms',
        'search', 'login', 'register', 'signup', '.pdf', '.doc'
    ]

    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)

        if href.startswith('/'):
            href = base + href
        elif not href.startswith('http'):
            continue

        if any(skip in href.lower() for skip in skip_patterns):
            continue

        if href == listing_url or href == listing_url.rstrip('/'):
            continue

        href_domain = urlparse(href).netloc.replace('www.', '')

        if is_aggregator_source:
            # For aggregators: only follow same-domain links (their article pages)
            if href_domain == listing_domain:
                path = urlparse(href).path
                if len(path.split('/')) >= 2 and len(text) > 15:
                    if href not in seen:
                        seen.add(href)
                        links.append(href)
        else:
            # For official sources: follow same-domain links
            if href_domain == listing_domain:
                path = urlparse(href).path
                if len(path.split('/')) >= 2 and len(text) > 10:
                    if href not in seen:
                        seen.add(href)
                        links.append(href)

    return links[:25]

if __name__ == "__main__":
    print("=" * 60)
    print("  ADMITGOAL MASTER SCRAPER v4.0")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Sources: {len(LISTING_PAGES)} listing pages")
    print(f"  Mode: Official links only, no job listings")
    print("=" * 60)

    conn = get_db()
    total_saved = 0
    total_skipped = 0

    for listing_url, is_agg in LISTING_PAGES:
        parsed = urlparse(listing_url)
        source_type = "AGGREGATOR" if is_agg else "OFFICIAL"
        print(f"\n[{source_type}] {parsed.netloc}")
        print(f"  URL: {listing_url}")

        individual_links = get_individual_links(listing_url, is_agg)
        print(f"  Found {len(individual_links)} individual links")

        for link in individual_links:
            print(f"\n  Checking: {link[:70]}")
            try:
                saved = scrape_scholarship_page(link, is_agg, conn)
                if saved:
                    print(f"  SAVED")
                    total_saved += 1
                else:
                    print(f"  Skipped")
                    total_skipped += 1
            except Exception as e:
                print(f"  Error: {e}")
                total_skipped += 1

            time.sleep(random.uniform(2, 4))

        time.sleep(random.uniform(3, 6))

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scholarship_details")
    db_total = cur.fetchone()[0]
    cur.close()
    conn.close()

    print(f"\n{'=' * 60}")
    print(f"  DONE!")
    print(f"  Saved      : {total_saved}")
    print(f"  Skipped    : {total_skipped}")
    print(f"  Total in DB: {db_total}")
    print(f"{'=' * 60}")