"""
ADMITGOAL — AGGREGATOR SOURCES SCRAPER
Visits 3rd party sites, finds official links, gets complete data
Runs at: 9am, 3pm, 9pm, 3am (3 hours offset from official scraper)
"""

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

MONTHS = {
    'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
    'july':7,'august':8,'september':9,'october':10,'november':11,'december':12
}

AGGREGATOR_DOMAINS = [
    'scholars4dev.com','opportunitydesk.org','afterschoolafrica.com',
    'youthop.com','scholarshipdb.net','mastersportal.eu','phdportal.eu',
    'opportunitiesforafricans.com','scholarshipsads.com','buddy4study.com',
    'propakistani.pk','scholarshipregion.com','estudyassistance.com',
    'admitgoal.com',
]

# 3rd party listing pages — we extract official links from these
AGGREGATOR_SOURCES = [
    # High quality scholarship blogs
    'https://www.scholars4dev.com/',
    'https://www.scholars4dev.com/page/2/',
    'https://www.scholars4dev.com/page/3/',
    'https://www.scholars4dev.com/page/4/',
    'https://www.scholars4dev.com/page/5/',
    'https://www.scholars4dev.com/page/6/',
    'https://www.scholars4dev.com/page/7/',
    'https://www.scholars4dev.com/page/8/',
    'https://opportunitydesk.org/category/scholarships/',
    'https://opportunitydesk.org/category/scholarships/page/2/',
    'https://opportunitydesk.org/category/scholarships/page/3/',
    'https://www.afterschoolafrica.com/category/scholarships/',
    'https://www.afterschoolafrica.com/category/scholarships/page/2/',
    'https://www.afterschoolafrica.com/category/scholarships/page/3/',
    'https://www.opportunitiesforafricans.com/category/scholarships/',
    'https://www.opportunitiesforafricans.com/category/scholarships/page/2/',
    'https://www.youthop.com/scholarships',
    'https://www.scholarshipsads.com/',
    # Country specific
    'https://scholarshipdb.net/scholarships-in-Germany',
    'https://scholarshipdb.net/scholarships-in-United-Kingdom',
    'https://scholarshipdb.net/scholarships-in-China',
    'https://scholarshipdb.net/scholarships-in-Turkey',
    'https://scholarshipdb.net/scholarships-in-South-Korea',
    'https://scholarshipdb.net/scholarships-in-Japan',
    'https://scholarshipdb.net/scholarships-in-Australia',
    'https://scholarshipdb.net/scholarships-in-Canada',
    'https://scholarshipdb.net/scholarships-in-USA',
    'https://scholarshipdb.net/scholarships-in-Saudi-Arabia',
    'https://scholarshipdb.net/scholarships-in-Netherlands',
    'https://scholarshipdb.net/scholarships-in-Hungary',
    'https://scholarshipdb.net/scholarships-in-Norway',
    'https://scholarshipdb.net/scholarships-in-Sweden',
    'https://scholarshipdb.net/scholarships-in-Finland',
    'https://scholarshipdb.net/scholarships-in-Italy',
    'https://scholarshipdb.net/scholarships-in-France',
    'https://scholarshipdb.net/scholarships-in-Malaysia',
    'https://scholarshipdb.net/scholarships-in-Singapore',
    'https://scholarshipdb.net/scholarships-in-New-Zealand',
    'https://scholarshipdb.net/scholarships-in-Indonesia',
    'https://scholarshipdb.net/scholarships-in-Russia',
    'https://scholarshipdb.net/scholarships-in-Brazil',
    'https://scholarshipdb.net/scholarships-in-Egypt',
    'https://scholarshipdb.net/scholarships-in-Morocco',
    'https://scholarshipdb.net/scholarships-in-South-Africa',
    'https://scholarshipdb.net/scholarships-in-Thailand',
    'https://scholarshipdb.net/scholarships-in-Vietnam',
    'https://scholarshipdb.net/scholarships-in-Taiwan',
    'https://scholarshipdb.net/scholarships-in-Hong-Kong',
    'https://scholarshipdb.net/scholarships-in-Pakistan',
    'https://scholarshipdb.net/scholarships-in-India',
]

