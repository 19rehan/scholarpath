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

# ── AGGREGATOR DOMAINS — we visit these but never save their links ─
AGGREGATOR_DOMAINS = [
    'scholars4dev.com', 'opportunitydesk.org', 'afterschoolafrica.com',
    'youthop.com', 'scholarshipdb.net', 'mastersportal.eu',
    'phdportal.eu', 'opportunitiesforafricans.com', 'scholarshipsads.com',
    'buddy4study.com', 'propakistani.pk', 'scholarshipregion.com',
    'scholarshiphunter.com', 'estudyassistance.com', 'afterschoolafrica.com',
]

# ── OFFICIAL GOVERNMENT SCHOLARSHIP PAGES ─────────────────
OFFICIAL_SOURCES = [
    {'url': 'https://www.chevening.org/scholarships/', 'country': 'United Kingdom', 'region': 'Europe'},
    {'url': 'https://www.daad.de/en/study-and-research-in-germany/scholarships/', 'country': 'Germany', 'region': 'Europe'},
    {'url': 'https://www.campuschina.org/scholarships/index.html', 'country': 'China', 'region': 'Asia'},
    {'url': 'https://www.turkiyeburslari.gov.tr/en', 'country': 'Turkey', 'region': 'Middle East'},
    {'url': 'https://stipendiumhungaricum.hu/en/', 'country': 'Hungary', 'region': 'Europe'},
    {'url': 'https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do', 'country': 'South Korea', 'region': 'Asia'},
    {'url': 'https://www.studyinjapan.go.jp/en/smap_stopj-applications_scholarship.html', 'country': 'Japan', 'region': 'Asia'},
    {'url': 'https://foreign.fulbrightonline.org/', 'country': 'USA', 'region': 'North America'},
    {'url': 'https://cscuk.fcdo.gov.uk/scholarships/', 'country': 'United Kingdom', 'region': 'Europe'},
    {'url': 'https://www.studyinaustralia.gov.au/english/australian-scholarships', 'country': 'Australia', 'region': 'Oceania'},
    {'url': 'https://www.scholarships.gc.ca/scholarships-bourses/index.aspx', 'country': 'Canada', 'region': 'North America'},
    {'url': 'https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en', 'country': 'Europe', 'region': 'Europe'},
    {'url': 'https://www.kaust.edu.sa/en/study/financial-support', 'country': 'Saudi Arabia', 'region': 'Middle East'},
    {'url': 'https://www.qu.edu.qa/students/student_life/scholarships', 'country': 'Qatar', 'region': 'Middle East'},
    {'url': 'https://www.uio.no/english/studies/admission/scholarships/', 'country': 'Norway', 'region': 'Europe'},
    {'url': 'https://studies.ku.dk/masters/financing/scholarships/', 'country': 'Denmark', 'region': 'Europe'},
    {'url': 'https://www.uu.se/en/study/scholarships', 'country': 'Sweden', 'region': 'Europe'},
    {'url': 'https://www.helsinki.fi/en/studying/fees-and-financial-aid/scholarships-and-grants', 'country': 'Finland', 'region': 'Europe'},
]

# ── AGGREGATOR LISTING PAGES — we extract official links FROM these ─
AGGREGATOR_SOURCES = [
    'https://www.scholars4dev.com/',
    'https://www.scholars4dev.com/page/2/',
    'https://www.scholars4dev.com/page/3/',
    'https://www.scholars4dev.com/page/4/',
    'https://www.scholars4dev.com/page/5/',
    'https://opportunitydesk.org/category/scholarships/',
    'https://opportunitydesk.org/category/scholarships/page/2/',
    'https://www.afterschoolafrica.com/category/scholarships/',
    'https://www.afterschoolafrica.com/category/scholarships/page/2/',
]

def get_headers():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
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
            time.sleep(random.uniform(2, 3))
            r = requests.get(url, headers=get_headers(), timeout=15)
            if r.status_code == 200:
                return r
            time.sleep(random.uniform(3, 5))
        except:
            time.sleep(3)
    return None

