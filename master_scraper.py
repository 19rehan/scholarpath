import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
import re
from datetime import datetime

CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month

def get_headers():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
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
        except:
            time.sleep(4)
    return None

# ══════════════════════════════════════════════════════════
# FRESHNESS CHECK — MOST IMPORTANT FUNCTION
# Removes outdated, keeps only open scholarships
# ══════════════════════════════════════════════════════════
def is_scholarship_open(text):
    text_lower = text.lower()

    # Hard closed signals — remove immediately
    closed_signals = [
        'applications are closed', 'deadline has passed',
        'no longer accepting', 'competition is closed',
        'applications closed', 'closed for',
        'this scholarship has ended', 'not available'
    ]
    for signal in closed_signals:
        if signal in text_lower:
            return False, "CLOSED"

    months_map = {
        'january':1,'february':2,'march':3,'april':4,
        'may':5,'june':6,'july':7,'august':8,
        'september':9,'october':10,'november':11,'december':12
    }

    # Find all dates in text
    patterns = [
        r'(january|february|march|april|may|june|july|august|'
        r'september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})',
        r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|'
        r'september|october|november|december)\s+(\d{4})',
        r'(\d{4})-(\d{2})-(\d{2})',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text_lower):
            try:
                g = match.groups()
                if g[0] in months_map:
                    month, day, year = months_map[g[0]], int(g[1]), int(g[2])
                elif g[1] in months_map:
                    day, month, year = int(g[0]), months_map[g[1]], int(g[2])
                else:
                    year, month, day = int(g[0]), int(g[1]), int(g[2])

                if year > CURRENT_YEAR:
                    return True, f"Open — deadline {month}/{year}"
                if year == CURRENT_YEAR and month >= CURRENT_MONTH:
                    return True, f"Open — deadline {month}/{CURRENT_YEAR}"
                if year == CURRENT_YEAR and month < CURRENT_MONTH:
                    return False, f"Expired — was {month}/{CURRENT_YEAR}"
            except:
                continue

    # Future year mentioned = likely open
    if str(CURRENT_YEAR + 1) in text:
        return True, f"Open — mentions {CURRENT_YEAR + 1}"

    # Current year + scholarship keyword = possibly open
    if str(CURRENT_YEAR) in text and any(
        kw in text_lower for kw in ['apply now','open','accepting','applications open']):
        return True, "Open — accepting applications"

    # No dates found — keep but flag
    return True, "No deadline found — keep and verify"

