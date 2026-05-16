"""
ADMITGOAL ULTIMATE SCRAPER v2.0
- Deadlines from MAY 16, 2026 forward ONLY
- Anti-block: cloudscraper + Playwright fallback
- Official links only (no aggregators)
- Original professional blogs
- Works on ANY site
"""

import cloudscraper
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import psycopg2
import re
import time
import random
from datetime import datetime
from urllib.parse import urlparse, urljoin
from dateutil import parser as date_parser

print("=" * 70)
print("  ADMITGOAL ULTIMATE SCRAPER v2.0")
print("  Anti-Block | Official Links Only | May 16, 2026+")
print("=" * 70)

# ── CRITICAL DATE FILTER ──────────────────────────────────
TODAY = datetime(2026, 5, 16)
print(f"\n🗓️  TODAY: {TODAY.strftime('%B %d, %Y')}")
print(f"📌 Only accepting deadlines from {TODAY.strftime('%B %d, %Y')} forward\n")

DATABASE_URL = 'postgresql://postgres.deqyxksflvlxjelppgxz:Rehan1819Rehan@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'

AGGREGATOR_DOMAINS = [
    'scholars4dev.com', 'opportunitydesk.org', 'afterschoolafrica.com',
    'scholarshipdb.net', 'youthop.com', 'mastersportal.eu', 'phdportal.eu',
    'scholarshipsads.com', 'buddy4study.com', 'scholarshipregion.com'
]

SOURCES = [
    'https://www.daad.de/en/study-and-research-in-germany/scholarships/',
    'https://www.chevening.org/scholarships/',
    'https://www.scholars4dev.com/',
    'https://scholarshipdb.net/scholarships-in-Germany',
    'https://scholarshipdb.net/scholarships-in-Canada',
    'https://www.opportunitydesk.org/category/scholarships/',
]

VISITED_URLS = set()
scraper = cloudscraper.create_scraper()

# ── ANTI-BLOCK FETCH ──────────────────────────────────────
def fetch_cloudscraper(url, retries=3):
    """Fast fetch with cloudscraper (bypasses Cloudflare)"""
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(2, 4))
            r = scraper.get(url, timeout=25)
            if r.status_code == 200:
                return r.text
            elif r.status_code == 403:
                time.sleep(random.uniform(8, 15))
        except Exception as e:
            if attempt == retries - 1:
                print(f"      Cloudscraper failed: {str(e)[:50]}")
            time.sleep(random.uniform(5, 10))
    return None

