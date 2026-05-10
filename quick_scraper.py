import requests
from bs4 import BeautifulSoup
import psycopg2
import psycopg2.extras
import os
import time
import random
import re
from datetime import datetime

CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month

# ── PUT YOUR SUPABASE URL HERE ─────────────────────────────
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:YOURPASSWORD@db.YOURPROJECT.supabase.co:5432/postgres'
)

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

def fetch(url):
    try:
        time.sleep(random.uniform(2, 3))
        r = requests.get(url, headers=get_headers(), timeout=12)
        return r if r.status_code == 200 else None
    except:
        return None

def is_open(text):
    text_lower = text.lower()
    closed = ['applications are closed', 'deadline has passed',
              'no longer accepting', 'competition is closed']
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
    ]
    for pattern in patterns:
        for m in re.finditer(pattern, text_lower):
            try:
                g = m.groups()
                if g[0] in months:
                    month, year = months[g[0]], int(g[2])
                else:
                    month, year = months[g[1]], int(g[2])
                if year > CURRENT_YEAR: return True
                if year == CURRENT_YEAR and month >= CURRENT_MONTH: return True
                if year == CURRENT_YEAR and month < CURRENT_MONTH: return False
            except:
                continue
    if str(CURRENT_YEAR + 1) in text: return True
    if str(CURRENT_YEAR) in text: return True
    return True

def extract_ielts(text):
    m = re.search(r'ielts[:\s]*(\d+\.?\d*)', text, re.IGNORECASE)
    if m: return m.group(1)
    return "Required" if re.search(r'ielts', text, re.IGNORECASE) else "Not required"

