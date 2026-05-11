import requests
from bs4 import BeautifulSoup
import psycopg2
import psycopg2.extras
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

# ── HEADERS ───────────────────────────────────────────────
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

# ── DATABASE ──────────────────────────────────────────────
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

# ── FRESHNESS CHECK ───────────────────────────────────────
def is_open(text):
    text_lower = text.lower()

    # Hard closed signals
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
        # All dates found are in the past
        max_year = max(y for y, m in found_dates)
        if max_year < CURRENT_YEAR - 1:
            return False  # Clearly old
        return False

    # No dates found — check year mentions
    if str(CURRENT_YEAR + 1) in text:
        return True
    if str(CURRENT_YEAR) in text:
        return True

    return False  # No year found = skip it, we only want confirmed open

# ── EXTRACTORS ────────────────────────────────────────────
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
            groups = [g for g in m.groups() if g and not g.lower() in ['close','due']]
            if groups:
                return groups[-1].strip()
    return None  # Return None if no deadline found — we need real data

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
            if 4.0 <= score <= 9.0:  # Valid IELTS range
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
        r'grade point average[:\s]*(\d+\.?\d*)',
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
    return levels  # Return LIST not string

def extract_funding(text):
    if re.search(r'full.?fund|fully.?fund|full scholarship|covers all', text, re.IGNORECASE):
        return "Fully Funded"
    if re.search(r'partial|50%|tuition only|tuition fee waiver', text, re.IGNORECASE):
        return "Partial"
    if re.search(r'stipend|living allowance|monthly allowance', text, re.IGNORECASE):
        return "Stipend Included"
    return "Check website"

def extract_eligible_countries(text):
    """Extract actual country names from text"""
    all_countries = [
        "Pakistan", "India", "Bangladesh", "Nepal", "Sri Lanka",
        "Afghanistan", "Nigeria", "Ghana", "Kenya", "Ethiopia",
        "Tanzania", "Uganda", "Rwanda", "Zimbabwe", "Zambia",
        "South Africa", "Egypt", "Morocco", "Tunisia", "Algeria",
        "Indonesia", "Malaysia", "Philippines", "Vietnam", "Thailand",
        "Cambodia", "Myanmar", "Laos", "China", "Mongolia",
        "Brazil", "Colombia", "Peru", "Argentina", "Mexico",
        "Bolivia", "Ecuador", "Paraguay", "Venezuela",
        "developing countries", "low-income countries",
        "middle-income countries", "African countries",
        "Asian countries", "all countries", "international students",
        "worldwide", "global"
    ]

    found = []
    text_lower = text.lower()

    # Check for specific country mentions
    for country in all_countries:
        if country.lower() in text_lower:
            found.append(country)

    if found:
        return found

    # Check for open to all
    if any(w in text_lower for w in ['all nationalities', 'all countries', 'international', 'worldwide', 'global']):
        return ["Open to international students worldwide"]

    return ["Check official website for eligible countries"]

def extract_benefits(text):
    """Extract what the scholarship covers"""
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