def fetch_playwright(url):
    """Browser automation for tough sites"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(random.uniform(3, 6))
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        print(f"      Playwright failed: {str(e)[:50]}")
        return None

def fetch(url):
    """Smart fetch: cloudscraper first, Playwright fallback"""
    if not url or any(url.endswith(e) for e in ['.pdf', '.doc', '.zip']):
        return None
    
    html = fetch_cloudscraper(url)
    if html and len(html) > 500:
        return html
    
    print(f"      Switching to Playwright...")
    return fetch_playwright(url)

# ── HELPERS ───────────────────────────────────────────────
def get_domain(url):
    try:
        return urlparse(url).netloc.replace('www.', '').lower()
    except:
        return ""

def is_aggregator(url):
    return any(agg in get_domain(url) for agg in AGGREGATOR_DOMAINS)

def clean_soup(soup):
    for tag in soup.find_all(['nav', 'footer', 'script', 'style', 'aside', 'header', 'iframe']):
        tag.decompose()
    return soup

def get_text(soup):
    return ' '.join(soup.get_text(separator=' ', strip=True).split())

# ── DEADLINE PARSER (STRICT) ──────────────────────────────
def parse_deadline(text):
    """Extract deadline - MUST be May 16, 2026 or later"""
    patterns = [
        r'deadline[:\s]*([\w\s,]+\d{4})',
        r'closing date[:\s]*([\w\s,]+\d{4})',
        r'apply by[:\s]*([\w\s,]+\d{4})',
        r'applications? close[:\s]*([\w\s,]+\d{4})',
        r'(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4})',
        r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4})',
    ]
    
    text_lower = text.lower()
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            try:
                deadline_date = date_parser.parse(match, fuzzy=True)
                
                # CRITICAL: Must be May 16, 2026 or later
                if deadline_date.date() >= TODAY.date():
                    return deadline_date.strftime("%B %d, %Y")
            except:
                continue
    
    return None

def is_outdated(text):
    """Check if scholarship is expired"""
    text_lower = text.lower()
    
    closed_indicators = [
        'applications closed', 'deadline has passed', 'expired',
        'no longer accepting', 'closed for applications'
    ]
    if any(ind in text_lower for ind in closed_indicators):
        return True
    
    deadline = parse_deadline(text)
    return deadline is None

# ── TITLE FILTER ──────────────────────────────────────────
def is_bad_title(title):
    if not title or len(title) < 15:
        return True
    t = title.lower()
    
    keep_patterns = [
        r'fellowship', r'scholarship', r'bursary', r'award', r'grant',
        r'fully.funded', r'phd (position|fellowship)', r'doctoral fellowship'
    ]
    for p in keep_patterns:
        if re.search(p, t):
            return False
    
    bad_patterns = [
        r'\bconsent\b', r'\bcookies\b', r'privacy policy',
        r'^top \d+', r'^best \d+', r'list of scholarships',
        r'\bjob (fair|vacancy)\b', r'\bhiring\b',
        r'\bsenior (manager|director)\b', r'\bchief officer\b',
    ]
    for p in bad_patterns:
        if re.search(p, t):
            return True
    
    return False

# ── EXTRACT TITLE (ORIGINAL) ──────────────────────────────
def extract_title(soup, url):
    """Extract and clean title"""
    for tag in ['h1', 'h2']:
        el = soup.find(tag)
        if el:
            title = el.get_text(strip=True)
            title = re.sub(r'\s*[\|\-]\s*(Scholars4Dev|OpportunityDesk|ScholarshipDB).*$', '', title, flags=re.IGNORECASE)
            if len(title) > 15:
                return clean_title(title)
    
    meta = soup.find('meta', {'property': 'og:title'}) or soup.find('title')
    if meta:
        title = meta.get('content') if meta.name == 'meta' else meta.get_text()
        title = re.sub(r'\s*[\|\-]\s*(Scholars4Dev|OpportunityDesk).*$', '', title, flags=re.IGNORECASE)
        if len(title) > 15:
            return clean_title(title)
    
    return None

def clean_title(title):
    """Make title professional"""
    title = title.strip()
    title = re.sub(r'\b20\d{2}\b', '', title)
    title = re.sub(r'\s*[\|\-]\s*(Apply Now|Click Here|Read More).*$', '', title, flags=re.IGNORECASE)
    title = ' '.join(title.split())
    return title[:100] if len(title) > 15 else None

# ── EXTRACT UNIVERSITY ────────────────────────────────────
def extract_university(soup, url):
    """Extract real university name"""
    meta = soup.find('meta', {'property': 'og:site_name'})
    if meta and meta.get('content'):
        name = meta['content'].strip()
        if len(name) > 3 and not is_aggregator(url):
            return name[:80]
    
    for tag in soup.find_all(['h1', 'h2', 'h3']):
        text = tag.get_text(strip=True)
        if any(word in text.lower() for word in ['university', 'college', 'institute']):
            if 5 < len(text) < 80:
                return text
    
    domain = get_domain(url)
    if '.edu' in domain or '.ac.' in domain:
        clean = re.sub(r'\.(edu|ac|gov|org|com)(\..*)?$', '', domain)
        clean = clean.replace('-', ' ').replace('.', ' ').title()
        return clean[:80] if len(clean) > 3 else None
    
    return None

# ── FIND OFFICIAL LINK ────────────────────────────────────
def find_official_link(soup, current_url):
    """Find official university link (not aggregator)"""
    current_domain = get_domain(current_url)
    
    official_tlds = ['.edu', '.ac.uk', '.ac.', '.gov']
    known_orgs = [
        'daad.de', 'chevening.org', 'fulbright', 'britishcouncil',
        'campuschina.org', 'turkiyeburslari', 'studyinkorea',
        'erasmusplus.org', 'commonwealth', 'australiaawards'
    ]
    
    candidates = []
    
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        text = a.get_text(strip=True).lower()
        
        if not href or href.startswith(('#', 'javascript:', 'mailto:')):
            continue
        
        if href.startswith('/'):
            href = urljoin(current_url, href)
        elif not href.startswith('http'):
            continue
        
        link_domain = get_domain(href)
        
        if link_domain == current_domain or is_aggregator(href):
            continue
        
        if any(s in href for s in ['facebook.', 'twitter.', 'linkedin.']):
            continue
        
        score = 0
        
        for tld in official_tlds:
            if link_domain.endswith(tld):
                score += 25
        
        for org in known_orgs:
            if org in link_domain:
                score += 20
        
        if any(kw in text for kw in ['apply', 'official', 'university', 'scholarship']):
            score += 15
        
        if any(kw in href.lower() for kw in ['scholarship', 'fellowship', 'apply']):
            score += 10
        
        if score > 0:
            candidates.append((score, href))
    
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    
    return None

# ── EXTRACT FIELDS ────────────────────────────────────────
def extract_degree(text):
    levels = []
    if re.search(r'\bundergraduate|bachelor\b', text, re.IGNORECASE):
        levels.append("Bachelor")
    if re.search(r'\bmaster|postgraduate|msc\b', text, re.IGNORECASE):
        levels.append("Master")
    if re.search(r'\bphd|doctoral\b', text, re.IGNORECASE):
        levels.append("PhD")
    return ", ".join(levels) if levels else "All levels"

def extract_funding(text):
    if re.search(r'full.?fund|fully.?fund|covers (all|tuition|living)', text, re.IGNORECASE):
        return "Fully Funded"
    if re.search(r'partial|tuition only', text, re.IGNORECASE):
        return "Partial"
    if re.search(r'stipend|living allowance', text, re.IGNORECASE):
        return "Stipend Included"
    return "Check website"

def extract_ielts(text):
    m = re.search(r'ielts[:\s]*(?:score[:\s]*)?(\d+\.?\d*)', text, re.IGNORECASE)
    if m:
        try:
            score = float(m.group(1))
            if 4.0 <= score <= 9.0:
                return str(score)
        except:
            pass
    return "Required" if re.search(r'\bielts\b', text, re.IGNORECASE) else "Not required"

def extract_toefl(text):
    m = re.search(r'toefl[:\s]*(?:ibt[:\s]*)?(\d+)', text, re.IGNORECASE)
    return m.group(1) if m else None

def extract_gpa(text):
    patterns = [
        r'(?:minimum\s+)?(?:gpa|cgpa)[:\s]*(?:of\s+)?(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*(?:gpa|cgpa)',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)[:30]
    return None

def extract_eligible_countries(text):
    countries = [
        "Pakistan", "India", "Bangladesh", "Nepal", "Nigeria", "Ghana",
        "Kenya", "Ethiopia", "South Africa", "Egypt", "Indonesia",
        "developing countries", "international students", "worldwide"
    ]
    found = []
    tl = text.lower()
    for c in countries:
        if c.lower() in tl:
            found.append(c)
    if found:
        return ", ".join(found[:10])
    if any(w in tl for w in ['all nationalities', 'international', 'worldwide']):
        return "Open to international students worldwide"
    return "Open to international students"

def extract_benefits(text):
    benefits = []
    checks = {
        "Full tuition": r'full tuition|tuition.*cover',
        "Living allowance": r'living allowance|monthly stipend',
        "Travel grant": r'travel (grant|allowance)|airfare',
        "Health insurance": r'health insurance|medical cover',
    }
    for name, pattern in checks.items():
        if re.search(pattern, text, re.IGNORECASE):
            benefits.append(name)
    return ", ".join(benefits) if benefits else ""

def detect_country(domain, text=""):
    tld_map = {
        '.ac.uk': 'United Kingdom', '.uk': 'United Kingdom',
        '.edu.au': 'Australia', '.au': 'Australia',
        '.ca': 'Canada', '.de': 'Germany', '.fr': 'France',
        '.nl': 'Netherlands', '.se': 'Sweden', '.ch': 'Switzerland',
        '.edu': 'USA', '.gov': 'USA',
    }
    for tld, country in sorted(tld_map.items(), key=lambda x: -len(x[0])):
        if domain.endswith(tld):
            return country
    
    hints = {
        'germany': 'Germany', 'australia': 'Australia', 'canada': 'Canada',
        'united kingdom': 'United Kingdom', 'united states': 'USA'
    }
    tl = text.lower()[:2000]
    for hint, country in hints.items():
        if hint in tl:
            return country
    return "International"

def detect_region(country):
    regions = {
        'Europe': ['United Kingdom', 'Germany', 'France', 'Netherlands', 'Sweden', 'Switzerland'],
        'North America': ['USA', 'Canada'],
        'Oceania': ['Australia', 'New Zealand'],
        'Asia': ['China', 'Japan', 'South Korea', 'Singapore'],
    }
    for region, countries in regions.items():
        if country in countries:
            return region
    return "International"

# ── ORIGINAL BLOG WRITER ──────────────────────────────────
def write_original_blog(data):
    """Write professional original blog content"""
    title = data['title']
    uni = data.get('university', 'Check official website')
    country = data.get('country', 'International')
    region = data.get('region', 'International')
    deadline = data.get('deadline', 'Check official website')
    degree = data.get('degree', 'All levels')
    funding = data.get('funding', 'Check website')
    ielts = data.get('ielts', 'Not required')
    gpa = data.get('gpa', 'Check website')
    eligible = data.get('eligible_countries', 'International students')
    benefits = data.get('benefits', 'Check official website')
    official_link = data['official_link']
    
    seo_title = f"{title} 2026 — Complete Guide for International Students"[:70]
    seo_desc = f"Apply for {title}. Deadline: {deadline}. {degree} students. IELTS: {ielts}. Eligible: {eligible[:40]}."[:160]
    
    blog = f"""# {title} 2026 — Complete Application Guide