def extract_deadline(text):
    months = "january|february|march|april|may|june|july|august|september|october|november|december"
    for p in [
        rf'deadline[:\s]*((?:{months})[\s\d,]+\d{{4}})',
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
    if re.search(r'full.?fund|fully.?fund|full scholarship', text, re.IGNORECASE):
        return "Fully Funded"
    if re.search(r'partial|tuition only', text, re.IGNORECASE):
        return "Partial"
    return "Check website"

def write_blog(title, desc, deadline, ielts, degree, funding, country, uni, link):
    seo_title = f"{title} {CURRENT_YEAR} – Eligibility, Deadline & How to Apply"[:70]
    seo_desc = f"Apply for {title}. Deadline: {deadline}. {degree} level. IELTS: {ielts}. Full guide for Pakistani and international students."[:160]
    blog = f"""# {title} {CURRENT_YEAR}

**Last Updated:** {datetime.now().strftime("%B %d, %Y")} | **Status:** Open

---

## Overview

The **{title}** is offered by **{uni}** in **{country}**. This is a great opportunity for international students including those from Pakistan, India, Bangladesh and Africa.

---

## Quick Summary

| Detail | Info |
|--------|------|
| **University** | {uni} |
| **Country** | {country} |
| **Degree** | {degree} |
| **Funding** | {funding} |
| **Deadline** | {deadline} |
| **IELTS** | {ielts} |
| **Updated** | {datetime.now().strftime("%B %Y")} |

---

## Description

{desc}

---

## English Language Requirement

**IELTS:** {ielts}

{"No English test required — great for students who have not yet taken IELTS." if ielts == "Not required" else f"Minimum IELTS score required: {ielts}. Start preparation at least 3 months before the deadline. British Council and IDP offer IELTS in Karachi, Lahore and Islamabad."}

---

## How to Apply

1. Visit the official scholarship website
2. Read all eligibility requirements carefully
3. Prepare your documents in advance
4. Write a strong Statement of Purpose
5. Submit before the deadline: **{deadline}**

---

## Documents Required

- Valid Passport
- Academic Transcripts
- IELTS Certificate (if required)
- Statement of Purpose (SOP)
- 2 Recommendation Letters
- Updated CV

---

## SOP Tips

1. Start with a strong personal story
2. Explain your academic background and GPA
3. State clearly why you want this scholarship
4. Describe your career goals
5. Keep it 600 to 1000 words

---

## FAQ

**Can Pakistani students apply?**
Most international scholarships welcome Pakistani students. Verify on the official website.

**Deadline?**
{deadline} — always confirm on official website.

**Is IELTS required?**
{ielts}

---

## Apply Now

Visit the official page: {link}

> Last verified: {datetime.now().strftime("%B %d, %Y")}
"""
    return blog, seo_title, seo_desc

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

def clean_outdated(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, scholarship_link, deadline FROM scholarship_details")
    rows = cur.fetchall()
    removed = 0
    months = {
        'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
        'july':7,'august':8,'september':9,'october':10,'november':11,'december':12
    }
    for sid, link, deadline in rows:
        if not deadline or deadline == 'See official website':
            continue
        dl = deadline.lower()
        year_m = re.search(r'(\d{4})', dl)
        if not year_m: continue
        year = int(year_m.group(1))
        expired = False
        if year < CURRENT_YEAR:
            expired = True
        elif year == CURRENT_YEAR:
            for month_name, month_num in months.items():
                if month_name in dl:
                    if month_num < CURRENT_MONTH - 1:
                        expired = True
                    break
        if expired:
            cur.execute("DELETE FROM scholarship_details WHERE id=%s", (sid,))
            cur.execute("DELETE FROM scholarships WHERE link=%s", (link,))
            removed += 1
    cur.close()
    print(f"  Removed {removed} outdated scholarships")

def save(conn, title, desc, deadline, ielts, degree,
         funding, country, region, uni, link, source):
    if not title or len(title) < 8 or not link:
        return False
    blog, seo_title, seo_desc = write_blog(
        title, desc, deadline, ielts, degree, funding, country, uni, link)
    lang = f"IELTS {ielts}" if ielts not in ["Not required","Check website"] else ielts
    try:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO scholarship_details
            (scholarship_link,title,full_description,eligible_countries,
             eligible_students,degree_level,deadline,language_requirement,
             ielts_score,benefits,how_to_apply,blog_post,seo_title,
             seo_description,university_name,country,region,
             funding_type,gpa_required,last_updated)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (scholarship_link) DO UPDATE SET
              deadline=EXCLUDED.deadline,
              last_updated=EXCLUDED.last_updated,
              blog_post=EXCLUDED.blog_post,
              seo_title=EXCLUDED.seo_title,
              seo_description=EXCLUDED.seo_description
        ''', (link, title, desc[:600], "International students",
              "International students", degree, deadline, lang,
              ielts, "", "", blog, seo_title, seo_desc,
              uni, country, region, funding, "Check website",
              datetime.now().strftime("%Y-%m-%d")))
        cur.execute('''
            INSERT INTO scholarships
            (title,description,country,deadline,link,source,scraped_date)
            VALUES(%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (link) DO NOTHING
        ''', (title, seo_desc, country, deadline, link, source,
              datetime.now().strftime("%Y-%m-%d")))
        cur.close()
        return True
    except Exception as e:
        print(f"  ✗ Save error: {e}")
        return False

FAST_SOURCES = [
    ("https://www.scholars4dev.com/", "International"),
    ("https://www.scholars4dev.com/page/2/", "International"),
    ("https://www.scholars4dev.com/page/3/", "International"),
    ("https://scholarshipdb.net/scholarships-in-Germany", "Germany"),
    ("https://scholarshipdb.net/scholarships-in-United-Kingdom", "UK"),
    ("https://scholarshipdb.net/scholarships-in-China", "China"),
    ("https://scholarshipdb.net/scholarships-in-Turkey", "Turkey"),
    ("https://scholarshipdb.net/scholarships-in-South-Korea", "South Korea"),
    ("https://scholarshipdb.net/scholarships-in-Japan", "Japan"),
    ("https://scholarshipdb.net/scholarships-in-Australia", "Australia"),
    ("https://scholarshipdb.net/scholarships-in-Canada", "Canada"),
    ("https://scholarshipdb.net/scholarships-in-Saudi-Arabia", "Saudi Arabia"),
    ("https://scholarshipdb.net/scholarships-in-Netherlands", "Netherlands"),
    ("https://scholarshipdb.net/scholarships-in-Hungary", "Hungary"),
    ("https://scholarshipdb.net/scholarships-in-Malaysia", "Malaysia"),
    ("https://scholarshipdb.net/scholarships-in-Norway", "Norway"),
    ("https://scholarshipdb.net/scholarships-in-Italy", "Italy"),
    ("https://scholarshipdb.net/scholarships-in-France", "France"),
    ("https://scholarshipdb.net/scholarships-in-Sweden", "Sweden"),
    ("https://scholarshipdb.net/scholarships-in-Finland", "Finland"),
]

REGION_MAP = {
    'Germany':'Europe','UK':'Europe','France':'Europe','Netherlands':'Europe',
    'Sweden':'Europe','Norway':'Europe','Finland':'Europe','Italy':'Europe',
    'Hungary':'Europe','Belgium':'Europe','Switzerland':'Europe',
    'China':'Asia','Japan':'Asia','South Korea':'Asia','Malaysia':'Asia',
    'Singapore':'Asia','Turkey':'Middle East','Saudi Arabia':'Middle East',
    'UAE':'Middle East','Qatar':'Middle East','Australia':'Oceania',
    'New Zealand':'Oceania','Canada':'North America','USA':'North America',
    'International':'International',
}

if __name__ == "__main__":
    print("="*55)
    print("  QUICK SCRAPER — Supabase Mode")
    print(f"  Target: fresh open scholarships")
    print("="*55)

    conn = get_db()

    print("\n[1] Cleaning outdated scholarships...")
    clean_outdated(conn)

    print(f"\n[2] Scraping {len(FAST_SOURCES)} sources...")
    total = 0

    for url, country in FAST_SOURCES:
        if total >= 80: break
        print(f"\n  → {url.split('/')[2]} ({country})")
        r = fetch(url)
        if not r:
            print("  ✗ Skipped")
            continue

        soup = BeautifulSoup(r.text, 'lxml')
        for tag in soup.find_all(['nav','footer','script','style']):
            tag.decompose()

        region = REGION_MAP.get(country, 'International')
        seen = set()
        items = []

        for h in soup.find_all(['h2','h3']):
            text = h.get_text(strip=True)
            a = h.find('a', href=True)
            if a and len(text) > 12:
                href = a['href']
                if not href.startswith('http'):
                    href = 'https://' + url.split('/')[2] + href
                items.append((text, href))

        for a in soup.find_all('a', href=True):
            text = a.get_text(strip=True)
            href = a['href']
            if len(text) < 15: continue
            if any(kw in text.lower() for kw in
                   ['scholarship','fellowship','award','grant','bursary']):
                if not href.startswith('http'):
                    href = 'https://' + url.split('/')[2] + href
                items.append((text, href))

        for title, link in items:
            if title in seen or total >= 80: break
            seen.add(title)

            dr = fetch(link)
            if not dr: continue
            dtext = BeautifulSoup(dr.text, 'lxml').get_text(separator=' ', strip=True)

            if not is_open(dtext):
                print(f"  ✗ Expired: {title[:50]}")
                continue

            deadline = extract_deadline(dtext)
            ielts = extract_ielts(dtext)
            degree = extract_degree(dtext)
            funding = extract_funding(dtext)

            dsoup = BeautifulSoup(dr.text, 'lxml')
            desc = ""
            for p in dsoup.find_all('p'):
                t = p.get_text(strip=True)
                if len(t) > 60:
                    desc = t[:500]
                    break
            desc = desc or title

            pt = dsoup.find('title')
            uni = pt.get_text(strip=True).split('|')[0].split('–')[0].strip()[:60] if pt else country

            ok = save(conn, title, desc, deadline, ielts, degree,
                     funding, country, region, uni, link,
                     url.split('/')[2])
            if ok:
                print(f"  ✓ [{deadline}] {title[:55]}")
                total += 1

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scholarship_details")
    db_total = cur.fetchone()[0]
    cur.close()
    conn.close()

    print(f"\n{'='*55}")
    print(f"  Fresh scholarships added : {total}")
    print(f"  Total in Supabase        : {db_total}")
    print(f"  Outdated removed         : ✓")
    print(f"{'='*55}")