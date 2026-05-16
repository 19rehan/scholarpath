import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import time
import random
import re
from datetime import datetime

# ─── ROTATING HEADERS ─────────────────────────────────────
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

# ─── SMART FETCH ──────────────────────────────────────────
def smart_fetch(url, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(2, 4))
            r = requests.get(url, headers=get_headers(), timeout=15)
            if r.status_code == 200:
                return r
            print(f"  ⚠ Status {r.status_code} on attempt {attempt+1}")
            time.sleep(random.uniform(4, 8))
        except Exception as e:
            print(f"  ✗ Error: {e}")
            time.sleep(5)
    return None

# ─── DATABASE SETUP ───────────────────────────────────────
def setup_database():
    conn = sqlite3.connect('scholarships.db')
    c = conn.cursor()

    # Main scholarships table (already exists)
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

    # New detailed info table
    c.execute('''
        CREATE TABLE IF NOT EXISTS scholarship_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scholarship_link TEXT UNIQUE,
            title TEXT,
            full_description TEXT,
            eligible_countries TEXT,
            eligible_students TEXT,
            degree_level TEXT,
            deadline TEXT,
            language_requirement TEXT,
            ielts_score TEXT,
            benefits TEXT,
            how_to_apply TEXT,
            blog_post TEXT,
            seo_title TEXT,
            seo_description TEXT,
            last_updated TEXT
        )
    ''')
    conn.commit()
    return conn

# ─── EXTRACT DETAIL FROM SCHOLARSHIP PAGE ─────────────────
def extract_scholarship_details(url, title):
    response = smart_fetch(url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, 'lxml')

    # Remove navigation, footer, ads
    for tag in soup.find_all(['nav', 'footer', 'script', 'style', 'aside']):
        tag.decompose()

    # Get main content
    content = (
        soup.find('article') or
        soup.find('div', class_=lambda c: c and 'content' in str(c).lower()) or
        soup.find('div', class_=lambda c: c and 'post' in str(c).lower()) or
        soup.find('main') or
        soup.find('body')
    )

    full_text = content.get_text(separator=' ', strip=True) if content else ""
    full_text = ' '.join(full_text.split())  # Clean whitespace

    # ── Smart extraction using keywords ──────────────────

    # Deadline
    deadline = "See official website"
    deadline_patterns = [
        r'deadline[:\s]*([A-Za-z]+ \d{1,2},?\s*\d{4})',
        r'closing date[:\s]*([A-Za-z]+ \d{1,2},?\s*\d{4})',
        r'apply by[:\s]*([A-Za-z]+ \d{1,2},?\s*\d{4})',
        r'applications? (close|due)[:\s]*([A-Za-z]+ \d{1,2},?\s*\d{4})',
        r'(\d{1,2} [A-Za-z]+ \d{4})',
        r'([A-Za-z]+ \d{4})',  # fallback: Month Year
    ]
    for pattern in deadline_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            deadline = match.group(1) if match.lastindex == 1 else match.group(2)
            break

    # IELTS / Language requirement
    language_req = "Not specified"
    ielts_score = "Not required"
    if re.search(r'ielts', full_text, re.IGNORECASE):
        ielts_match = re.search(r'ielts[:\s]*(\d+\.?\d*)', full_text, re.IGNORECASE)
        ielts_score = ielts_match.group(1) if ielts_match else "Required (check website)"
        language_req = "IELTS required"
    if re.search(r'pte', full_text, re.IGNORECASE):
        pte_match = re.search(r'pte[:\s]*(\d+)', full_text, re.IGNORECASE)
        pte_score = pte_match.group(1) if pte_match else "Required"
        language_req += f" | PTE: {pte_score}"
    if re.search(r'toefl', full_text, re.IGNORECASE):
        toefl_match = re.search(r'toefl[:\s]*(\d+)', full_text, re.IGNORECASE)
        toefl_score = toefl_match.group(1) if toefl_match else "Required"
        language_req += f" | TOEFL: {toefl_score}"
    if language_req == "Not specified" and re.search(r'english proficiency|english language', full_text, re.IGNORECASE):
        language_req = "English proficiency required (check website)"

    # Eligible countries
    eligible_countries = "Open to international students"
    country_keywords = ['open to', 'eligible countries', 'nationals of', 'citizens of', 'students from']
    for keyword in country_keywords:
        idx = full_text.lower().find(keyword)
        if idx != -1:
            snippet = full_text[idx:idx+200]
            eligible_countries = snippet
            break

    # Degree level
    degree_level = "Not specified"
    levels = []
    if re.search(r'\bbachelor|undergraduate\b', full_text, re.IGNORECASE):
        levels.append("Bachelor's / Undergraduate")
    if re.search(r'\bmaster|postgraduate\b', full_text, re.IGNORECASE):
        levels.append("Master's / Postgraduate")
    if re.search(r'\bphd|doctoral|doctorate\b', full_text, re.IGNORECASE):
        levels.append("PhD / Doctoral")
    if levels:
        degree_level = ", ".join(levels)

    # Benefits / Funding
    benefits = "See official website for full details"
    benefit_keywords = ['covers', 'includes', 'provides', 'award', 'stipend', 'tuition', 'living allowance']
    for keyword in benefit_keywords:
        idx = full_text.lower().find(keyword)
        if idx != -1:
            snippet = full_text[idx:idx+300]
            benefits = snippet
            break

    # How to apply
    how_to_apply = "Visit the official website to apply"
    apply_idx = full_text.lower().find('how to apply')
    if apply_idx != -1:
        how_to_apply = full_text[apply_idx:apply_idx+400]

    return {
        "title": title,
        "full_text": full_text[:3000],
        "deadline": deadline,
        "language_requirement": language_req,
        "ielts_score": ielts_score,
        "eligible_countries": eligible_countries[:500],
        "degree_level": degree_level,
        "benefits": benefits[:500],
        "how_to_apply": how_to_apply[:500],
    }