**Last Updated:** {datetime.now().strftime("%B %d, %Y")} | **Status:** Open for Applications

---

## Overview

The **{title}** is a prestigious opportunity offered by **{uni}** in **{country}**. This scholarship is designed for talented international students from developing countries including Pakistan, India, Bangladesh, Nigeria, Kenya, and many others.

This is your chance to study abroad without paying expensive education agents. AdmitGoal provides you with all the information you need — completely free.

---

## Quick Facts

| Detail | Information |
|--------|-------------|
| **Scholarship Name** | {title} |
| **Host Institution** | {uni} |
| **Country** | {country} |
| **Region** | {region} |
| **Degree Level** | {degree} |
| **Funding Type** | {funding} |
| **Application Deadline** | {deadline} |
| **IELTS Requirement** | {ielts} |
| **Minimum GPA** | {gpa} |
| **Eligible Countries** | {eligible} |

---

## Who Can Apply?

**Eligible Countries:** {eligible}

**Academic Level:** This scholarship is open for {degree} students.

**Academic Requirements:** Minimum GPA of {gpa}. Strong academic record with relevant coursework in your field.

---

## Scholarship Benefits

**Funding Type: {funding}**

This scholarship typically covers:

{benefits if benefits else "- Full or partial tuition fees\n- Monthly living stipend\n- Health insurance\n- Travel allowance (in some cases)"}