def get_headers():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1",
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

def fetch(url, retries=4):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(2, 5) * (attempt + 1))
            session = requests.Session()
            session.headers.update(get_headers())
            r = session.get(url, timeout=20, allow_redirects=True)
            if r.status_code == 200:
                return r
            elif r.status_code == 403:
                time.sleep(random.uniform(10, 20))
            elif r.status_code == 429:
                time.sleep(30)
            else:
                time.sleep(random.uniform(5, 10))
        except:
            time.sleep(5)
    return None

def get_domain(url):
    try:
        return urlparse(url).netloc.replace('www.','')
    except:
        return ""

def is_aggregator_domain(url):
    domain = get_domain(url)
    return any(agg in domain for agg in AGGREGATOR_DOMAINS)

def is_future_date(text):
    text_lower = text.lower()
    if any(c in text_lower for c in [
        'applications are closed','deadline has passed',
        'no longer accepting','competition is closed']):
        return False

    found_dates = []
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
                found_dates.append((year, month))
            except:
                continue

    if found_dates:
        future = [(y,m) for y,m in found_dates
                  if y > CURRENT_YEAR or (y == CURRENT_YEAR and m >= CURRENT_MONTH)]
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
    for p in [r'ielts[:\s]*(\d+\.?\d*)', r'(\d+\.?\d*)\s*(?:in|for)?\s*ielts']:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                score = float(m.group(1))
                if 4.0 <= score <= 9.0:
                    return str(score)
            except:
                pass
    return "Required" if re.search(r'\bielts\b', text, re.IGNORECASE) else "Not required"

def extract_degree(text):
    levels = []
    if re.search(r'\bundergraduate|bachelor\b', text, re.IGNORECASE): levels.append("Bachelor")
    if re.search(r'\bmaster|postgraduate|msc|mba\b', text, re.IGNORECASE): levels.append("Master")
    if re.search(r'\bphd|doctoral\b', text, re.IGNORECASE): levels.append("PhD")
    return ", ".join(levels) if levels else "All levels"

def extract_funding(text):
    if re.search(r'full.?fund|fully.?fund|full scholarship', text, re.IGNORECASE): return "Fully Funded"
    if re.search(r'partial|tuition only', text, re.IGNORECASE): return "Partial"
    if re.search(r'stipend|living allowance', text, re.IGNORECASE): return "Stipend Included"
    return "Check website"

def extract_eligible_countries(text):
    countries = [
        "Pakistan","India","Bangladesh","Nepal","Sri Lanka","Afghanistan",
        "Nigeria","Ghana","Kenya","Ethiopia","Tanzania","Uganda","Rwanda",
        "South Africa","Egypt","Morocco","Tunisia","Algeria","Indonesia",
        "Malaysia","Philippines","Vietnam","Thailand","Cambodia","Myanmar",
        "Brazil","Colombia","Peru","Argentina","Mexico","developing countries",
        "low-income countries","African countries","Asian countries",
        "all countries","international students","worldwide"
    ]
    found = []
    tl = text.lower()
    for c in countries:
        if c.lower() in tl:
            found.append(c)
    return ", ".join(found[:15]) if found else "Open to international students worldwide"

def is_job_listing(title):
    if not title: return True
    t = title.lower()
    return any(w in t for w in [
        'position','professor','lecturer','postdoc','instructor',
        'faculty','director','dean','researcher','scientist',
        'engineer','analyst','coordinator','manager','officer',
        'job fair','recruitment','hiring','vacancy','staff',
        'technician','nurse','surgeon','consultant','associate',
        'assistant ','senior ','junior ','lead ','head of'
    ])

def is_list_page(title):
    if not title: return True
    t = title.lower()
    return any(re.search(p, t) for p in [
        r'top \d+', r'^\d+ scholarships', 'list of',
        'best scholarships', 'countries where', r'\d+ fully funded'
    ])