# ─── AI BLOG WRITER (rule-based, no API needed) ───────────
def write_seo_blog(details, link):
    title = details['title']
    deadline = details['deadline']
    degree = details['degree_level']
    countries = details['eligible_countries']
    ielts = details['ielts_score']
    language = details['language_requirement']
    benefits = details['benefits']
    apply_info = details['how_to_apply']
    year = datetime.now().year

    # SEO Title (under 60 chars is ideal)
    seo_title = f"{title} {year} – Complete Guide & How to Apply"
    if len(seo_title) > 70:
        seo_title = f"{title[:50]}... {year} – Apply Now"

    # SEO Meta Description (under 160 chars)
    seo_desc = (
        f"Complete guide to {title}. Deadline: {deadline}. "
        f"Learn eligibility, IELTS requirements, benefits & how to apply step by step."
    )[:160]

    # Full Blog Post
    blog = f"""# {title} {year} – Complete Guide

**Last Updated:** {datetime.now().strftime("%B %d, %Y")}

---

## What is the {title}?

The **{title}** is one of the exciting scholarship opportunities available for students in {year}. 
This scholarship provides financial support to deserving students who want to pursue their academic 
goals abroad. Whether you are a fresh graduate or an experienced professional looking to upgrade 
your qualifications, this scholarship could be the perfect opportunity for you.

---

## Quick Overview

| Detail | Information |
|--------|------------|
| **Scholarship Name** | {title} |
| **Deadline** | {deadline} |
| **Degree Level** | {degree} |
| **Language Requirement** | {language} |
| **IELTS Score Required** | {ielts} |
| **Last Updated** | {datetime.now().strftime("%B %Y")} |

---

## Who Can Apply? (Eligibility)

{countries}

Students who meet the academic requirements and have a strong desire to study internationally 
are encouraged to apply. Make sure to check the official website for the most updated 
eligibility criteria before applying.

---

## Degree Levels Covered

This scholarship is available for: **{degree}**

Whether you are applying for an undergraduate program, a master's degree, or a doctoral 
program, make sure your intended program qualifies under this scholarship.

---

## Scholarship Benefits

{benefits}

This is a fantastic opportunity to reduce your financial burden while pursuing world-class 
education. The scholarship is designed to cover the essential costs of studying abroad so 
you can focus on your academic performance.

---

## Language Requirements

**IELTS / English Proficiency:** {language}

**IELTS Score Required:** {ielts}

If English is not your first language, you will likely need to prove your English proficiency. 
Here are some tips to meet the requirement:

- Start preparing for IELTS/PTE at least 3 months before the deadline
- Practice reading, writing, listening, and speaking daily
- Take mock tests to assess your current score
- Many universities accept TOEFL or PTE as alternatives to IELTS

---

## How to Apply – Step by Step

{apply_info}

**General application steps:**

1. Visit the official scholarship website (link below)
2. Create an account or register as a new applicant
3. Fill in your personal and academic information carefully
4. Upload required documents (transcripts, passport, language certificates)
5. Write a strong Statement of Purpose (SOP)
6. Submit your application before the deadline: **{deadline}**
7. Keep a copy of your submission confirmation

---

## Documents You Will Need

Most scholarships require the following documents. Prepare them in advance:

- Valid passport (check expiry date)
- Academic transcripts (all previous degrees)
- IELTS / PTE / TOEFL certificate (if required)
- Statement of Purpose (SOP)
- Letters of Recommendation (usually 2-3)
- CV / Resume
- Research proposal (for PhD applicants)
- Proof of admission or acceptance letter (sometimes required)

---

## Tips to Strengthen Your Application

1. **Start early** – Do not wait until the last week before the deadline
2. **Write a compelling SOP** – Explain why you deserve this scholarship specifically
3. **Get strong recommendation letters** – Choose people who know your work well
4. **Double-check eligibility** – Make sure you meet every requirement
5. **Follow instructions exactly** – Many applications are rejected for missing documents

---

## Frequently Asked Questions (FAQ)

**Q: When is the deadline for this scholarship?**
A: The deadline is **{deadline}**. Always verify on the official website as dates can change.

**Q: Is IELTS required for this scholarship?**
A: {ielts}. Check the official requirements as some universities accept alternatives.

**Q: Can Pakistani students apply for this scholarship?**
A: Please check the eligibility section above and verify on the official website.

**Q: How competitive is this scholarship?**
A: Scholarships at this level are competitive. A strong academic record, good SOP, and 
meeting all requirements will significantly improve your chances.

---

## Apply Now

Ready to apply? Visit the official scholarship page for the most accurate and updated 
information:

**Official Link:** {link}

> **Disclaimer:** Scholarship details including deadlines and requirements may change. 
> Always verify information on the official website before applying.
> Last verified: {datetime.now().strftime("%B %d, %Y")}

---

*Found this helpful? Share it with a friend who is also looking for scholarships!*
"""

    return blog, seo_title, seo_desc