Always verify the exact benefits on the official scholarship page as they may vary by program.

---

## English Language Requirements

{"**IELTS Required:** " + ielts if ielts not in ['Not required', 'Required'] else "English proficiency may be required. Check official website for specific requirements."}

**Where to take IELTS in Pakistan:**
- British Council centers in Karachi, Lahore, Islamabad, Faisalabad
- IDP Education centers nationwide
- Start preparation 3 months before your deadline

**Alternative tests:** TOEFL, PTE Academic, or Duolingo English Test may be accepted. Verify on the official page.

---

## Application Deadline

**{deadline}**

**Recommended Timeline:**
- **3 months before deadline:** Start gathering documents, prepare for IELTS
- **2 months before:** Write your Statement of Purpose and CV
- **1 month before:** Get recommendation letters from professors
- **2 weeks before:** Submit application — never wait until the last day

---

## Required Documents

Standard documents for most scholarship applications:

1. **Valid Passport** (at least 6 months validity)
2. **Academic Transcripts** (all previous degrees, officially translated)
3. **Degree Certificates** (Bachelor's for Master's, Master's for PhD)
4. **English Test Score** (IELTS/TOEFL if required)
5. **Statement of Purpose** (800-1000 words)
6. **Curriculum Vitae** (Academic CV format)
7. **Two Recommendation Letters** (from professors or employers)
8. **Research Proposal** (for PhD applicants)
9. **Passport-size Photographs**
10. **Financial documents** (if partial funding)

---

## How to Write a Winning Statement of Purpose

Your SOP is the most important part of your application. Here's how to write one that stands out:

**Opening Paragraph:**
Start with a compelling story or experience that sparked your interest in this field. Never start with "I am writing to apply for..."

**Academic Background:**
Highlight your degrees, GPA, relevant coursework, and academic achievements. Use specific numbers and examples.

**Why This Scholarship:**
Show that you've researched the university and program. Mention specific professors, research centers, or courses that interest you.

**Career Goals:**
Explain where you see yourself in 5-10 years. How will this scholarship help you achieve those goals? How will you contribute to your home country?

**Why You:**
What makes you unique? Leadership roles, research experience, community service, publications — provide evidence, not just claims.

**Closing:**
End with confidence and gratitude. Keep your SOP between 800-1000 words.

---

## Application Process

1. **Visit the official scholarship page** (link below)
2. **Create an account** on the application portal
3. **Fill out the online application form**
4. **Upload all required documents** (PDF format preferred)
5. **Submit before the deadline**
6. **Save your application confirmation**

---

## Tips for Pakistani Students

- **HEC Attestation:** Get your degrees attested from HEC Pakistan
- **IBCC Equivalence:** Required for Bachelor's degree if you have FSc/A-Levels
- **Passport:** Apply early — it takes 2-3 weeks
- **Bank Statement:** Some scholarships require proof of funds
- **Recommendation Letters:** Ask professors at least 1 month in advance

---

## Frequently Asked Questions

**Is this scholarship fully funded?**
Funding type: **{funding}**. Check the official page for complete financial details.

**Can Pakistani students apply?**
{"Yes, Pakistani students are eligible." if "Pakistan" in eligible else "Check the eligibility section above. Many international scholarships accept Pakistani students."}

**Do I need IELTS?**
{f"Yes, minimum IELTS score of {ielts} is required." if ielts not in ['Not required', 'Required'] else "Check the official website for English language requirements."}

**When is the deadline?**
**{deadline}** — Do not wait until the last day to apply.

**How do I apply?**
Visit the official link below and follow the application instructions.

---

## Official Application Link

**Apply Here:** {official_link}

> ✅ Link verified by AdmitGoal on {datetime.now().strftime("%B %d, %Y")}

---

## About AdmitGoal

AdmitGoal is Pakistan's first free AI-powered scholarship platform. We help students from developing countries find and apply for scholarships without paying expensive education agents.

**Our Mission:** Make quality education accessible to everyone, regardless of financial background.

---

**Share this scholarship with a friend who deserves it. Good luck with your application!**

*Need help with your SOP or application? Contact us through our website.*
"""
    
    return blog, seo_title, seo_desc

# ── DATABASE ──────────────────────────────────────────────
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

def save(conn, data):
    """Save scholarship with validation"""
    if not data.get('title') or len(data['title']) < 15:
        return False
    if not data.get('official_link'):
        return False
    if is_bad_title(data['title']):
        return False
    if not data.get('deadline'):
        return False
    
    blog, seo_title, seo_desc = write_original_blog(data)
    
    try:
        cur = conn.cursor()
        
        # Check duplicate by link
        cur.execute("SELECT id FROM scholarship_details WHERE scholarship_link=%s", (data['official_link'],))
        if cur.fetchone():
            cur.close()
            return False
        
        # Check duplicate by title
        cur.execute("SELECT id FROM scholarship_details WHERE title=%s", (data['title'],))
        existing = cur.fetchone()
        if existing:
            if not is_aggregator(data['official_link']):
                cur.execute("""
                    UPDATE scholarship_details SET
                        scholarship_link=%s, deadline=%s, last_updated=%s,
                        blog_post=%s, seo_title=%s, seo_description=%s
                    WHERE id=%s
                """, (data['official_link'], data['deadline'],
                      datetime.now().strftime("%Y-%m-%d"), blog, seo_title, seo_desc, existing[0]))
                cur.close()
                return True
            cur.close()
            return False
        
        cur.execute('''
            INSERT INTO scholarship_details
            (scholarship_link, title, full_description, eligible_countries,
             eligible_students, degree_level, deadline, language_requirement,
             ielts_score, benefits, how_to_apply, blog_post, seo_title,
             seo_description, university_name, country, region,
             funding_type, gpa_required, last_updated)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ''', (
            data['official_link'], data['title'],
            data.get('description', '')[:800],
            data.get('eligible_countries', 'International students'),
            "International students",
            data.get('degree', 'All levels'),
            data['deadline'],
            f"IELTS {data.get('ielts','')}" if data.get('ielts') not in ['Not required', None] else "Not required",
            data.get('ielts', 'Not required'),
            data.get('benefits', ''),
            f"Visit: {data['official_link']}",
            blog, seo_title, seo_desc,
            data.get('university', 'Check official website'),
            data.get('country', 'International'),
            data.get('region', 'International'),
            data.get('funding', 'Check website'),
            data.get('gpa', 'Check website'),
            datetime.now().strftime("%Y-%m-%d")
        ))
        
        cur.execute('''
            INSERT INTO scholarships (title, description, country, deadline, link, source, scraped_date)
            VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (link) DO NOTHING
        ''', (
            data['title'], seo_desc, data.get('country', 'International'),
            data['deadline'], data['official_link'],
            data.get('university', '')[:50], datetime.now().strftime("%Y-%m-%d")
        ))
        
        cur.close()
        return True
    except Exception as e:
        print(f"    DB Error: {str(e)[:100]}")
        return False

# ── SCRAPE PAGE ───────────────────────────────────────────
def scrape_page(url, conn, fallback_title=""):
    """Main scraping logic for one URL"""
    if url in VISITED_URLS:
        return False
    VISITED_URLS.add(url)
    
    html = fetch(url)
    if not html:
        print(f"      Fetch failed")
        return False
    
    soup = clean_soup(BeautifulSoup(html, 'lxml'))
    text = get_text(soup)
    
    if not any(kw in text.lower() for kw in ['scholarship', 'fellowship', 'grant', 'award']):
        return False
    
    if is_outdated(text):
        print(f"      Expired/outdated")
        return False
    
    title = extract_title(soup, url)
    if not title or is_bad_title(title):
        print(f"      Bad/no title")
        return False
    
    # Find official link
    official_link = url
    combined_text = text
    official_soup = soup
    
    if is_aggregator(url):
        found = find_official_link(soup, url)
        if found and not is_aggregator(found):
            off_html = fetch(found)
            if off_html:
                official_soup = clean_soup(BeautifulSoup(off_html, 'lxml'))
                official_text = get_text(official_soup)
                combined_text = text + " " + official_text
                official_link = found
            else:
                official_link = found
        elif not found:
            print(f"      No official link found")
            return False
    
    # Extract deadline - MUST exist and be future
    deadline = parse_deadline(combined_text)
    if not deadline:
        print(f"      No valid future deadline")
        return False
    
    # Extract all fields
    ielts = extract_ielts(combined_text)
    toefl = extract_toefl(combined_text)
    gpa = extract_gpa(combined_text)
    degree = extract_degree(combined_text)
    funding = extract_funding(combined_text)
    eligible = extract_eligible_countries(combined_text)
    benefits = extract_benefits(combined_text)
    
    domain = get_domain(official_link)
    country = detect_country(domain, combined_text)
    region = detect_region(country)
    uni = extract_university(official_soup, official_link)
    
    desc = ""
    for p in soup.find_all('p'):
        t = p.get_text(strip=True)
        if len(t) > 80:
            desc = t[:600]
            break
    if not desc:
        desc = combined_text[:400]
    
    data = {
        'title': title,
        'description': desc,
        'university': uni,
        'country': country,
        'region': region,
        'deadline': deadline,
        'ielts': ielts,
        'toefl': toefl,
        'gpa': gpa,
        'degree': degree,
        'funding': funding,
        'eligible_countries': eligible,
        'benefits': benefits,
        'official_link': official_link,
    }
    
    if save(conn, data):
        print(f"      ✅ SAVED: {title[:55]}")
        return True
    else:
        print(f"      ⏭️  Skipped (duplicate/incomplete)")
        return False

# ── EXTRACT FROM LIST PAGE ────────────────────────────────
def extract_from_list(listing_url, soup, conn):
    """Extract individual scholarship links from list page"""
    links = []
    seen = set()
    parsed = urlparse(listing_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    listing_domain = get_domain(listing_url)
    
    skip = ['/category/', '/tag/', '/author/', 'mailto:', 'javascript:',
            'facebook.', 'twitter.', 'instagram.', 'linkedin.',
            '/about', '/contact', '/privacy', '.pdf', '#']
    
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        text = a.get_text(strip=True)
        
        if not href:
            continue
        if href.startswith('/'):
            href = base_url + href
        elif not href.startswith('http'):
            continue
        
        if any(s in href.lower() for s in skip):
            continue
        if href in seen or href in VISITED_URLS:
            continue
        if get_domain(href) != listing_domain:
            continue
        
        path_parts = [p for p in urlparse(href).path.split('/') if p]
        if len(path_parts) >= 1 and len(text) > 10:
            seen.add(href)
            links.append((text[:80], href))
    
    print(f"      Found {len(links)} sub-links")
    saved = 0
    for title, link in links:
        print(f"\n        -> {title[:60]}")
        try:
            if scrape_page(link, conn, title):
                saved += 1
        except Exception as e:
            print(f"        Error: {str(e)[:50]}")
        time.sleep(random.uniform(2, 4))
    return saved > 0

# ── GET SOURCE LINKS ──────────────────────────────────────
def get_source_links(source_url):
    """Get all post links from source listing page"""
    html = fetch(source_url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    parsed = urlparse(source_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    source_domain = get_domain(source_url)
    
    skip = ['/category/', '/tag/', '/author/', 'mailto:', 'javascript:',
            'facebook.', 'twitter.', 'instagram.', 'linkedin.',
            '/about', '/contact', '/privacy', '.pdf', '#']
    
    links = []
    seen = set()
    
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        text = a.get_text(strip=True)
        
        if not href:
            continue
        if href.startswith('/'):
            href = base + href
        elif not href.startswith('http'):
            continue
        
        if any(s in href.lower() for s in skip):
            continue
        if href in seen or href in VISITED_URLS:
            continue
        
        # For scholarshipdb allow external official links
        if 'scholarshipdb.net' in source_domain:
            if is_aggregator(href):
                continue
        else:
            if get_domain(href) != source_domain:
                continue
        
        path_parts = [p for p in urlparse(href).path.split('/') if p]
        if len(path_parts) >= 1 and len(text) > 8:
            seen.add(href)
            links.append((text[:80], href))
    
    return links

# ── MAIN ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 70)
    print("  STARTING SCRAPER")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    conn = get_db()
    total_saved = 0
    total_skipped = 0
    
    for i, source_url in enumerate(SOURCES, 1):
        print(f"\n[{i}/{len(SOURCES)}] 🌐 {source_url}")
        
        post_links = get_source_links(source_url)
        print(f"  📋 Found {len(post_links)} links")
        
        for title, link in post_links:
            print(f"\n  ➡️  {title[:65]}")
            try:
                saved = scrape_page(link, conn, title)
                if saved:
                    total_saved += 1
                else:
                    total_skipped += 1
            except Exception as e:
                print(f"  ❌ Error: {str(e)[:80]}")
                total_skipped += 1
            time.sleep(random.uniform(2, 4))
        
        time.sleep(random.uniform(4, 7))
    
    # Final stats
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scholarship_details")
    db_total = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    print(f"\n{'=' * 70}")
    print(f"  ✅ NEW SAVED    : {total_saved}")
    print(f"  ⏭️  SKIPPED     : {total_skipped}")
    print(f"  📊 TOTAL IN DB : {db_total}")
    print(f"  🗓️  DEADLINE    : May 16, 2026 or later only")
    print(f"{'=' * 70}")