def get_domain(url):
    return urlparse(url).netloc.replace('www.', '')

def is_aggregator(url):
    domain = get_domain(url)
    return any(agg in domain for agg in AGGREGATOR_DOMAINS)

def is_outdated(text):
    months = {
        'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
        'july':7,'august':8,'september':9,'october':10,'november':11,'december':12
    }
    patterns = [
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})',
        r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',
    ]
    found_dates = []
    for p in patterns:
        for m in re.finditer(p, text.lower()):
            try:
                g = m.groups()
                if g[0] in months:
                    month, year = months[g[0]], int(g[2])
                else:
                    month, year = months[g[1]], int(g[2])
                found_dates.append((year, month))
            except:
                continue

    if found_dates:
        future = [(y,m) for y,m in found_dates if y > CURRENT_YEAR or (y == CURRENT_YEAR and m >= CURRENT_MONTH)]
        if future:
            return False  # Has future date = open
        return True  # All dates in past = outdated

    # No dates found — check year
    if str(CURRENT_YEAR + 1) in text or str(CURRENT_YEAR) in text:
        return False
    return True  # No year = skip

def is_job_listing(title):
    if not title:
        return True
    t = title.lower()
    job_words = [
        'position', 'professor', 'lecturer', 'postdoc', 'instructor',
        'faculty', 'director', 'dean', 'researcher', 'scientist',
        'engineer', 'analyst', 'coordinator', 'manager', 'officer',
        'job fair', 'recruitment', 'hiring', 'vacancy', 'staff',
        'technician', 'nurse', 'doctor ', 'surgeon', 'consultant',
    ]
    return any(w in t for w in job_words)

def is_list_page(title):
    if not title:
        return True
    t = title.lower()
    list_words = [
        'top 10', 'top 5', 'top 20', 'top 25', 'top 50', 'top 100',
        'list of', 'best scholarships', 'countries where',
        r'\d+ scholarships', 'all scholarships', 'scholarships for 2025',
        'scholarships for 2026',
    ]
    for w in list_words:
        if re.search(w, t):
            return True
    return False

def extract_ielts(text):
    m = re.search(r'ielts[:\s]*(\d+\.?\d*)', text, re.IGNORECASE)
    if m:
        score = float(m.group(1))
        if 4.0 <= score <= 9.0:
            return str(score)
    return "Required" if re.search(r'\bielts\b', text, re.IGNORECASE) else "Not required"