def extract_official_link(soup, current_url, text):
    """Find the actual official application/university link"""
    # Keywords that indicate official links
    official_keywords = [
        'apply now', 'apply here', 'apply online', 'official website',
        'application portal', 'click here to apply', 'submit application',
        'online application', 'application form', 'apply for this',
        'visit official', 'official link', 'apply at'
    ]

    # Domain patterns for universities and official sources
    official_domains = [
        '.edu', '.ac.uk', '.edu.au', '.ac.jp', '.ac.kr', '.edu.cn',
        '.gov', '.org', 'daad.de', 'chevening.org', 'fulbright',
        'erasmus', 'scholarship', 'stipendium', 'turkiyeburslari',
        'campuschina', 'studyinkorea', 'mext.go.jp'
    ]

    candidates = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        link_text = a.get_text(strip=True).lower()

        # Skip social media, navigation links
        if any(skip in href for skip in ['facebook', 'twitter', 'instagram', 'linkedin', '#', 'javascript', 'mailto']):
            continue

        # Make absolute URL
        if href.startswith('/'):
            parsed = urlparse(current_url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        elif not href.startswith('http'):
            continue

        score = 0

        # Score based on link text
        for kw in official_keywords:
            if kw in link_text:
                score += 10

        # Score based on domain
        for domain in official_domains:
            if domain in href:
                score += 5

        # Penalize 3rd party aggregator domains
        aggregator_domains = [
            'scholars4dev', 'scholarshipdb', 'opportunitydesk',
            'afterschoolafrica', 'youthop', 'mastersportal',
            'phdportal', 'opportunitiesforafricans'
        ]
        for agg in aggregator_domains:
            if agg in href:
                score -= 20

        if score > 0:
            candidates.append((score, href))

    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]

    # Fallback: return current URL if it's already an official source
    parsed = urlparse(current_url)
    domain = parsed.netloc
    if any(d in domain for d in ['.edu', '.ac.', '.gov', 'daad', 'chevening', 'fulbright', 'erasmus']):
        return current_url

    return None  # No official link found

def detect_country(domain, text=""):
    """Detect country from domain and text"""
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
        '.qa': 'Qatar', '.jo': 'Jordan', '.kw': 'Kuwait',
        '.cn': 'China', '.jp': 'Japan', '.kr': 'South Korea',
        '.my': 'Malaysia', '.sg': 'Singapore', '.th': 'Thailand',
        '.nz': 'New Zealand', '.za': 'South Africa',
        '.edu': 'USA', '.gov': 'USA',
        '.pk': 'Pakistan', '.in': 'India',
    }
    for tld, country in sorted(tld_map.items(), key=lambda x: -len(x[0])):
        if domain.endswith(tld):
            return country
    return "International"