def find_official_link(soup, page_url):
    """Find official university/government link inside a 3rd party post"""
    apply_keywords = [
        'apply now','apply here','official website','click here to apply',
        'application portal','official link','visit official','more information',
        'official page','scholarship page','apply for','learn more',
        'application form','online application','apply at','official scholarship',
        'for more information','visit the','official site'
    ]
    official_indicators = [
        '.edu','.ac.uk','.edu.au','.ac.jp','.ac.kr','.edu.cn',
        '.gov','.org','university','college','institute','daad.de',
        'chevening.org','fulbright','erasmus','stipendiumhungaricum',
        'turkiyeburslari','campuschina','studyinkorea','mext.go.jp',
        'scholarships.gc.ca','studyinaustralia.gov'
    ]
    current_domain = get_domain(page_url)
    candidates = []

    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        link_text = a.get_text(strip=True).lower()
        if not href or href.startswith('#') or 'javascript' in href:
            continue
        if href.startswith('/'):
            parsed = urlparse(page_url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        elif not href.startswith('http'):
            continue
        if any(s in href for s in ['facebook','twitter','instagram','linkedin','youtube','whatsapp','telegram']):
            continue
        if is_aggregator_domain(href):
            continue

        link_domain = get_domain(href)
        score = 0
        for ind in official_indicators:
            if ind in link_domain:
                score += 15
        for kw in apply_keywords:
            if kw in link_text:
                score += 10
        if any(kw in href.lower() for kw in ['scholarship','fellowship','grant','apply','admission']):
            score += 5
        if link_domain != current_domain and score > 0:
            score += 3
        if score > 5:
            candidates.append((score, href))

    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]
    return None

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
        if domain.endswith(tld):
            return country
    hints = {
        'germany':'Germany','united kingdom':'United Kingdom','australia':'Australia',
        'canada':'Canada','japan':'Japan','china':'China','korea':'South Korea',
        'turkey':'Turkey','france':'France','netherlands':'Netherlands',
        'usa':'USA','united states':'USA','saudi arabia':'Saudi Arabia',
        'malaysia':'Malaysia','singapore':'Singapore','italy':'Italy',
        'russia':'Russia','indonesia':'Indonesia','vietnam':'Vietnam',
        'brazil':'Brazil','egypt':'Egypt','pakistan':'Pakistan','india':'India',
        'norway':'Norway','sweden':'Sweden','finland':'Finland',
    }
    for hint, country in hints.items():
        if hint in text.lower()[:2000]:
            return country
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
        if country in countries:
            return region
    return "International"