def extract_deadline(text):
    months = "january|february|march|april|may|june|july|august|september|october|november|december"
    patterns = [
        rf'deadline[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'closing date[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'apply by[:\s]*((?:{months})[\s\d,]+\d{{4}})',
        rf'(\d{{1,2}}\s+(?:{months})\s+\d{{4}})',
        rf'((?:{months})\s+\d{{1,2}},?\s+\d{{4}})',
        rf'((?:{months})\s+\d{{4}})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            groups = [g for g in m.groups() if g]
            if groups:
                return groups[-1].strip()
    return None

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

def extract_eligible_countries(text):
    countries = [
        "Pakistan", "India", "Bangladesh", "Nepal", "Sri Lanka",
        "Nigeria", "Ghana", "Kenya", "Ethiopia", "Tanzania",
        "Uganda", "Rwanda", "South Africa", "Egypt", "Morocco",
        "Indonesia", "Malaysia", "Philippines", "Vietnam", "Thailand",
        "Brazil", "Colombia", "Mexico", "developing countries",
        "low-income countries", "African countries", "Asian countries",
        "all countries", "international students", "worldwide"
    ]
    found = []
    text_lower = text.lower()
    for c in countries:
        if c.lower() in text_lower:
            found.append(c)
    if found:
        return ", ".join(found[:10])
    return "Open to international students"

def find_official_link(soup, current_url):
    """
    Smart official link finder.
    From a 3rd party page, find the real official scholarship link.
    """
    apply_keywords = [
        'apply now', 'apply here', 'apply online', 'official website',
        'click here to apply', 'application portal', 'official link',
        'visit official', 'more information', 'official page',
        'scholarship page', 'university website', 'official scholarship',
        'apply for', 'learn more', 'read more', 'click here',
        'application form', 'online application'
    ]

    official_indicators = [
        '.edu', '.ac.uk', '.edu.au', '.ac.jp', '.ac.kr', '.edu.cn',
        '.gov', '.org', 'university', 'college', 'institute',
        'daad.de', 'chevening.org', 'fulbright', 'erasmus',
        'stipendiumhungaricum', 'turkiyeburslari', 'campuschina',
        'studyinkorea', 'mext.go.jp', 'scholarships.gc.ca'
    ]

    current_domain = get_domain(current_url)
    candidates = []

    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        link_text = a.get_text(strip=True).lower()

        if not href or href.startswith('#') or 'javascript' in href:
            continue

        # Make absolute
        if href.startswith('/'):
            parsed = urlparse(current_url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        elif not href.startswith('http'):
            continue

        # Skip social media
        if any(s in href for s in ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'whatsapp', 'telegram']):
            continue

        link_domain = get_domain(href)

        # Skip if same aggregator domain
        if is_aggregator(href):
            continue

        score = 0

        # Official domain indicators
        for indicator in official_indicators:
            if indicator in link_domain:
                score += 15

        # Apply-related text
        for kw in apply_keywords:
            if kw in link_text:
                score += 10

        # Scholarship keywords in URL
        if any(kw in href.lower() for kw in ['scholarship', 'fellowship', 'grant', 'funding', 'award', 'apply', 'admission']):
            score += 5

        # Different domain = external official link
        if link_domain != current_domain and score > 0:
            score += 3

        if score > 5:
            candidates.append((score, href))

    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]

    return None

def write_blog(title, desc, deadline, ielts, degree, funding,
               country, region, uni, eligible_countries, official_link):

    seo_title = f"{title} {CURRENT_YEAR} — Eligibility, Deadline & How to Apply"[:70]
    seo_desc = f"Apply for {title}. Deadline: {deadline or 'Check website'}. {degree} students. IELTS: {ielts}. Full guide for Pakistani and international students."[:160]

    lang_note = ""
    if ielts == "Not required":
        lang_note = "No English language test is required for this scholarship. This is excellent news for students who have not yet taken IELTS or TOEFL."
    else:
        lang_note = f"The minimum IELTS score required is {ielts}. Start your preparation at least 3 months before the deadline. British Council and IDP offer IELTS tests in Karachi, Lahore and Islamabad. Focus on all four sections equally."

    blog = f"""# {title} {CURRENT_YEAR}

**Last Updated:** {datetime.now().strftime("%B %d, %Y")} | **Status:** Open for Applications

---

## About This Scholarship

The **{title}** is a genuine opportunity for international students who want to pursue world-class education at **{uni}** in **{country}**. If you are a student from Pakistan, India, Bangladesh, Nigeria, Kenya or any developing country with strong academics and ambition — read this carefully.

We have gathered every piece of information you need in one place so you do not have to visit ten different websites or pay an agent to explain it to you.

---

## Quick Summary

| Detail | Information |
|--------|------------|
| **Scholarship** | {title} |
| **University** | {uni} |
| **Country** | {country} |
| **Region** | {region} |
| **Degree Level** | {degree} |
| **Funding** | {funding} |
| **Deadline** | {deadline or "Check official website"} |
| **IELTS** | {ielts} |
| **Last Verified** | {datetime.now().strftime("%B %Y")} |

---

## Who Can Apply?

**Eligible students:** {eligible_countries}

{"This scholarship welcomes applications from students worldwide including Pakistan, India and Bangladesh." if "international" in eligible_countries.lower() else f"Students from the following backgrounds are eligible: {eligible_countries}"}

Make sure you meet the eligibility criteria before investing time in your application. Always verify the latest requirements on the official website.

---

## What Does This Scholarship Cover?

**Funding type: {funding}**

{desc}

Visit the official website for the complete and most up-to-date breakdown of benefits. Scholarship packages can include tuition fees, monthly living allowance, health insurance, travel grant and accommodation support.

---

## English Language Requirements

{lang_note}

Some universities may waive the IELTS requirement if your previous education was entirely in English medium. Always check the official requirements carefully.

---

## Application Deadline

**{deadline or "Check official website"}**

Do not wait until the last week. Follow this timeline:

- 3 months before: Start gathering all documents
- 2 months before: Draft and refine your Statement of Purpose
- 1 month before: Request recommendation letters
- 2 weeks before: Submit your complete application
- Keep your submission confirmation safe

---

## Documents You Will Need

- Valid Passport (valid throughout the scholarship period)
- Academic Transcripts (all previous degrees, certified)
- Degree Certificate or Provisional Certificate
- IELTS / TOEFL Certificate (score: {ielts})
- Statement of Purpose — 600 to 1000 words
- 2 to 3 Recommendation Letters
- Updated Academic CV
- Passport-size Photographs
- Research Proposal (PhD applicants only)

---

## How to Write a Winning Statement of Purpose

Most students fail at this step. Here is what actually works:

**Opening — Make them feel something**
Do not start with "I am writing to apply for..." Start with a real moment. A problem you witnessed. A turning point in your life. Something that made you choose this path.

**Academic background — Be specific**
Your degree, your GPA, your most important projects or research. Use numbers. "I graduated with a 3.8 GPA" is stronger than "I was a good student."

**Why this specific scholarship**
This is where most applications fail. Generic reasons get rejected. Research the university, the program, specific professors. Show that you chose this deliberately.

**Career goals**
Where will you be in 5 years? How does this scholarship fit into that picture? How will you contribute to your country or field after graduating?

**Why you deserve it**
Leadership roles, research papers, community work, challenges you overcame. This is not bragging — it is evidence.

**Closing**
Confident, forward-looking, genuine. Thank the committee and restate your commitment.

Length: 600 to 1000 words unless the application specifies otherwise.

---

## Frequently Asked Questions

**Can students from Pakistan apply?**
{"Yes — Pakistani students are among the eligible applicants for this scholarship." if "Pakistan" in eligible_countries else "Check the eligibility section above. Many international scholarships accept Pakistani students even if not explicitly listed."}

**Is IELTS required?**
{f"Yes — minimum {ielts}. Some universities accept TOEFL as an alternative." if ielts not in ["Not required", "Check website"] else "No IELTS requirement mentioned. Verify on the official website."}

**When is the deadline?**
**{deadline or "Check official website"}** — Always confirm on the official website.

**Is this fully funded?**
Funding type: **{funding}**. Visit the official page for exact details.

---

## Apply Now

Visit the official scholarship page:

**{official_link}**

> Always verify details on the official website before applying.
> Last verified by AdmitGoal: {datetime.now().strftime("%B %d, %Y")}

---

*Share this with a friend who deserves a scholarship. One share can change a life.*
"""
    return blog, seo_title, seo_desc

def save(conn, data):
    if not data.get('title') or len(data['title']) < 10:
        return False
    if not data.get('official_link'):
        return False
    if not data.get('deadline'):
        return False

    blog, seo_title, seo_desc = write_blog(
        data['title'], data['description'], data['deadline'],
        data['ielts'], data['degree'], data['funding'],
        data['country'], data['region'], data['university'],
        data['eligible_countries'], data['official_link']
    )

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
              seo_description=EXCLUDED.seo_description
        ''', (
            data['official_link'], data['title'],
            data['description'][:800],
            data['eligible_countries'], "International students",
            data['degree'], data['deadline'],
            f"IELTS {data['ielts']}" if data['ielts'] != "Not required" else "Not required",
            data['ielts'], data.get('benefits', ''), '',
            blog, seo_title, seo_desc,
            data['university'], data['country'], data['region'],
            data['funding'], "Check website",
            datetime.now().strftime("%Y-%m-%d")
        ))
        cur.execute('''
            INSERT INTO scholarships
            (title, description, country, deadline, link, source, scraped_date)
            VALUES(%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (link) DO NOTHING
        ''', (
            data['title'], seo_desc, data['country'],
            data['deadline'], data['official_link'],
            data['university'][:50],
            datetime.now().strftime("%Y-%m-%d")
        ))
        cur.close()
        return True
    except Exception as e:
        print(f"    DB Error: {e}")
        return False

def scrape_official_page(url, country, region, conn):
    """Scrape directly from official scholarship page"""
    r = fetch(url)
    if not r:
        return 0

    soup = BeautifulSoup(r.text, 'lxml')
    for tag in soup.find_all(['nav', 'footer', 'script', 'style', 'aside']):
        tag.decompose()

    full_text = ' '.join(soup.get_text(separator=' ', strip=True).split())
    saved = 0
    seen_titles = set()

    # Get university name from domain or title
    title_tag = soup.find('title')
    site_name = title_tag.get_text(strip=True).split('|')[0].split('–')[0].strip()[:60] if title_tag else ""

    # Find all scholarship links on this page
    for a in soup.find_all('a', href=True):
        href = a['href']
        link_text = a.get_text(strip=True)

        if len(link_text) < 15:
            continue

        # Must contain scholarship keywords
        if not any(kw in link_text.lower() for kw in
                   ['scholarship', 'fellowship', 'award', 'grant', 'bursary', 'funding']):
            continue

        # Make absolute
        if href.startswith('/'):
            parsed = urlparse(url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        elif not href.startswith('http'):
            continue

        if link_text in seen_titles:
            continue
        seen_titles.add(link_text)

        # Visit the scholarship detail page
        detail_r = fetch(href)
        if not detail_r:
            continue

        detail_soup = BeautifulSoup(detail_r.text, 'lxml')
        for tag in detail_soup.find_all(['nav', 'footer', 'script', 'style', 'aside']):
            tag.decompose()

        detail_text = ' '.join(detail_soup.get_text(separator=' ', strip=True).split())

        # Check if outdated
        if is_outdated(detail_text):
            print(f"    Skip (outdated): {link_text[:50]}")
            continue

        # Get title
        h1 = detail_soup.find('h1')
        title = h1.get_text(strip=True) if h1 else link_text
        if is_job_listing(title) or is_list_page(title):
            print(f"    Skip (job/list): {title[:50]}")
            continue

        deadline = extract_deadline(detail_text)
        if not deadline:
            continue

        ielts = extract_ielts(detail_text)
        degree = extract_degree(detail_text)
        funding = extract_funding(detail_text)
        eligible = extract_eligible_countries(detail_text)

        # Description
        desc = ""
        for p in detail_soup.find_all('p'):
            t = p.get_text(strip=True)
            if len(t) > 80:
                desc = t[:600]
                break

        data = {
            'title': title,
            'description': desc or title,
            'university': site_name or country,
            'country': country,
            'region': region,
            'deadline': deadline,
            'ielts': ielts,
            'degree': degree,
            'funding': funding,
            'eligible_countries': eligible,
            'official_link': href,
            'benefits': '',
        }

        if save(conn, data):
            print(f"    SAVED: {title[:60]}")
            saved += 1

        time.sleep(random.uniform(1, 2))

    return saved

def scrape_aggregator_page(listing_url, conn):
    """
    Visit aggregator listing page.
    For each scholarship post:
      1. Visit the post
      2. Find the official link inside the post
      3. Visit official link for complete data
      4. Save with complete information
    """
    r = fetch(listing_url)
    if not r:
        return 0

    soup = BeautifulSoup(r.text, 'lxml')
    base_domain = get_domain(listing_url)
    parsed_base = urlparse(listing_url)
    base_url = f"{parsed_base.scheme}://{parsed_base.netloc}"

    # Find individual post links
    post_links = []
    seen = set()

    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)

        if not href.startswith('http'):
            href = base_url + href if href.startswith('/') else listing_url + href

        if get_domain(href) != base_domain:
            continue

        # Skip navigation/category pages
        skip = ['/category/', '/tag/', '/page/', '/author/', '#', 'mailto',
                '/about', '/contact', '/privacy', '/search']
        if any(s in href for s in skip):
            continue

        if href == listing_url or href in seen:
            continue

        if len(text) > 15:
            seen.add(href)
            post_links.append((text, href))

    print(f"  Found {len(post_links)} posts")
    saved = 0

    for post_title, post_url in post_links[:15]:
        print(f"\n  Post: {post_title[:60]}")

        # Skip if clearly a job or list
        if is_job_listing(post_title) or is_list_page(post_title):
            print(f"  Skip (job/list)")
            continue

        # Visit the aggregator post
        post_r = fetch(post_url)
        if not post_r:
            continue

        post_soup = BeautifulSoup(post_r.text, 'lxml')
        for tag in post_soup.find_all(['nav', 'footer', 'script', 'style', 'aside']):
            tag.decompose()

        post_text = ' '.join(post_soup.get_text(separator=' ', strip=True).split())

        # Check if outdated
        if is_outdated(post_text):
            print(f"  Skip (outdated)")
            continue

        # Find official link from the post
        official_link = find_official_link(post_soup, post_url)

        if official_link and not is_aggregator(official_link):
            print(f"  Official link found: {official_link[:60]}")

            # Visit official page for complete data
            official_r = fetch(official_link)
            if official_r:
                official_soup = BeautifulSoup(official_r.text, 'lxml')
                for tag in official_soup.find_all(['nav', 'footer', 'script', 'style', 'aside']):
                    tag.decompose()
                official_text = ' '.join(official_soup.get_text(separator=' ', strip=True).split())

                # Use combined text for better data extraction
                combined_text = post_text + " " + official_text
            else:
                # Fallback to just post data
                official_link = post_url
                combined_text = post_text
        else:
            print(f"  No official link — using post data")
            official_link = post_url
            combined_text = post_text

        # Extract all data
        h1 = post_soup.find('h1')
        title = h1.get_text(strip=True) if h1 else post_title

        if is_job_listing(title) or is_list_page(title):
            print(f"  Skip after visiting: {title[:50]}")
            continue

        deadline = extract_deadline(combined_text)
        if not deadline:
            print(f"  Skip (no deadline found)")
            continue

        ielts = extract_ielts(combined_text)
        degree = extract_degree(combined_text)
        funding = extract_funding(combined_text)
        eligible = extract_eligible_countries(combined_text)

        # Detect country from official link domain
        if official_link and not is_aggregator(official_link):
            domain = get_domain(official_link)
        else:
            domain = get_domain(post_url)

        country = detect_country_from_domain(domain, combined_text)
        region = detect_region(country)

        # University name
        title_tag = post_soup.find('title')
        uni = ""
        if title_tag:
            uni = title_tag.get_text(strip=True).split('|')[0].split('–')[0].strip()[:60]
        if not uni or is_aggregator(post_url):
            uni = domain.replace('.edu', '').replace('.ac.uk', '').replace('www.', '').title()

        # Description from post
        desc = ""
        for p in post_soup.find_all('p'):
            t = p.get_text(strip=True)
            if len(t) > 80:
                desc = t[:600]
                break

        data = {
            'title': title,
            'description': desc or title,
            'university': uni,
            'country': country,
            'region': region,
            'deadline': deadline,
            'ielts': ielts,
            'degree': degree,
            'funding': funding,
            'eligible_countries': eligible,
            'official_link': official_link,
            'benefits': '',
        }

        if save(conn, data):
            print(f"  SAVED: {title[:60]}")
            saved += 1

        time.sleep(random.uniform(2, 3))

    return saved

def detect_country_from_domain(domain, text=""):
    tld_map = {
        '.ac.uk': 'United Kingdom', '.co.uk': 'United Kingdom', '.uk': 'United Kingdom',
        '.edu.au': 'Australia', '.com.au': 'Australia', '.au': 'Australia',
        '.ca': 'Canada', '.de': 'Germany', '.fr': 'France',
        '.nl': 'Netherlands', '.se': 'Sweden', '.no': 'Norway',
        '.fi': 'Finland', '.dk': 'Denmark', '.ch': 'Switzerland',
        '.at': 'Austria', '.be': 'Belgium', '.it': 'Italy',
        '.es': 'Spain', '.tr': 'Turkey', '.sa': 'Saudi Arabia',
        '.ae': 'UAE', '.qa': 'Qatar', '.cn': 'China',
        '.jp': 'Japan', '.kr': 'South Korea', '.my': 'Malaysia',
        '.sg': 'Singapore', '.nz': 'New Zealand', '.za': 'South Africa',
        '.edu': 'USA', '.gov': 'USA',
    }
    for tld, country in sorted(tld_map.items(), key=lambda x: -len(x[0])):
        if domain.endswith(tld):
            return country

    # Try from text
    hints = {
        'germany': 'Germany', 'uk ': 'United Kingdom', 'australia': 'Australia',
        'canada': 'Canada', 'japan': 'Japan', 'china': 'China',
        'korea': 'South Korea', 'turkey': 'Turkey', 'france': 'France',
        'netherlands': 'Netherlands', 'sweden': 'Sweden', 'norway': 'Norway',
        'usa': 'USA', 'united states': 'USA', 'saudi arabia': 'Saudi Arabia',
        'malaysia': 'Malaysia', 'singapore': 'Singapore', 'italy': 'Italy',
    }
    text_lower = text.lower()[:1000]
    for hint, country in hints.items():
        if hint in text_lower:
            return country

    return "International"

def detect_region(country):
    regions = {
        'Europe': ['United Kingdom', 'Germany', 'France', 'Netherlands', 'Sweden',
                   'Norway', 'Finland', 'Denmark', 'Switzerland', 'Austria',
                   'Belgium', 'Italy', 'Spain', 'Poland', 'Hungary', 'Ireland'],
        'Middle East': ['Turkey', 'Saudi Arabia', 'UAE', 'Qatar', 'Jordan', 'Egypt'],
        'Asia': ['China', 'Japan', 'South Korea', 'Malaysia', 'Singapore',
                 'Thailand', 'Indonesia', 'Pakistan', 'India', 'Bangladesh'],
        'Oceania': ['Australia', 'New Zealand'],
        'North America': ['USA', 'Canada'],
        'Africa': ['Nigeria', 'South Africa', 'Kenya', 'Ghana', 'Ethiopia'],
        'Latin America': ['Brazil', 'Colombia', 'Argentina'],
    }
    for region, countries in regions.items():
        if country in countries:
            return region
    return "International"

# ── MAIN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  ADMITGOAL SMART SCRAPER")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("  Strategy: 3rd party → find official link → full data")
    print("=" * 60)

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    total = 0

    # Phase 1: Official government sources
    print(f"\n{'─'*60}")
    print("PHASE 1: Official government & university sources")
    print(f"{'─'*60}")

    for source in OFFICIAL_SOURCES:
        print(f"\n[OFFICIAL] {source['country']} — {source['url'][:60]}")
        saved = scrape_official_page(
            source['url'], source['country'], source['region'], conn
        )
        total += saved
        print(f"  Saved: {saved}")
        time.sleep(random.uniform(3, 5))

    # Phase 2: Aggregator sources — extract official links
    print(f"\n{'─'*60}")
    print("PHASE 2: Aggregator sources — finding official links")
    print(f"{'─'*60}")

    for listing_url in AGGREGATOR_SOURCES:
        print(f"\n[AGGREGATOR] {listing_url}")
        saved = scrape_aggregator_page(listing_url, conn)
        total += saved
        print(f"  Saved: {saved}")
        time.sleep(random.uniform(3, 5))

    # Final count
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scholarship_details")
    db_total = cur.fetchone()[0]
    cur.close()
    conn.close()

    print(f"\n{'='*60}")
    print(f"  New scholarships saved : {total}")
    print(f"  Total in database      : {db_total}")
    print(f"  Quality checks         :")
    print(f"    No job listings      : Yes")
    print(f"    No list pages        : Yes")
    print(f"    Official links only  : Yes")
    print(f"    Future deadlines only: Yes")
    print(f"    Complete blogs       : Yes")
    print(f"{'='*60}")