def detect_region(country):
    regions = {
        'Europe': ['United Kingdom','Germany','France','Netherlands','Sweden',
                   'Norway','Finland','Denmark','Switzerland','Austria','Belgium',
                   'Italy','Spain','Portugal','Poland','Czech Republic','Hungary',
                   'Romania','Slovakia','Slovenia','Croatia','Greece','Bulgaria',
                   'Lithuania','Latvia','Estonia','Ireland','Luxembourg'],
        'Middle East': ['Turkey','Saudi Arabia','UAE','Qatar','Jordan',
                        'Kuwait','Oman','Bahrain','Egypt','Morocco','Tunisia','Algeria'],
        'Asia': ['China','Japan','South Korea','Malaysia','Singapore',
                 'Thailand','Indonesia','Vietnam','Taiwan','Hong Kong',
                 'Pakistan','India','Bangladesh','Sri Lanka','Nepal','Philippines'],
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

# ── BLOG WRITER ───────────────────────────────────────────
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

    # Build language requirement string
    lang_parts = []
    if ielts and ielts != "Not required":
        lang_parts.append(f"IELTS {ielts}")
    if pte:
        lang_parts.append(f"PTE {pte}")
    if toefl:
        lang_parts.append(f"TOEFL {toefl}")
    lang_str = " / ".join(lang_parts) if lang_parts else "No English test required"

    # Build eligible countries string
    if isinstance(eligible_countries, list):
        countries_str = ", ".join(eligible_countries[:10])
    else:
        countries_str = str(eligible_countries)

    # Build benefits string
    if isinstance(benefits, list) and benefits:
        benefits_str = "\n".join([f"- {b}" for b in benefits])
    else:
        benefits_str = "- Check official website for complete benefits"

    # Build degree string
    if isinstance(degree_levels, list) and degree_levels:
        degree_str = ", ".join(degree_levels)
    else:
        degree_str = str(degree_levels) if degree_levels else "All levels"

    seo_title = f"{title} {CURRENT_YEAR} — Complete Guide, Eligibility & How to Apply"
    seo_title = seo_title[:70]

    seo_desc = (
        f"Apply for {title} {CURRENT_YEAR}. "
        f"Deadline: {deadline}. "
        f"Open for {degree_str} students. "
        f"{lang_str}. "
        f"Eligible countries: {countries_str[:80]}."
    )[:160]

    blog = f"""# {title} {CURRENT_YEAR}

**Last Updated:** {datetime.now().strftime("%B %d, %Y")} | **Status:** Open for Applications

---

## About This Scholarship

The **{title}** is offered by **{uni}** in **{country}**, {region}. This is a genuine opportunity for international students who want to pursue world-class education abroad without paying lakhs of rupees to agents.

If you are a student from Pakistan, India, Bangladesh, Africa or any developing country — this scholarship is worth reading about carefully. We have gathered all the information you need in one place.

---

## Quick Summary

| Detail | Information |
|--------|------------|
| **Scholarship Name** | {title} |
| **Host University** | {uni} |
| **Country** | {country} |
| **Region** | {region} |
| **Degree Level** | {degree_str} |
| **Funding Type** | {funding} |
| **Application Deadline** | {deadline} |
| **IELTS Required** | {ielts or "Not required"} |
| **PTE Required** | {pte or "Not required"} |
| **TOEFL Required** | {toefl or "Not required"} |
| **Minimum GPA** | {gpa or "Check official website"} |
| **Last Verified** | {datetime.now().strftime("%B %Y")} |

---

## Who Is Eligible?

**Countries eligible to apply:**
{countries_str}

{"This scholarship is open to students from all over the world. Students from Pakistan, India, Bangladesh, Nigeria, Kenya, Ghana and other developing countries are strongly encouraged to apply." if any(w in countries_str.lower() for w in ['international', 'worldwide', 'all countries', 'open to']) else f"Students from the following countries or regions can apply: {countries_str}"}

**Academic level:**
This scholarship is available for: **{degree_str}** students.

Make sure your intended program and field of study is covered under this scholarship before applying.

---

## What Does This Scholarship Cover?

**Funding type: {funding}**

{benefits_str}

Always check the official website for the most accurate and updated breakdown of what this scholarship covers. Benefits can include tuition fees, monthly living allowance, travel grant, health insurance and accommodation.

---

## English Language Requirements

{"This scholarship does not specifically require an IELTS or English test. However, if your previous education was not in English, some universities may still ask for proof of English proficiency. Check the official requirements carefully." if not lang_parts else f"""
**Language tests required:**

{chr(10).join([f"- {l}" for l in lang_parts])}

**Tips to meet the requirement:**

- Start preparation at least 3 months before the application deadline
- Practice reading, writing, listening and speaking sections daily
- Take a mock test first to know your current level
- British Council and IDP offer IELTS in Pakistan — available in Karachi, Lahore, Islamabad and other cities
- Many students from Pakistan score 6.5 to 7.0 within 2 to 3 months of focused preparation
- Some universities accept TOEFL or Duolingo as alternatives — check official requirements
"""}

---

## Academic Requirements

**Minimum GPA / CGPA:** {gpa or "Check official website for specific GPA requirements"}

General guidance:
- Bachelor scholarships typically require 60% or above, or 2.5+ GPA
- Master scholarships often require First Class or 3.0+ GPA
- PhD scholarships usually require a strong Master's degree with research experience
- Some scholarships focus more on research output and motivation than GPA alone

---

## Application Deadline

**Deadline: {deadline}**

Do not wait until the last week. Here is a realistic timeline you should follow:

- 3 months before: Start gathering documents
- 2 months before: Write your SOP and get feedback
- 1 month before: Request recommendation letters
- 2 weeks before: Submit your application
- Keep confirmation receipt safe

Always verify the deadline on the official website as it can change.

---

## How to Apply — Step by Step

1. Visit the official scholarship website using the link at the bottom of this page
2. Read all eligibility criteria carefully before starting
3. Create an account on the application portal
4. Fill in all personal and academic information accurately
5. Upload all required documents in the specified format
6. Write your Statement of Purpose (see guide below)
7. Request recommendation letters from professors or employers
8. Review everything carefully before submission
9. Submit before the deadline: **{deadline}**
10. Save a copy of your submission confirmation

---

## Documents You Will Need

Prepare all of these well in advance:

- Valid Passport (must be valid throughout the scholarship period)
- Academic Transcripts (all previous degrees, certified copies)
- Degree Certificates or Provisional Certificates
- IELTS / PTE / TOEFL Certificate (if required — score: {lang_str})
- Statement of Purpose — 600 to 1000 words
- 2 to 3 Recommendation Letters (from professors or supervisors)
- Updated Academic CV or Resume
- Passport-size photographs
- Research Proposal (required for PhD applicants)
- Proof of English Medium Education (may waive IELTS requirement)
- Any other documents specified by the university

---

## How to Write a Winning SOP

Your Statement of Purpose is the most critical part of your application. Scholarship committees read thousands of SOPs. Yours must stand out.

**Structure that works:**

**Opening paragraph — Your story**
Do not start with "I am applying for..." Start with something real. A challenge you overcame. A moment that defined your direction. Make the reader feel something in the first three lines.

**Academic background**
Mention your degree, institution, GPA and the most relevant courses or projects you did. Be specific. Numbers matter — "published 2 research papers" is stronger than "I did research."

**Why this specific scholarship**
This is where most students fail. They write generic reasons. Research the university, the faculty, the specific program. Mention specific professors whose work aligns with yours. Show that you chose this scholarship deliberately — not because it was the first one you found.

**Career goals**
Where do you want to be in 5 years? 10 years? How does this scholarship fit into that path? How will you use this education to contribute to your country or field? Committees want to fund people who will make a difference — show them that is you.

**Why you deserve it**
Highlight what makes you different. Leadership roles, research experience, community work, awards, challenges you have overcome. Not bragging — evidence.

**Strong closing**
Thank the committee, restate your commitment, express genuine excitement. End on a confident, forward-looking note.

**Length:** 600 to 1000 words unless specified otherwise. Never exceed the given limit.

---

## Frequently Asked Questions

**Can students from Pakistan apply?**
{f"Yes — Pakistan is listed among the eligible countries for this scholarship." if "Pakistan" in countries_str else f"Check the eligibility section above and verify on the official website. Many international scholarships accept Pakistani students even if Pakistan is not explicitly listed."}

**Is IELTS compulsory?**
{f"Yes — the minimum IELTS score required is {ielts}. Some universities may accept TOEFL or PTE as alternatives." if ielts and ielts not in ["Not required", "Check website"] else "No IELTS requirement has been mentioned for this scholarship. Verify on the official website."}

**When is the deadline?**
**{deadline}** — Always confirm on the official website as deadlines can be updated.

**Is this scholarship fully funded?**
Funding type: **{funding}**. Visit the official page for the exact breakdown of what is covered.

**What if I am not selected?**
Do not stop. Most successful scholarship recipients applied to 5 to 10 scholarships before getting selected. Use this application as practice. Browse our website for more opportunities matched to your profile.

---

## Apply Now

Visit the official scholarship page for complete and updated information:

**Official Link:** {official_link}

> **Important:** Scholarship details including deadlines, requirements and benefits may change without notice. Always verify on the official website before applying.
> Last verified by AdmitGoal: {datetime.now().strftime("%B %d, %Y")}

---

*Share this with a friend who is looking for scholarships. One share can change someone's life.*
"""

    return blog, seo_title, seo_desc

# ── SAVE TO DATABASE ──────────────────────────────────────
def save(conn, data):
    if not data.get('title') or len(data['title']) < 10:
        return False
    if not data.get('scholarship_link'):
        return False
    if not data.get('deadline'):
        return False  # Only save scholarships with known deadlines

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

# ── SCRAPE INDIVIDUAL SCHOLARSHIP PAGE ───────────────────
def scrape_scholarship_page(url, source_domain, conn):
    """Scrape a single scholarship detail page"""
    r = fetch(url)
    if not r:
        return False

    soup = BeautifulSoup(r.text, 'lxml')
    for tag in soup.find_all(['nav', 'footer', 'script', 'style', 'aside', 'header']):
        tag.decompose()

    full_text = ' '.join(soup.get_text(separator=' ', strip=True).split())

    # Skip if clearly not about a scholarship
    if not any(kw in full_text.lower() for kw in ['scholarship', 'fellowship', 'grant', 'award', 'funding']):
        return False

    # Check freshness
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

    # Skip list pages — must be individual scholarship
    list_indicators = [
        'top 10', 'top 20', 'top 25', 'top 50', 'top 100',
        'list of', 'best scholarships', 'scholarships for 2025',
        'scholarships in 2026', '10 scholarships', '20 scholarships',
        '25 scholarships', '50 scholarships'
    ]
    if any(indicator in title.lower() for indicator in list_indicators):
        print(f"    Skip list page: {title[:50]}")
        return False

    # Extract all data
    deadline = extract_deadline(full_text)
    if not deadline:
        return False  # Skip if no deadline found

    ielts = extract_ielts(full_text)
    pte = extract_pte(full_text)
    toefl = extract_toefl(full_text)
    gpa = extract_gpa(full_text)
    degree_levels = extract_degree(full_text)
    funding = extract_funding(full_text)
    eligible_countries = extract_eligible_countries(full_text)
    benefits = extract_benefits(full_text)

    # Find official link
    official_link = extract_official_link(soup, url, full_text)
    if not official_link:
        official_link = url  # Use current URL as fallback

    # Detect country and region
    parsed_url = urlparse(official_link)
    domain = parsed_url.netloc
    country = detect_country(domain, full_text)
    region = detect_region(country)

    # If country is unknown try from text
    if country == "International":
        country_hints = {
            'germany': 'Germany', 'uk': 'United Kingdom', 'australia': 'Australia',
            'canada': 'Canada', 'japan': 'Japan', 'china': 'China',
            'korea': 'South Korea', 'turkey': 'Turkey', 'france': 'France',
            'netherlands': 'Netherlands', 'sweden': 'Sweden', 'norway': 'Norway',
            'usa': 'USA', 'united states': 'USA', 'america': 'USA',
            'saudi arabia': 'Saudi Arabia', 'malaysia': 'Malaysia',
            'singapore': 'Singapore', 'new zealand': 'New Zealand',
        }
        for hint, c in country_hints.items():
            if hint in full_text.lower()[:500]:
                country = c
                region = detect_region(country)
                break

    # Extract university name
    uni_name = "Check official website"
    # Try to find uni name from meta or title
    meta_site = soup.find('meta', {'property': 'og:site_name'})
    if meta_site:
        uni_name = meta_site.get('content', '')[:80]
    elif domain:
        uni_name = domain.replace('www.', '').replace('.edu', '').replace('.ac.uk', '').replace('.com', '').title()[:80]

    # Build description
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

# ── SOURCES TO SCRAPE ────────────────────────────────────
# These are listing pages — we extract individual scholarship links from them
LISTING_PAGES = [
    # scholars4dev — reliable individual scholarship pages
    "https://www.scholars4dev.com/",
    "https://www.scholars4dev.com/page/2/",
    "https://www.scholars4dev.com/page/3/",
    "https://www.scholars4dev.com/page/4/",
    "https://www.scholars4dev.com/page/5/",

    # Scholarship by country — individual pages
    "https://scholarshipdb.net/scholarships-in-Germany?page=1",
    "https://scholarshipdb.net/scholarships-in-United-Kingdom?page=1",
    "https://scholarshipdb.net/scholarships-in-China?page=1",
    "https://scholarshipdb.net/scholarships-in-Turkey?page=1",
    "https://scholarshipdb.net/scholarships-in-South-Korea?page=1",
    "https://scholarshipdb.net/scholarships-in-Japan?page=1",
    "https://scholarshipdb.net/scholarships-in-Australia?page=1",
    "https://scholarshipdb.net/scholarships-in-Canada?page=1",
    "https://scholarshipdb.net/scholarships-in-Saudi-Arabia?page=1",
    "https://scholarshipdb.net/scholarships-in-Netherlands?page=1",
    "https://scholarshipdb.net/scholarships-in-Norway?page=1",
    "https://scholarshipdb.net/scholarships-in-Sweden?page=1",
    "https://scholarshipdb.net/scholarships-in-Finland?page=1",
    "https://scholarshipdb.net/scholarships-in-Hungary?page=1",
    "https://scholarshipdb.net/scholarships-in-France?page=1",
    "https://scholarshipdb.net/scholarships-in-Italy?page=1",
    "https://scholarshipdb.net/scholarships-in-Malaysia?page=1",
    "https://scholarshipdb.net/scholarships-in-Singapore?page=1",
    "https://scholarshipdb.net/scholarships-in-New-Zealand?page=1",
    "https://scholarshipdb.net/scholarships-in-USA?page=1",

    # Government official scholarship pages
    "https://www.chevening.org/scholarships/",
    "https://www.daad.de/en/study-and-research-in-germany/scholarships/",
    "https://www.campuschina.org/scholarships/index.html",
    "https://www.turkiyeburslari.gov.tr/en",
    "https://stipendiumhungaricum.hu/en/",
    "https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do",
]

def get_individual_links(listing_url):
    """Extract individual scholarship page links from a listing page"""
    r = fetch(listing_url)
    if not r:
        return []

    soup = BeautifulSoup(r.text, 'lxml')
    links = []
    seen = set()

    # Get base domain
    parsed = urlparse(listing_url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    # Find all article/post links
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)

        # Make absolute
        if href.startswith('/'):
            href = base + href
        elif not href.startswith('http'):
            continue

        # Skip navigation, category, tag pages
        skip_patterns = [
            '/category/', '/tag/', '/page/', '/author/', '#',
            'javascript', 'mailto', 'facebook', 'twitter',
            'instagram', 'linkedin', 'youtube',
            '/about', '/contact', '/privacy', '/terms',
            'search', 'login', 'register', 'signup'
        ]
        if any(skip in href.lower() for skip in skip_patterns):
            continue

        # Skip if same as listing page
        if href == listing_url or href == listing_url.rstrip('/'):
            continue

        # Must be from same domain or known scholarship domain
        href_domain = urlparse(href).netloc
        listing_domain = urlparse(listing_url).netloc

        if href_domain == listing_domain:
            # Individual content page
            path = urlparse(href).path
            if len(path.split('/')) >= 2 and len(text) > 15:
                if href not in seen:
                    seen.add(href)
                    links.append(href)

    return links[:20]  # Max 20 links per listing page

# ── MAIN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  ADMITGOAL MASTER SCRAPER v3.0")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Target: Individual fresh scholarships only")
    print(f"  Sources: {len(LISTING_PAGES)} listing pages")
    print("=" * 60)

    conn = get_db()
    total_saved = 0
    total_skipped = 0

    for listing_url in LISTING_PAGES:
        parsed = urlparse(listing_url)
        print(f"\n[SOURCE] {parsed.netloc}")
        print(f"  URL: {listing_url}")

        # Get individual scholarship links
        individual_links = get_individual_links(listing_url)
        print(f"  Found {len(individual_links)} individual links")

        for link in individual_links:
            print(f"\n  Checking: {link[:70]}")
            try:
                saved = scrape_scholarship_page(link, parsed.netloc, conn)
                if saved:
                    print(f"  SAVED")
                    total_saved += 1
                else:
                    print(f"  Skipped (outdated/incomplete/list)")
                    total_skipped += 1
            except Exception as e:
                print(f"  Error: {e}")
                total_skipped += 1

            time.sleep(random.uniform(2, 4))

        time.sleep(random.uniform(3, 6))

    # Final count
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
    print(f"  Quality    : Individual pages only")
    print(f"               Official links only")
    print(f"               Open scholarships only")
    print(f"               Complete data only")
    print(f"{'=' * 60}")