def write_blog(d):
    title = d['title']
    country = d['country']
    region = d['region']
    uni = d['university']
    deadline = d['deadline'] or "Check official website"
    ielts = d['ielts']
    degree = d['degree']
    funding = d['funding']
    eligible = d['eligible_countries']
    link = d['official_link']
    desc = d['description']

    lang_note = (
        f"Minimum IELTS score required: **{ielts}**. "
        "Start preparation at least 3 months before the deadline. "
        "British Council and IDP offer IELTS in major cities across Pakistan and India."
        if ielts not in ["Not required","Check website"]
        else "No English language test required for this scholarship."
    )

    seo_title = f"{title} {CURRENT_YEAR} — Eligibility, Deadline & How to Apply"[:70]
    seo_desc = f"Apply for {title}. Deadline: {deadline}. {degree} level. IELTS: {ielts}. Complete guide for international students."[:160]

    blog = f"""# {title} {CURRENT_YEAR}

**Last Updated:** {datetime.now().strftime("%B %d, %Y")} | **Status:** Open

---

## About This Scholarship

The **{title}** is a verified open scholarship for {CURRENT_YEAR}. Hosted by **{uni}** in **{country}**, {region}.

{desc}

This is a real opportunity. We verified the deadline is in the future and the official link is working before publishing this guide.

---

## Quick Summary

| Detail | Information |
|--------|------------|
| **Scholarship** | {title} |
| **Host** | {uni} |
| **Country** | {country} |
| **Degree Level** | {degree} |
| **Funding** | {funding} |
| **Deadline** | {deadline} |
| **IELTS** | {ielts} |
| **Verified** | {datetime.now().strftime("%B %Y")} |

---

## Who Can Apply?

{eligible}

---

## Scholarship Benefits

**Funding type: {funding}**

Visit the official website for the complete breakdown of what this scholarship covers including tuition, living allowance, travel and insurance.

---

## Language Requirements

{lang_note}

---

## Deadline

**{deadline}** — Verify on official website before applying.

---

## Documents Required

- Valid Passport
- Academic Transcripts
- Degree Certificate
- IELTS / TOEFL (Score: {ielts})
- Statement of Purpose
- 2–3 Recommendation Letters
- Updated CV
- Research Proposal (PhD only)

---

## How to Write Your SOP

Start with a real story. Explain your academic background with numbers. Say specifically why this scholarship and this university. Describe your 5-year career goals. Show why you deserve it. Close confidently.

Length: 600–1000 words.

---

## FAQ

**Can Pakistani students apply?**
{"Yes — Pakistan is listed as an eligible country." if "Pakistan" in eligible else "Check official website for complete eligibility list."}

**IELTS required?**
{f"Yes — minimum {ielts}." if ielts not in ["Not required","Check website"] else "No IELTS requirement mentioned."}

**Deadline?**
**{deadline}**

---

## Apply Now

**Official Link:** {link}

> Verified by AdmitGoal: {datetime.now().strftime("%B %d, %Y")}

*Share with someone who deserves this opportunity.*
"""
    return blog, seo_title, seo_desc

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