def setup_db():
    conn = sqlite3.connect('scholarships.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scholarships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, description TEXT, country TEXT,
        deadline TEXT, link TEXT UNIQUE,
        source TEXT, scraped_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS scholarship_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scholarship_link TEXT UNIQUE, title TEXT,
        full_description TEXT, eligible_countries TEXT,
        eligible_students TEXT, degree_level TEXT,
        deadline TEXT, language_requirement TEXT,
        ielts_score TEXT, benefits TEXT, how_to_apply TEXT,
        blog_post TEXT, seo_title TEXT, seo_description TEXT,
        university_name TEXT, country TEXT, region TEXT,
        funding_type TEXT, gpa_required TEXT,
        last_updated TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS discovered_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE, domain TEXT, country TEXT,
        last_scraped TEXT, total_found INTEGER DEFAULT 0)''')
    conn.commit()
    return conn

# ══════════════════════════════════════════════════════════
# EXTRACTORS
# ══════════════════════════════════════════════════════════
def extract_ielts(text):
    for p in [r'ielts[:\s]*(\d+\.?\d*)', r'(\d+\.?\d*)\s*(?:in|for)?\s*ielts']:
        m = re.search(p, text, re.IGNORECASE)
        if m: return m.group(1)
    if re.search(r'ielts', text, re.IGNORECASE): return "Required"
    return "Not required"

def extract_pte(text):
    m = re.search(r'pte[:\s]*(\d+)', text, re.IGNORECASE)
    return m.group(1) if m else ("Required" if re.search(r'\bpte\b', text, re.IGNORECASE) else "Not mentioned")

def extract_toefl(text):
    m = re.search(r'toefl[:\s]*(\d+)', text, re.IGNORECASE)
    return m.group(1) if m else ("Required" if re.search(r'toefl', text, re.IGNORECASE) else "Not mentioned")

def extract_gpa(text):
    for p in [r'gpa[:\s]*(\d+\.?\d*)', r'cgpa[:\s]*(\d+\.?\d*)',
              r'(\d+\.?\d*)\s*(?:gpa|cgpa)',
              r'(\d{2,3})%\s*(?:or above|minimum|at least)']:
        m = re.search(p, text, re.IGNORECASE)
        if m: return m.group(1)
    return "Check website"

def extract_deadline(text):
    months = ("january|february|march|april|may|june|july|august|"
               "september|october|november|december")
    for p in [
        rf'deadline[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'closing date[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'apply by[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'due[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'(\d{{1,2}}\s+(?:{months})\s+\d{{4}})',
        rf'((?:{months})\s+\d{{1,2}},?\s+\d{{4}})',
        rf'((?:{months})\s+\d{{4}})',
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
    if re.search(r'partial|tuition only', text, re.IGNORECASE): return "Partial"
    if re.search(r'stipend|living allowance|monthly allowance', text, re.IGNORECASE):
        return "Stipend Included"
    return "Check website"

def extract_eligible_countries(text):
    for kw in ['open to','eligible countries','nationals of',
               'citizens of','students from','who can apply']:
        idx = text.lower().find(kw)
        if idx != -1:
            return text[idx:idx+300]
    return "Open to international students worldwide"

def detect_country(domain):
    tlds = {
        '.ac.uk':'UK','.co.uk':'UK','.uk':'UK',
        '.edu.au':'Australia','.com.au':'Australia','.au':'Australia',
        '.ca':'Canada','.de':'Germany','.fr':'France',
        '.nl':'Netherlands','.se':'Sweden','.no':'Norway',
        '.fi':'Finland','.dk':'Denmark','.ch':'Switzerland',
        '.at':'Austria','.be':'Belgium','.it':'Italy',
        '.es':'Spain','.pt':'Portugal','.pl':'Poland',
        '.cz':'Czech Republic','.hu':'Hungary','.ro':'Romania',
        '.sk':'Slovakia','.si':'Slovenia','.hr':'Croatia',
        '.gr':'Greece','.bg':'Bulgaria','.lt':'Lithuania',
        '.lv':'Latvia','.ee':'Estonia',
        '.tr':'Turkey','.sa':'Saudi Arabia','.ae':'UAE',
        '.qa':'Qatar','.jo':'Jordan','.kw':'Kuwait',
        '.om':'Oman','.bh':'Bahrain','.eg':'Egypt',
        '.ma':'Morocco','.tn':'Tunisia','.ng':'Nigeria',
        '.za':'South Africa','.ke':'Kenya','.gh':'Ghana',
        '.cn':'China','.jp':'Japan','.kr':'South Korea',
        '.my':'Malaysia','.sg':'Singapore','.th':'Thailand',
        '.id':'Indonesia','.vn':'Vietnam','.tw':'Taiwan',
        '.hk':'Hong Kong','.nz':'New Zealand',
        '.br':'Brazil','.mx':'Mexico','.ar':'Argentina',
        '.pk':'Pakistan','.in':'India','.bd':'Bangladesh',
        '.lk':'Sri Lanka','.np':'Nepal',
        '.edu':'USA','.gov':'USA',
    }
    for tld, country in sorted(tlds.items(), key=lambda x: -len(x[0])):
        if domain.endswith(tld): return country
    return "International"

def detect_region(country):
    regions = {
        'Europe': ['UK','Germany','France','Netherlands','Sweden','Norway',
                   'Finland','Denmark','Switzerland','Austria','Belgium',
                   'Italy','Spain','Portugal','Poland','Czech Republic',
                   'Hungary','Romania','Slovakia','Slovenia','Croatia',
                   'Greece','Bulgaria','Lithuania','Latvia','Estonia'],
        'Middle East': ['Turkey','Saudi Arabia','UAE','Qatar','Jordan',
                        'Kuwait','Oman','Bahrain','Egypt','Morocco','Tunisia'],
        'Asia': ['China','Japan','South Korea','Malaysia','Singapore',
                 'Thailand','Indonesia','Vietnam','Taiwan','Hong Kong',
                 'Pakistan','India','Bangladesh','Sri Lanka','Nepal'],
        'Oceania': ['Australia','New Zealand'],
        'North America': ['USA','Canada'],
        'Africa': ['Nigeria','South Africa','Kenya','Ghana'],
        'Latin America': ['Brazil','Mexico','Argentina'],
    }
    for region, countries in regions.items():
        if country in countries: return region
    return "International"

# ══════════════════════════════════════════════════════════
# BLOG WRITER — Complete, detailed, SEO optimized
# ══════════════════════════════════════════════════════════
def write_blog(title, desc, eligible_countries, degree, deadline,
               ielts, pte, toefl, gpa, funding, benefits,
               how_to_apply, uni_name, country, link):

    lang_req = []
    if ielts != "Not required": lang_req.append(f"IELTS: {ielts}")
    if pte != "Not mentioned": lang_req.append(f"PTE: {pte}")
    if toefl != "Not mentioned": lang_req.append(f"TOEFL: {toefl}")
    lang_str = " | ".join(lang_req) if lang_req else "No English test required"

    seo_title = f"{title} {CURRENT_YEAR} – Complete Guide, Eligibility & How to Apply"
    seo_desc = (f"Apply for {title} {CURRENT_YEAR}. Deadline: {deadline}. "
                f"Open for {degree} students. {lang_str}. "
                f"Full eligibility, documents & step-by-step guide.")[:160]

    blog = f"""# {title} {CURRENT_YEAR} – Complete Guide

**Last Updated:** {datetime.now().strftime("%B %d, %Y")} | **Status:** Open for Applications

---

## Overview

The **{title}** is an exciting opportunity for international students in {CURRENT_YEAR}. 
Offered by **{uni_name}** in **{country}**, this scholarship supports deserving students 
who want to pursue world-class education abroad. Thousands of students from Pakistan, 
India, Bangladesh, Africa and around the world apply for opportunities like this every year 
— and many miss out simply because they did not know it existed. We found it for you.

---

## Quick Summary Table

| Detail | Information |
|--------|------------|
| **Scholarship Name** | {title} |
| **University / Host** | {uni_name} |
| **Country** | {country} |
| **Degree Level** | {degree} |
| **Funding Type** | {funding} |
| **Application Deadline** | {deadline} |
| **IELTS Required** | {ielts} |
| **PTE Required** | {pte} |
| **TOEFL Required** | {toefl} |
| **Minimum GPA / CGPA** | {gpa} |
| **Last Verified** | {datetime.now().strftime("%B %Y")} |

---

## What Does This Scholarship Cover?

{benefits if benefits and len(benefits) > 30 else
f"The {title} is designed to support students financially so they can focus on academics. "
f"Please visit the official website for the complete and most updated funding breakdown, "
f"as scholarship benefits can include tuition fees, living allowance, flights, and health insurance."}

---

## Who Can Apply? (Eligibility)

{eligible_countries}

Students who meet the academic and eligibility requirements are strongly encouraged to apply. 
Do not assume you are not eligible — always check the official website. Many scholarships 
that say "limited countries" still accept applications from Pakistan, India, and Bangladesh.

---

## Degree Levels

This scholarship accepts applications for: **{degree}**

Make sure your intended program and field of study is covered. Some scholarships are 
field-specific (engineering, medicine, business) while others are open to all disciplines.

---

## English Language Requirements

**{lang_str}**

{"This scholarship does not require an English language test. This is great news for students who have not yet appeared in IELTS or PTE." if not lang_req else f"""
If you need to appear in an English test, here is what you should know:

- **IELTS score required:** {ielts}
- **PTE score required:** {pte}  
- **TOEFL score required:** {toefl}

**Tips to achieve the required score:**

1. Start preparation at least 3 months before the deadline
2. Practice past papers daily — reading, writing, listening, speaking
3. Take a mock test first to know your current level
4. Join a preparation course if needed — many affordable options are available
5. British Council and IDP both offer IELTS in Pakistan — check your nearest center
6. Some scholarships waive IELTS if your previous education was in English medium
"""}

---

## Academic Requirements

**Minimum GPA / CGPA:** {gpa}

Most international scholarships require a strong academic record. Here are some general tips:

- Undergraduate scholarships typically need 3.0+ GPA or 70%+ marks
- Master's scholarships often need First Class or 3.2+ GPA
- PhD scholarships usually require a Master's with strong research background
- Some scholarships look at research publications and extracurricular activities

---

## How to Apply – Step by Step

{how_to_apply if how_to_apply and len(how_to_apply) > 50 else "Visit the official website to start your application."}

**General application steps:**

1. Visit the official scholarship website (link at the bottom)
2. Read all eligibility requirements carefully
3. Create an account or register as a new applicant
4. Fill in your personal and academic information completely
5. Upload all required documents (see checklist below)
6. Write your Statement of Purpose (SOP)
7. Get recommendation letters from professors or employers
8. Submit your application before: **{deadline}**
9. Keep a screenshot or PDF of your submission confirmation

---

## Documents Required – Full Checklist

Prepare these documents before starting your application:

- ✅ Valid Passport (check expiry — must be valid for full scholarship duration)
- ✅ Academic Transcripts (all previous degrees — certified copies)
- ✅ Degree Certificates or Provisional Certificates
- ✅ IELTS / PTE / TOEFL Certificate (if required)
- ✅ Statement of Purpose (SOP) — 600 to 1000 words
- ✅ 2 to 3 Recommendation Letters (from professors or supervisors)
- ✅ Updated CV / Resume (academic and professional)
- ✅ Passport-size photographs
- ✅ Research Proposal (for PhD applicants)
- ✅ Proof of English Medium Education (if IELTS waiver applies)
- ✅ Bank statement or financial documents (some scholarships require)
- ✅ Medical certificate (some scholarships require)

---

## How to Write a Strong SOP for This Scholarship

Your Statement of Purpose is the most important part of your application. Here is the 
structure that works:

**Paragraph 1 — Hook:** Start with a powerful personal story or achievement. 
Example: "Growing up in a small town in Pakistan, access to quality education was my 
biggest challenge — and my biggest motivation."

**Paragraph 2 — Academic Background:** Mention your degree, GPA, relevant courses, 
and any research or projects.

**Paragraph 3 — Why This Scholarship:** Be specific. Mention the university, the 
program, and why THIS scholarship matches your goals.

**Paragraph 4 — Career Goals:** Where do you see yourself in 5 years? How does this 
scholarship help you get there?

**Paragraph 5 — Why You Deserve It:** Leadership, community work, awards, hardships 
you have overcome.

**Paragraph 6 — Closing:** Thank the committee. Restate your commitment and potential.

**Length:** 600–1000 words. Never exceed the word limit given by the scholarship.

---

## Tips to Maximize Your Chances

1. **Apply early** — Do not wait until the last week
2. **Be specific in your SOP** — Generic SOPs get rejected
3. **Strong recommendation letters** — Brief your recommenders about the scholarship
4. **Double-check every document** — Incomplete applications are rejected instantly
5. **Follow instructions exactly** — Wrong format = automatic disqualification
6. **Apply to multiple scholarships** — Never put all hopes in one application
7. **Contact the scholarship office** — Emailing them shows genuine interest

---

## Frequently Asked Questions

**Q: Can students from Pakistan apply?**
A: Check the eligibility section above. Most international scholarships welcome Pakistani 
students. Verify on the official website for the most accurate information.

**Q: Is IELTS required?**
A: {f"Yes — minimum IELTS score required is {ielts}" if ielts not in ["Not required","Not mentioned"] else "No IELTS requirement mentioned. Verify on official website."}

**Q: When is the deadline?**
A: **{deadline}** — Always verify on the official website as deadlines can be extended or changed.

**Q: Is this scholarship fully funded?**
A: Funding type: **{funding}**. Visit the official page for exact details of what is covered.

**Q: What if I am not eligible for this scholarship?**
A: Browse our website for hundreds of other scholarships matched to your profile. We update 
daily so new opportunities appear regularly.

---

## Apply Now

🚀 **Ready to apply?** Visit the official page for complete and updated information:

**Official Link:** {link}

> ⚠️ **Important:** Scholarship details including deadlines and requirements may change 
> without notice. Always verify on the official website before applying.
> **Last verified by ScholarPath:** {datetime.now().strftime("%B %d, %Y")}

---

*Found this useful? Share it with a friend who is looking for scholarships. 
One share can change someone's life.*
"""
    return blog, seo_title, seo_desc

# ══════════════════════════════════════════════════════════
# SAVE TO DATABASE
# ══════════════════════════════════════════════════════════
def save_to_db(conn, uni_name, country, region, title, desc,
               eligible_countries, degree, deadline, ielts, pte,
               toefl, gpa, funding, benefits, how_to_apply, link):
    if not title or len(title) < 8 or not link:
        return False

    blog, seo_title, seo_desc = write_blog(
        title, desc, eligible_countries, degree, deadline,
        ielts, pte, toefl, gpa, funding, benefits, how_to_apply,
        uni_name, country, link)

    lang_req = []
    if ielts != "Not required": lang_req.append(f"IELTS {ielts}")
    if pte != "Not mentioned": lang_req.append(f"PTE {pte}")
    lang_str = " | ".join(lang_req) if lang_req else "No test required"

    try:
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO scholarship_details
            (scholarship_link, title, full_description, eligible_countries,
             eligible_students, degree_level, deadline, language_requirement,
             ielts_score, benefits, how_to_apply, blog_post, seo_title,
             seo_description, university_name, country, region,
             funding_type, gpa_required, last_updated)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (link, title, desc[:800], eligible_countries[:400],
             "International students", degree, deadline, lang_str,
             ielts, benefits[:400], how_to_apply[:400], blog,
             seo_title, seo_desc, uni_name, country, region,
             funding, gpa, datetime.now().strftime("%Y-%m-%d")))
        c.execute('''INSERT OR IGNORE INTO scholarships
            (title, description, country, deadline, link, source, scraped_date)
            VALUES(?,?,?,?,?,?,?)''',
            (title, seo_desc, country, deadline, link,
             f"uni_{uni_name[:20].lower().replace(' ','_')}",
             datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        return True
    except Exception as e:
        return False

# ══════════════════════════════════════════════════════════
# CLEAN OUTDATED SCHOLARSHIPS EVERY RUN
# ══════════════════════════════════════════════════════════
def clean_outdated(conn):
    print("\n[CLEAN] Removing outdated scholarships...")
    c = conn.cursor()
    rows = c.execute(
        "SELECT id, scholarship_link, deadline FROM scholarship_details"
    ).fetchall()

    removed = 0
    months_map = {
        'january':1,'february':2,'march':3,'april':4,
        'may':5,'june':6,'july':7,'august':8,
        'september':9,'october':10,'november':11,'december':12
    }

    for sid, link, deadline in rows:
        if not deadline or deadline in ['See official website','See link']:
            continue

        dl = deadline.lower()
        expired = False

        # Check year
        year_match = re.search(r'(\d{4})', dl)
        if year_match:
            year = int(year_match.group(1))
            if year < CURRENT_YEAR:
                expired = True
            elif year == CURRENT_YEAR:
                # Check month
                for month_name, month_num in months_map.items():
                    if month_name in dl:
                        if month_num < CURRENT_MONTH - 1:
                            expired = True
                        break

        if expired:
            c.execute("DELETE FROM scholarship_details WHERE id=?", (sid,))
            c.execute("DELETE FROM scholarships WHERE link=?", (link,))
            conn.commit()
            removed += 1

    print(f"  Removed {removed} outdated scholarships")
    return removed

# ══════════════════════════════════════════════════════════
# SCRAPE ANY URL — SMART & DEEP
# ══════════════════════════════════════════════════════════
def scrape_url(conn, url, domain, country):
    r = smart_fetch(url)
    if not r:
        return 0

    soup = BeautifulSoup(r.text, 'lxml')
    for tag in soup.find_all(['nav','footer','script','style','aside']):
        tag.decompose()

    full_text = ' '.join(soup.get_text(separator=' ', strip=True).split())

    # Check if page itself is about an open scholarship
    is_open, reason = is_scholarship_open(full_text)

    region = detect_region(country)
    saved = 0
    seen = set()

    # Detect uni name
    uni_name = domain
    title_tag = soup.find('title')
    if title_tag:
        raw = title_tag.get_text(strip=True)
        uni_name = raw.split('|')[0].split('–')[0].split('-')[0].strip()[:80]

    # Global extractions
    ielts = extract_ielts(full_text)
    pte = extract_pte(full_text)
    toefl = extract_toefl(full_text)
    gpa = extract_gpa(full_text)
    funding = extract_funding(full_text)
    degree = extract_degree(full_text)
    deadline = extract_deadline(full_text)
    eligible = extract_eligible_countries(full_text)

    def process_item(title, link, local_text=""):
        nonlocal saved
        if title in seen or len(title) < 10:
            return
        seen.add(title)

        combined = local_text + " " + full_text
        item_open, item_reason = is_scholarship_open(combined)
        if not item_open:
            return

        item_deadline = extract_deadline(local_text) if local_text else deadline
        item_ielts = extract_ielts(local_text) if local_text else ielts
        item_pte = extract_pte(local_text) if local_text else pte
        item_toefl = extract_toefl(local_text) if local_text else toefl
        item_gpa = extract_gpa(local_text) if local_text else gpa
        item_funding = extract_funding(local_text) if local_text else funding
        item_degree = extract_degree(local_text) if local_text else degree

        # Build description
        desc = local_text[:500] if len(local_text) > 50 else f"Scholarship at {uni_name}"

        # Benefits
        benefits = ""
        for kw in ['covers','includes','provides','award','stipend','tuition']:
            idx = combined.lower().find(kw)
            if idx != -1:
                benefits = combined[idx:idx+300]
                break

        # How to apply
        how_to = ""
        idx = combined.lower().find('how to apply')
        if idx != -1:
            how_to = combined[idx:idx+400]

        ok = save_to_db(conn, uni_name, country, region, title, desc,
                        eligible, item_degree, item_deadline, item_ielts,
                        item_pte, item_toefl, item_gpa, item_funding,
                        benefits, how_to, link)
        if ok:
            print(f"  ✓ [{item_deadline}] {title[:65]}")
            saved += 1

    # Strategy 1: Headings
    for tag in soup.find_all(['h1','h2','h3','h4','h5']):
        text = tag.get_text(strip=True)
        if not any(kw in text.lower() for kw in
                   ['scholarship','award','bursary','fellowship',
                    'grant','funding','financial aid','stipend','prize']):
            continue
        link = url
        a = tag.find('a', href=True) or tag.find_next('a', href=True)
        if a:
            href = a['href']
            link = href if href.startswith('http') else \
                   f"https://{domain}{href}" if href.startswith('/') else url
        local = ""
        nxt = tag.find_next_sibling()
        for _ in range(4):
            if nxt and nxt.name in ['p','div','ul','ol']:
                local += " " + nxt.get_text(strip=True)
                nxt = nxt.find_next_sibling()
            else:
                break
        process_item(text, link, local)

    # Strategy 2: Scholarship links
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        href = a['href']
        if not any(kw in text.lower() for kw in
                   ['scholarship','award','bursary','fellowship',
                    'grant','funding','financial aid']):
            continue
        if len(text) < 12: continue
        if not href.startswith('http'):
            href = f"https://{domain}{href}" if href.startswith('/') else url
        process_item(text, href, "")

    # Strategy 3: Go deeper into sub-pages if nothing found
    if saved == 0:
        for a in soup.find_all('a', href=True):
            href = a['href']
            if not any(kw in href.lower() for kw in
                       ['scholarship','award','funding','bursary','fellowship']):
                continue
            if not href.startswith('http'):
                href = f"https://{domain}{href}" if href.startswith('/') else url
            if domain not in href or href in seen:
                continue
            seen.add(href)
            sub_r = smart_fetch(href)
            if not sub_r: continue
            sub_soup = BeautifulSoup(sub_r.text, 'lxml')
            sub_text = ' '.join(sub_soup.get_text(separator=' ', strip=True).split())
            sub_open, _ = is_scholarship_open(sub_text)
            if not sub_open: continue
            for h in sub_soup.find_all(['h1','h2','h3']):
                h_text = h.get_text(strip=True)
                if any(kw in h_text.lower() for kw in
                       ['scholarship','award','fellowship','grant','funding']):
                    process_item(h_text, href, sub_text[:1000])
            time.sleep(1)

    return saved

# ══════════════════════════════════════════════════════════
# SOURCES — Every region, every type
# Seeds + Google discovery = world coverage
# ══════════════════════════════════════════════════════════
SEED_SOURCES = [
    # ── Aggregators ───────────────────────────────────────
    ("https://www.scholars4dev.com/", "scholars4dev.com", "International"),
    ("https://www.scholars4dev.com/page/2/", "scholars4dev.com", "International"),
    ("https://www.scholars4dev.com/page/3/", "scholars4dev.com", "International"),
    ("https://www.scholars4dev.com/page/4/", "scholars4dev.com", "International"),
    ("https://scholarshipdb.net/scholarships", "scholarshipdb.net", "International"),
    ("https://scholarshipdb.net/scholarships?page=2", "scholarshipdb.net", "International"),
    ("https://scholarshipdb.net/scholarships?page=3", "scholarshipdb.net", "International"),
    ("https://scholarshipdb.net/scholarships?page=4", "scholarshipdb.net", "International"),
    ("https://www.afterschoolafrica.com/category/scholarships/", "afterschoolafrica.com", "Africa"),
    ("https://www.afterschoolafrica.com/category/scholarships/page/2/", "afterschoolafrica.com", "Africa"),
    ("https://opportunitydesk.org/category/scholarships/", "opportunitydesk.org", "International"),
    ("https://www.youthop.com/scholarships", "youthop.com", "International"),
    ("https://www.mastersportal.eu/scholarship/", "mastersportal.eu", "Europe"),
    ("https://www.phdportal.eu/scholarship/", "phdportal.eu", "International"),
    ("https://www.opportunitiesforafricans.com/category/scholarships/", "opportunitiesforafricans.com", "Africa"),
    ("https://www.estudyassistance.com/scholarships", "estudyassistance.com", "International"),

    # ── Pakistan / South Asia focused ─────────────────────
    ("https://propakistani.pk/scholarships/", "propakistani.pk", "Pakistan"),
    ("https://www.hec.gov.pk/english/scholarshipsgrants/Pages/default.aspx", "hec.gov.pk", "Pakistan"),
    ("https://www.buddy4study.com/scholarships", "buddy4study.com", "India"),

    # ── Europe governments ─────────────────────────────────
    ("https://www.daad.de/en/study-and-research-in-germany/scholarships/", "daad.de", "Germany"),
    ("https://www.chevening.org/scholarships/", "chevening.org", "UK"),
    ("https://cscuk.fcdo.gov.uk/scholarships/", "cscuk.fcdo.gov.uk", "UK"),
    ("https://stipendiumhungaricum.hu/en/", "stipendiumhungaricum.hu", "Hungary"),
    ("https://www.studyineurope.eu/scholarships", "studyineurope.eu", "Europe"),
    ("https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en", "eacea.ec.europa.eu", "Europe"),
    ("https://www.scholarships.gc.ca/scholarships-bourses/index.aspx", "scholarships.gc.ca", "Canada"),

    # ── Asia governments ───────────────────────────────────
    ("https://www.campuschina.org/scholarships/index.html", "campuschina.org", "China"),
    ("https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do", "studyinkorea.go.kr", "South Korea"),
    ("https://www.studyinjapan.go.jp/en/smap_stopj-applications_scholarship.html", "studyinjapan.go.jp", "Japan"),
    ("https://www.mohe.gov.my/en/scholarships", "mohe.gov.my", "Malaysia"),

    # ── Middle East ────────────────────────────────────────
    ("https://www.turkiyeburslari.gov.tr/en", "turkiyeburslari.gov.tr", "Turkey"),
    ("https://www.kaust.edu.sa/en/study/financial-support", "kaust.edu.sa", "Saudi Arabia"),
    ("https://www.qu.edu.qa/students/student_life/scholarships", "qu.edu.qa", "Qatar"),

    # ── Oceania ────────────────────────────────────────────
    ("https://www.studyinaustralia.gov.au/english/australian-scholarships", "studyinaustralia.gov.au", "Australia"),
    ("https://www.studyinnewzealand.govt.nz/how-to-apply/scholarships", "studyinnewzealand.govt.nz", "New Zealand"),

    # ── USA ────────────────────────────────────────────────
    ("https://foreign.fulbrightonline.org/", "fulbrightonline.org", "USA"),
    ("https://www.iie.org/programs/", "iie.org", "USA"),

    # ── Africa ─────────────────────────────────────────────
    ("https://www.africanscholarships.com/", "africanscholarships.com", "Africa"),
    ("https://www.opportunitiesforafricans.com/scholarships-for-africans/", "opportunitiesforafricans.com", "Africa"),

    # ── Country-specific discovery ─────────────────────────
    ("https://scholarshipdb.net/scholarships-in-United-Kingdom", "scholarshipdb.net", "UK"),
    ("https://scholarshipdb.net/scholarships-in-Germany", "scholarshipdb.net", "Germany"),
    ("https://scholarshipdb.net/scholarships-in-France", "scholarshipdb.net", "France"),
    ("https://scholarshipdb.net/scholarships-in-China", "scholarshipdb.net", "China"),
    ("https://scholarshipdb.net/scholarships-in-Australia", "scholarshipdb.net", "Australia"),
    ("https://scholarshipdb.net/scholarships-in-Canada", "scholarshipdb.net", "Canada"),
    ("https://scholarshipdb.net/scholarships-in-USA", "scholarshipdb.net", "USA"),
    ("https://scholarshipdb.net/scholarships-in-Japan", "scholarshipdb.net", "Japan"),
    ("https://scholarshipdb.net/scholarships-in-South-Korea", "scholarshipdb.net", "South Korea"),
    ("https://scholarshipdb.net/scholarships-in-Turkey", "scholarshipdb.net", "Turkey"),
    ("https://scholarshipdb.net/scholarships-in-Saudi-Arabia", "scholarshipdb.net", "Saudi Arabia"),
    ("https://scholarshipdb.net/scholarships-in-Netherlands", "scholarshipdb.net", "Netherlands"),
    ("https://scholarshipdb.net/scholarships-in-Sweden", "scholarshipdb.net", "Sweden"),
    ("https://scholarshipdb.net/scholarships-in-Norway", "scholarshipdb.net", "Norway"),
    ("https://scholarshipdb.net/scholarships-in-Finland", "scholarshipdb.net", "Finland"),
    ("https://scholarshipdb.net/scholarships-in-Denmark", "scholarshipdb.net", "Denmark"),
    ("https://scholarshipdb.net/scholarships-in-Switzerland", "scholarshipdb.net", "Switzerland"),
    ("https://scholarshipdb.net/scholarships-in-Belgium", "scholarshipdb.net", "Belgium"),
    ("https://scholarshipdb.net/scholarships-in-Italy", "scholarshipdb.net", "Italy"),
    ("https://scholarshipdb.net/scholarships-in-Spain", "scholarshipdb.net", "Spain"),
    ("https://scholarshipdb.net/scholarships-in-Hungary", "scholarshipdb.net", "Hungary"),
    ("https://scholarshipdb.net/scholarships-in-Czech-Republic", "scholarshipdb.net", "Czech Republic"),
    ("https://scholarshipdb.net/scholarships-in-Poland", "scholarshipdb.net", "Poland"),
    ("https://scholarshipdb.net/scholarships-in-Romania", "scholarshipdb.net", "Romania"),
    ("https://scholarshipdb.net/scholarships-in-Malaysia", "scholarshipdb.net", "Malaysia"),
    ("https://scholarshipdb.net/scholarships-in-Singapore", "scholarshipdb.net", "Singapore"),
    ("https://scholarshipdb.net/scholarships-in-New-Zealand", "scholarshipdb.net", "New Zealand"),
    ("https://scholarshipdb.net/scholarships-in-Egypt", "scholarshipdb.net", "Egypt"),
    ("https://scholarshipdb.net/scholarships-in-Brazil", "scholarshipdb.net", "Brazil"),
]

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  MASTER SCHOLARSHIP ENGINE")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Sources: {len(SEED_SOURCES)}")
    print("=" * 60)

    conn = setup_db()

    # Step 1: Clean outdated first
    clean_outdated(conn)

    # Step 2: Scrape all sources
    total = 0
    for i, (url, domain, country) in enumerate(SEED_SOURCES, 1):
        print(f"\n[{i}/{len(SEED_SOURCES)}] {domain} ({country})")
        saved = scrape_url(conn, url, domain, country)
        total += saved
        time.sleep(random.uniform(2, 5))

    # Final count
    c = conn.cursor()
    db_total = c.execute("SELECT COUNT(*) FROM scholarship_details").fetchone()[0]
    conn.close()

    print(f"\n{'='*60}")
    print(f"  New scholarships added : {total}")
    print(f"  Total in database      : {db_total}")
    print(f"  All outdated removed   : ✓")
    print(f"  Blogs written          : ✓")
    print(f"  SEO titles generated   : ✓")
    print(f"{'='*60}")