# ─── SAVE DETAILS TO DATABASE ─────────────────────────────
def save_details(conn, details, blog, seo_title, seo_desc, link):
    try:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO scholarship_details
            (scholarship_link, title, full_description, eligible_countries,
             eligible_students, degree_level, deadline, language_requirement,
             ielts_score, benefits, how_to_apply, blog_post, seo_title,
             seo_description, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            link,
            details['title'],
            details['full_text'][:1000],
            details['eligible_countries'],
            "International students",
            details['degree_level'],
            details['deadline'],
            details['language_requirement'],
            details['ielts_score'],
            details['benefits'],
            details['how_to_apply'],
            blog,
            seo_title,
            seo_desc,
            datetime.now().strftime("%Y-%m-%d")
        ))
        conn.commit()
    except Exception as e:
        print(f"  ✗ DB error: {e}")

# ─── EXPORT ALL BLOGS TO JSON ──────────────────────────────
def export_blogs(conn):
    print("\n[EXPORT] Saving all blogs to blogs.json ...")
    c = conn.cursor()
    c.execute("SELECT * FROM scholarship_details")
    rows = c.fetchall()
    cols = [d[0] for d in c.description]
    data = [dict(zip(cols, row)) for row in rows]
    with open('blogs.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {len(data)} blog posts saved to blogs.json")
    return len(data)

# ─── MAIN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("   SCHOLARSHIP DETAIL SCRAPER + BLOG GENERATOR")
    print("=" * 55)

    conn = setup_database()
    c = conn.cursor()

    # Load all scholarships from main table
    c.execute("SELECT title, link FROM scholarships WHERE link != '' AND link IS NOT NULL")
    scholarships = c.fetchall()
    print(f"\n  Found {len(scholarships)} scholarships to process\n")

    success = 0
    failed = 0

    for i, (title, link) in enumerate(scholarships, 1):
        print(f"\n[{i}/{len(scholarships)}] {title[:60]}")
        print(f"  URL: {link[:70]}")

        # Skip if already processed today
        c.execute("SELECT last_updated FROM scholarship_details WHERE scholarship_link=?", (link,))
        existing = c.fetchone()
        if existing and existing[0] == datetime.now().strftime("%Y-%m-%d"):
            print("  → Already processed today, skipping")
            success += 1
            continue

        # Extract details
        details = extract_scholarship_details(link, title)
        if not details:
            print("  ✗ Could not fetch page")
            failed += 1
            continue

        # Write blog post
        blog, seo_title, seo_desc = write_seo_blog(details, link)

        # Save to database
        save_details(conn, details, blog, seo_title, seo_desc, link)

        print(f"  ✓ Blog written | Deadline: {details['deadline']} | IELTS: {details['ielts_score']}")
        success += 1

        # Polite delay between requests
        time.sleep(random.uniform(3, 6))

    # Export everything
    total = export_blogs(conn)
    conn.close()

    print(f"\n{'=' * 55}")
    print(f"   SUCCESS: {success} | FAILED: {failed}")
    print(f"   {total} blog posts ready in blogs.json")
    print(f"   Next step: build the website to display these!")
    print(f"{'=' * 55}")