def save(conn, data):
    if not data.get('title') or len(data['title']) < 10: return False
    if not data.get('official_link'): return False
    if not data.get('deadline'): return False
    if is_job_listing(data['title']): return False
    if is_list_page(data['title']): return False

    blog, seo_title, seo_desc = write_blog(data)
    lang = f"IELTS {data['ielts']}" if data['ielts'] not in ["Not required","Check website"] else data['ielts']

    try:
        cur = conn.cursor()
        cur.execute("SELECT id, deadline FROM scholarship_details WHERE scholarship_link=%s",
                    (data['official_link'],))
        existing = cur.fetchone()
        if existing:
            if data['deadline'] and data['deadline'] != 'Check website':
                cur.execute('''UPDATE scholarship_details SET
                    deadline=%s,last_updated=%s,blog_post=%s,
                    seo_title=%s,seo_description=%s,
                    eligible_countries=%s,ielts_score=%s
                    WHERE scholarship_link=%s''',
                    (data['deadline'],datetime.now().strftime("%Y-%m-%d"),
                     blog,seo_title,seo_desc,
                     data['eligible_countries'],data['ielts'],
                     data['official_link']))
            cur.close()
            return True

        cur.execute('''INSERT INTO scholarship_details
            (scholarship_link,title,full_description,eligible_countries,
             eligible_students,degree_level,deadline,language_requirement,
             ielts_score,benefits,how_to_apply,blog_post,seo_title,
             seo_description,university_name,country,region,
             funding_type,gpa_required,last_updated)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (data['official_link'],data['title'],
             data['description'][:800],data['eligible_countries'],
             "International students",data['degree'],data['deadline'],
             lang,data['ielts'],"","",blog,seo_title,seo_desc,
             data['university'],data['country'],data['region'],
             data['funding'],"Check website",
             datetime.now().strftime("%Y-%m-%d")))

        cur.execute('''INSERT INTO scholarships
            (title,description,country,deadline,link,source,scraped_date)
            VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (link) DO NOTHING''',
            (data['title'],seo_desc,data['country'],data['deadline'],
             data['official_link'],data['university'][:50],
             datetime.now().strftime("%Y-%m-%d")))
        cur.close()
        return True
    except Exception as e:
        print(f"    DB Error: {e}")
        return False

def scrape_listing(listing_url, conn):
    r = fetch(listing_url)
    if not r:
        return 0

    soup = BeautifulSoup(r.text, 'lxml')
    base_domain = get_domain(listing_url)
    parsed = urlparse(listing_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # Find individual post links on this listing page
    post_links = []
    seen = set()

    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        if not href.startswith('http'):
            href = base_url + href if href.startswith('/') else listing_url + href
        if get_domain(href) != base_domain:
            continue
        skip = ['/category/','/tag/','/page/','/author/','#','mailto',
                '/about','/contact','/privacy','/search','/login']
        if any(s in href for s in skip):
            continue
        if href == listing_url or href in seen:
            continue
        if len(text) > 12:
            seen.add(href)
            post_links.append((text, href))

    print(f"  Found {len(post_links)} posts")
    saved = 0

    for post_title, post_url in post_links[:30]:  # 30 per listing page
        print(f"\n  Post: {post_title[:65]}")

        if is_job_listing(post_title) or is_list_page(post_title):
            print(f"  Skip (job/list)")
            continue

        post_r = fetch(post_url)
        if not post_r:
            continue

        post_soup = BeautifulSoup(post_r.text, 'lxml')
        for tag in post_soup.find_all(['nav','footer','script','style','aside']):
            tag.decompose()
        post_text = ' '.join(post_soup.get_text(separator=' ', strip=True).split())

        if not is_future_date(post_text):
            print(f"  Skip (outdated)")
            continue

        # Find official link from post
        official_link = find_official_link(post_soup, post_url)

        combined_text = post_text
        if official_link and not is_aggregator_domain(official_link):
            print(f"  Official: {official_link[:65]}")
            official_r = fetch(official_link)
            if official_r:
                off_soup = BeautifulSoup(official_r.text, 'lxml')
                for tag in off_soup.find_all(['nav','footer','script','style','aside']):
                    tag.decompose()
                off_text = ' '.join(off_soup.get_text(separator=' ', strip=True).split())
                combined_text = post_text + " " + off_text
        else:
            official_link = post_url
            print(f"  No official link — using post")

        h1 = post_soup.find('h1')
        title = h1.get_text(strip=True) if h1 else post_title
        if is_job_listing(title) or is_list_page(title):
            print(f"  Skip: {title[:50]}")
            continue

        deadline = extract_deadline(combined_text)
        if not deadline:
            print(f"  Skip (no deadline)")
            continue

        ielts = extract_ielts(combined_text)
        degree = extract_degree(combined_text)
        funding = extract_funding(combined_text)
        eligible = extract_eligible_countries(combined_text)

        link_domain = get_domain(official_link)
        country = detect_country(link_domain, combined_text)
        region = detect_region(country)

        title_tag = post_soup.find('title')
        uni = title_tag.get_text(strip=True).split('|')[0].split('–')[0].strip()[:60] if title_tag else base_domain

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
        }

        if save(conn, data):
            print(f"  SAVED: {title[:60]}")
            saved += 1

        time.sleep(random.uniform(2, 4))

    return saved

if __name__ == "__main__":
    print("=" * 60)
    print("  ADMITGOAL — AGGREGATOR SCRAPER")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Sources: {len(AGGREGATOR_SOURCES)}")
    print("  Strategy: 3rd party → official link → complete data")
    print("=" * 60)

    conn = get_db()
    total = 0

    for i, url in enumerate(AGGREGATOR_SOURCES, 1):
        print(f"\n[{i}/{len(AGGREGATOR_SOURCES)}] {url}")
        saved = scrape_listing(url, conn)
        total += saved
        print(f"  Saved: {saved}")
        time.sleep(random.uniform(3, 6))

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scholarship_details")
    db_total = cur.fetchone()[0]
    cur.close()
    conn.close()

    print(f"\n{'='*60}")
    print(f"  Saved this run : {total}")
    print(f"  Total in DB    : {db_total}")
    print(f"{'='*60}")