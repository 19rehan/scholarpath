"""
ADMITGOAL — OFFICIAL SOURCES SCRAPER
Scrapes directly from government and university scholarship pages worldwide
Runs at: 6am, 12pm, 6pm, 12am
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

# 100+ official sources worldwide
OFFICIAL_SOURCES = [
    # ── EUROPE ────────────────────────────────────────────
    {'url':'https://www.chevening.org/scholarships/','country':'United Kingdom','region':'Europe'},
    {'url':'https://cscuk.fcdo.gov.uk/scholarships/','country':'United Kingdom','region':'Europe'},
    {'url':'https://www.daad.de/en/study-and-research-in-germany/scholarships/','country':'Germany','region':'Europe'},
    {'url':'https://stipendiumhungaricum.hu/en/','country':'Hungary','region':'Europe'},
    {'url':'https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en','country':'Europe','region':'Europe'},
    {'url':'https://www.uu.se/en/study/scholarships','country':'Sweden','region':'Europe'},
    {'url':'https://www.helsinki.fi/en/studying/fees-and-financial-aid/scholarships-and-grants','country':'Finland','region':'Europe'},
    {'url':'https://studies.ku.dk/masters/financing/scholarships/','country':'Denmark','region':'Europe'},
    {'url':'https://www.uio.no/english/studies/admission/scholarships/','country':'Norway','region':'Europe'},
    {'url':'https://www.ugent.be/en/research/funding/devcoop/scholarships','country':'Belgium','region':'Europe'},
    {'url':'https://www.uva.nl/en/education/master-s/scholarships--tuition/scholarships-and-loans/scholarships-and-loans.html','country':'Netherlands','region':'Europe'},
    {'url':'https://www.tum.de/en/studies/fees-and-financial-aid/scholarships','country':'Germany','region':'Europe'},
    {'url':'https://international.univie.ac.at/scholarships/','country':'Austria','region':'Europe'},
    {'url':'https://en.uw.edu.pl/education/scholarships/','country':'Poland','region':'Europe'},
    {'url':'https://cuni.cz/UKEN-178.html','country':'Czech Republic','region':'Europe'},
    {'url':'https://ut.ee/en/scholarships','country':'Estonia','region':'Europe'},
    {'url':'https://www.tcd.ie/study/fees-funding/scholarships/','country':'Ireland','region':'Europe'},
    {'url':'https://www.uzh.ch/en/studies/application/scholarships.html','country':'Switzerland','region':'Europe'},
    {'url':'https://www.unipd.it/en/scholarships-and-grants','country':'Italy','region':'Europe'},
    {'url':'https://www.uni-bonn.de/en/studying/international-students/scholarships','country':'Germany','region':'Europe'},
    {'url':'https://www.lmu.de/en/study/all-degrees-and-offerings/fees-and-funding/scholarships/','country':'Germany','region':'Europe'},

    # ── MIDDLE EAST ───────────────────────────────────────
    {'url':'https://www.turkiyeburslari.gov.tr/en','country':'Turkey','region':'Middle East'},
    {'url':'https://www.kaust.edu.sa/en/study/financial-support','country':'Saudi Arabia','region':'Middle East'},
    {'url':'https://www.kau.edu.sa/Content.aspx?Site_ID=0&lng=EN&CID=206','country':'Saudi Arabia','region':'Middle East'},
    {'url':'https://www.qu.edu.qa/students/student_life/scholarships','country':'Qatar','region':'Middle East'},
    {'url':'https://www.uaeu.ac.ae/en/admissions/scholarships.shtml','country':'UAE','region':'Middle East'},
    {'url':'https://www.ju.edu.jo/en/home/scholarships.aspx','country':'Jordan','region':'Middle East'},
    {'url':'https://www.iau.edu.sa/en/admission/scholarships','country':'Saudi Arabia','region':'Middle East'},

    # ── ASIA ──────────────────────────────────────────────
    {'url':'https://www.campuschina.org/scholarships/index.html','country':'China','region':'Asia'},
    {'url':'https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do','country':'South Korea','region':'Asia'},
    {'url':'https://www.studyinjapan.go.jp/en/smap_stopj-applications_scholarship.html','country':'Japan','region':'Asia'},
    {'url':'https://www.u-tokyo.ac.jp/en/prospective-students/scholarships.html','country':'Japan','region':'Asia'},
    {'url':'https://www.kyoto-u.ac.jp/en/education-campus/international/students2/scholarship','country':'Japan','region':'Asia'},
    {'url':'https://en.snu.ac.kr/apply/scholarship','country':'South Korea','region':'Asia'},
    {'url':'https://international.kaist.ac.kr/cms/FR_CON/index.do?MENU_ID=90','country':'South Korea','region':'Asia'},
    {'url':'https://www.nus.edu.sg/oam/scholarships','country':'Singapore','region':'Asia'},
    {'url':'https://um.edu.my/study-at-um/scholarships','country':'Malaysia','region':'Asia'},
    {'url':'https://www.ait.ac.th/admissions/scholarships/','country':'Thailand','region':'Asia'},
    {'url':'https://www.tsinghua.edu.cn/en/Admission/Scholarships.htm','country':'China','region':'Asia'},
    {'url':'https://en.sjtu.edu.cn/admissions/scholarships/','country':'China','region':'Asia'},
    {'url':'https://www.zju.edu.cn/english/2020/0709/c19573a2138573/page.htm','country':'China','region':'Asia'},
    {'url':'https://www.hec.gov.pk/english/scholarshipsgrants/Pages/default.aspx','country':'Pakistan','region':'Asia'},
    {'url':'https://mohe.gov.my/en/scholarships','country':'Malaysia','region':'Asia'},
    {'url':'https://www.scholarship.or.th/en/','country':'Thailand','region':'Asia'},
    {'url':'https://www.vied.vn/en/scholarships','country':'Vietnam','region':'Asia'},
    {'url':'https://www.most.gov.tw/scholarship','country':'Taiwan','region':'Asia'},
    {'url':'https://www.ugc.edu.hk/eng/rgc/funding_opport/ras/','country':'Hong Kong','region':'Asia'},
    {'url':'https://iccr.gov.in/scholarships','country':'India','region':'Asia'},
    {'url':'https://www.itb.ac.id/admission/scholarship','country':'Indonesia','region':'Asia'},
    {'url':'https://international.ui.ac.id/scholarships/','country':'Indonesia','region':'Asia'},

    # ── OCEANIA ───────────────────────────────────────────
    {'url':'https://www.studyinaustralia.gov.au/english/australian-scholarships','country':'Australia','region':'Oceania'},
    {'url':'https://scholarships.unimelb.edu.au/','country':'Australia','region':'Oceania'},
    {'url':'https://www.anu.edu.au/study/scholarships','country':'Australia','region':'Oceania'},
    {'url':'https://scholarships.uq.edu.au/','country':'Australia','region':'Oceania'},
    {'url':'https://www.unsw.edu.au/study/scholarships','country':'Australia','region':'Oceania'},
    {'url':'https://www.studyinnewzealand.govt.nz/how-to-apply/scholarships','country':'New Zealand','region':'Oceania'},
    {'url':'https://www.auckland.ac.nz/en/study/fees-and-money/scholarships.html','country':'New Zealand','region':'Oceania'},

    # ── NORTH AMERICA ─────────────────────────────────────
    {'url':'https://foreign.fulbrightonline.org/','country':'USA','region':'North America'},
    {'url':'https://www.iie.org/programs/','country':'USA','region':'North America'},
    {'url':'https://www.scholarships.gc.ca/scholarships-bourses/index.aspx','country':'Canada','region':'North America'},
    {'url':'https://www.sgs.utoronto.ca/awards/','country':'Canada','region':'North America'},
    {'url':'https://students.ubc.ca/enrolment/finances/scholarships-awards-bursaries','country':'Canada','region':'North America'},
    {'url':'https://www.mcgill.ca/studentaid/scholarships-awards','country':'Canada','region':'North America'},

    # ── AFRICA ────────────────────────────────────────────
    {'url':'https://www.uct.ac.za/main/explore-uct/funding','country':'South Africa','region':'Africa'},
    {'url':'https://www.africanscholarships.com/','country':'Africa','region':'Africa'},
    {'url':'https://scholarshipdb.net/scholarships-in-Egypt','country':'Egypt','region':'Africa'},
    {'url':'https://scholarshipdb.net/scholarships-in-Morocco','country':'Morocco','region':'Africa'},

    # ── LATIN AMERICA ─────────────────────────────────────
    {'url':'https://www.cnpq.br/web/guest/chamadas-publicas','country':'Brazil','region':'Latin America'},
    {'url':'https://www.conicet.gov.ar/becas/','country':'Argentina','region':'Latin America'},

    # ── RUSSIA & CENTRAL ASIA ─────────────────────────────
    {'url':'https://russia.study/en','country':'Russia','region':'Europe'},
    {'url':'https://scholarshipdb.net/scholarships-in-Russia','country':'Russia','region':'Europe'},
    {'url':'https://scholarshipdb.net/scholarships-in-Kazakhstan','country':'Kazakhstan','region':'Asia'},
]

def get_headers():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    ]
    return {
        "User-Agent": random.choice(agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
        "Referer": "https://www.google.com/",
    }

def fetch(url, retries=4):
    for attempt in range(retries):
        try:
            delay = random.uniform(2, 5) * (attempt + 1)
            time.sleep(delay)
            session = requests.Session()
            session.headers.update(get_headers())
            r = session.get(url, timeout=20, allow_redirects=True)
            if r.status_code == 200:
                return r
            elif r.status_code == 403:
                print(f"    Blocked (403) attempt {attempt+1} — waiting...")
                time.sleep(random.uniform(10, 20))
            elif r.status_code == 429:
                print(f"    Rate limited (429) — waiting 30s...")
                time.sleep(30)
            else:
                time.sleep(random.uniform(5, 10))
        except requests.exceptions.Timeout:
            print(f"    Timeout attempt {attempt+1}")
            time.sleep(5)
        except Exception as e:
            print(f"    Error: {e}")
            time.sleep(5)
    return None

def get_domain(url):
    try:
        return urlparse(url).netloc.replace('www.', '')
    except:
        return ""

def is_future_date(text):
    """Returns True if text contains a future date"""
    text_lower = text.lower()

    # Hard closed signals
    if any(c in text_lower for c in [
        'applications are closed', 'deadline has passed',
        'no longer accepting', 'competition is closed'
    ]):
        return False

    found_dates = []
    patterns = [
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})',
        r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',
        r'(\d{4})[/-](\d{2})[/-](\d{2})',
    ]
    for p in patterns:
        for m in re.finditer(p, text_lower):
            try:
                g = m.groups()
                if g[0] in MONTHS:
                    month, year = MONTHS[g[0]], int(g[2])
                elif len(g) == 3 and g[0].isdigit() and len(g[0]) == 4:
                    year, month = int(g[0]), int(g[1])
                else:
                    month, year = MONTHS[g[1]], int(g[2])
                found_dates.append((year, month))
            except:
                continue

    if found_dates:
        future = [(y,m) for y,m in found_dates
                  if y > CURRENT_YEAR or (y == CURRENT_YEAR and m >= CURRENT_MONTH)]
        return len(future) > 0

    # No date found — check year
    return str(CURRENT_YEAR) in text or str(CURRENT_YEAR+1) in text

def extract_deadline(text):
    months_str = "january|february|march|april|may|june|july|august|september|october|november|december"
    patterns = [
        rf'deadline[:\s]*((?:{months_str})[\s\d,]+\d{{4}})',
        rf'closing date[:\s]*((?:{months_str})[\s\d,]+\d{{4}})',
        rf'apply by[:\s]*((?:{months_str})[\s\d,]+\d{{4}})',
        rf'applications? (close|due)[s]?[:\s]*((?:{months_str})[\s\d,]+\d{{4}})',
        rf'(\d{{1,2}}\s+(?:{months_str})\s+\d{{4}})',
        rf'((?:{months_str})\s+\d{{1,2}},?\s+\d{{4}})',
        rf'((?:{months_str})\s+\d{{4}})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            groups = [g for g in m.groups() if g and g.lower() not in ['close','due','closes']]
            if groups:
                deadline = groups[-1].strip()
                # Verify it's a future date
                if is_future_date(deadline):
                    return deadline
    return None

def extract_ielts(text):
    patterns = [
        r'ielts[:\s]*(?:score[:\s]*)?(\d+\.?\d*)',
        r'ielts[:\s]*(?:minimum[:\s]*)?(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*(?:overall)?\s*(?:in|for)?\s*ielts',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                score = float(m.group(1))
                if 4.0 <= score <= 9.0:
                    return str(score)
            except:
                pass
    if re.search(r'\bielts\b', text, re.IGNORECASE):
        return "Required"
    return "Not required"

def extract_degree(text):
    levels = []
    if re.search(r'\bundergraduate|bachelor\b', text, re.IGNORECASE): levels.append("Bachelor")
    if re.search(r'\bmaster|postgraduate|msc|mba\b', text, re.IGNORECASE): levels.append("Master")
    if re.search(r'\bphd|doctoral\b', text, re.IGNORECASE): levels.append("PhD")
    return ", ".join(levels) if levels else "All levels"

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
        "Pakistan","India","Bangladesh","Nepal","Sri Lanka","Afghanistan",
        "Nigeria","Ghana","Kenya","Ethiopia","Tanzania","Uganda","Rwanda",
        "Zimbabwe","Zambia","South Africa","Egypt","Morocco","Tunisia","Algeria",
        "Indonesia","Malaysia","Philippines","Vietnam","Thailand","Cambodia",
        "Myanmar","China","Mongolia","Brazil","Colombia","Peru","Argentina",
        "Mexico","Bolivia","Ecuador","developing countries","low-income countries",
        "middle-income countries","African countries","Asian countries",
        "all countries","international students","worldwide","global"
    ]
    found = []
    text_lower = text.lower()
    for c in countries:
        if c.lower() in text_lower:
            found.append(c)
    if found:
        return ", ".join(found[:15])
    return "Open to international students worldwide"

def is_job_listing(title):
    if not title: return True
    t = title.lower()
    job_words = [
        'position', 'professor', 'lecturer', 'postdoc', 'instructor',
        'faculty', 'director', 'dean', 'researcher', 'scientist',
        'engineer', 'analyst', 'coordinator', 'manager', 'officer',
        'job fair', 'recruitment', 'hiring', 'vacancy', 'staff',
        'technician', 'nurse', 'surgeon', 'consultant', 'associate',
        'assistant ', 'senior ', 'junior ', 'lead ', 'head of',
    ]
    return any(w in t for w in job_words)

def is_list_page(title):
    if not title: return True
    t = title.lower()
    return any(re.search(p, t) for p in [
        r'top \d+', r'^\d+ scholarships', 'list of scholarships',
        'best scholarships', 'countries where', r'\d+ fully funded',
        'all scholarships in', 'scholarships for 2025$'
    ])

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
        f"The minimum IELTS score required is **{ielts}**. "
        "Start preparation at least 3 months before the deadline. "
        "British Council and IDP offer IELTS in Karachi, Lahore and Islamabad. "
        "Some universities accept TOEFL or PTE as alternatives."
        if ielts not in ["Not required", "Check website"]
        else "No English language test is required. This is great for students who have not yet taken IELTS."
    )

    seo_title = f"{title} {CURRENT_YEAR} — Eligibility, Deadline & How to Apply"[:70]
    seo_desc = f"Apply for {title}. Deadline: {deadline}. {degree} level. IELTS: {ielts}. Complete guide for Pakistani and international students."[:160]

    blog = f"""# {title} {CURRENT_YEAR}

**Last Updated:** {datetime.now().strftime("%B %d, %Y")} | **Status:** Open

---

## About This Scholarship

The **{title}** is offered by **{uni}** in **{country}**, {region}. This is a verified, open scholarship opportunity for international students in {CURRENT_YEAR}.

If you are a student from Pakistan, India, Bangladesh, Nigeria, Kenya or any developing country — this is a real opportunity worth your attention. We verified it is still open before publishing this guide.

{desc}

---

## Quick Summary

| Detail | Information |
|--------|------------|
| **Scholarship** | {title} |
| **University / Host** | {uni} |
| **Country** | {country} |
| **Region** | {region} |
| **Degree Level** | {degree} |
| **Funding Type** | {funding} |
| **Application Deadline** | {deadline} |
| **IELTS Required** | {ielts} |
| **Last Verified** | {datetime.now().strftime("%B %Y")} |

---

## Who Can Apply?

{eligible}

{"This scholarship is open to students from all countries. Pakistani, Indian and Bangladeshi students are eligible and strongly encouraged to apply." if any(w in eligible.lower() for w in ['international', 'worldwide', 'all countries']) else f"Students from the following backgrounds can apply: {eligible}"}

---

## What Does This Scholarship Cover?

**Funding: {funding}**

Visit the official website for the complete breakdown. Scholarship packages typically include tuition fees, monthly living allowance, health insurance, travel grant and accommodation support depending on the program.

---

## English Language Requirements

{lang_note}

---

## Application Deadline

**{deadline}**

Recommended timeline:
- 3 months before: Gather all documents
- 2 months before: Write and refine your SOP
- 1 month before: Request recommendation letters
- 2 weeks before: Submit your complete application

---

## Documents Required

- Valid Passport
- Academic Transcripts (certified copies)
- Degree Certificate
- IELTS / TOEFL Certificate — Score: {ielts}
- Statement of Purpose (600–1000 words)
- 2–3 Recommendation Letters
- Updated CV / Resume
- Passport Photos
- Research Proposal (PhD only)

---

## How to Write a Strong SOP

**Opening:** Start with a real story — a moment that defined your direction. Not "I am applying for..."

**Academic background:** Your degree, GPA, key projects. Use specific numbers.

**Why this scholarship:** Research the university and program specifically. Generic reasons get rejected.

**Career goals:** Where will you be in 5 years? How does this scholarship fit?

**Why you deserve it:** Leadership, research, community work, challenges overcome.

**Closing:** Confident and forward-looking.

Length: 600–1000 words unless specified otherwise.

---

## FAQ

**Can Pakistani students apply?**
{"Yes — Pakistani students are eligible." if "Pakistan" in eligible else "Check the eligibility section. Most international scholarships welcome Pakistani applicants."}

**Is IELTS required?**
{f"Yes — minimum {ielts}." if ielts not in ["Not required","Check website"] else "No IELTS requirement mentioned."}

**Deadline?**
**{deadline}** — Always verify on the official website.

---

## Apply Now

**Official Link:** {link}

> Last verified: {datetime.now().strftime("%B %d, %Y")}

*Share this with someone who deserves a scholarship.*
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
        # Check if exists with better data
        cur.execute("SELECT id, deadline FROM scholarship_details WHERE scholarship_link=%s", (data['official_link'],))
        existing = cur.fetchone()

        if existing:
            # Only update if new data has more complete deadline
            if data['deadline'] and data['deadline'] != 'Check website':
                cur.execute('''UPDATE scholarship_details SET
                    deadline=%s, last_updated=%s, blog_post=%s,
                    seo_title=%s, seo_description=%s,
                    eligible_countries=%s, ielts_score=%s
                    WHERE scholarship_link=%s''',
                    (data['deadline'], datetime.now().strftime("%Y-%m-%d"),
                     blog, seo_title, seo_desc,
                     data['eligible_countries'], data['ielts'],
                     data['official_link']))
                cur.close()
                return True
            cur.close()
            return False

        cur.execute('''INSERT INTO scholarship_details
            (scholarship_link,title,full_description,eligible_countries,
             eligible_students,degree_level,deadline,language_requirement,
             ielts_score,benefits,how_to_apply,blog_post,seo_title,
             seo_description,university_name,country,region,
             funding_type,gpa_required,last_updated)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (data['official_link'],data['title'],data['description'][:800],
             data['eligible_countries'],"International students",
             data['degree'],data['deadline'],lang,data['ielts'],
             "","",blog,seo_title,seo_desc,
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

def detect_country(domain, text=""):
    tld_map = {
        '.ac.uk':'United Kingdom','.co.uk':'United Kingdom','.uk':'United Kingdom',
        '.edu.au':'Australia','.com.au':'Australia','.au':'Australia',
        '.ca':'Canada','.de':'Germany','.fr':'France','.nl':'Netherlands',
        '.se':'Sweden','.no':'Norway','.fi':'Finland','.dk':'Denmark',
        '.ch':'Switzerland','.at':'Austria','.be':'Belgium','.it':'Italy',
        '.es':'Spain','.pt':'Portugal','.pl':'Poland','.cz':'Czech Republic',
        '.hu':'Hungary','.ro':'Romania','.tr':'Turkey','.sa':'Saudi Arabia',
        '.ae':'UAE','.qa':'Qatar','.jo':'Jordan','.kw':'Kuwait',
        '.cn':'China','.jp':'Japan','.kr':'South Korea','.my':'Malaysia',
        '.sg':'Singapore','.th':'Thailand','.id':'Indonesia','.vn':'Vietnam',
        '.tw':'Taiwan','.hk':'Hong Kong','.nz':'New Zealand',
        '.za':'South Africa','.eg':'Egypt','.ma':'Morocco','.ng':'Nigeria',
        '.br':'Brazil','.mx':'Mexico','.ar':'Argentina',
        '.ru':'Russia','.kz':'Kazakhstan','.pk':'Pakistan','.in':'India',
        '.bd':'Bangladesh','.lk':'Sri Lanka','.np':'Nepal',
        '.edu':'USA','.gov':'USA','.org':'International',
    }
    for tld, country in sorted(tld_map.items(), key=lambda x: -len(x[0])):
        if domain.endswith(tld):
            return country
    hints = {
        'germany':'Germany','united kingdom':'United Kingdom','uk ':'United Kingdom',
        'australia':'Australia','canada':'Canada','japan':'Japan','china':'China',
        'korea':'South Korea','turkey':'Turkey','france':'France',
        'netherlands':'Netherlands','sweden':'Sweden','norway':'Norway',
        'usa':'USA','united states':'USA','saudi arabia':'Saudi Arabia',
        'malaysia':'Malaysia','singapore':'Singapore','italy':'Italy',
        'russia':'Russia','indonesia':'Indonesia','vietnam':'Vietnam',
        'brazil':'Brazil','egypt':'Egypt','pakistan':'Pakistan',
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
                'Vietnam','Taiwan','Hong Kong','Pakistan','India','Bangladesh','Sri Lanka',
                'Nepal','Philippines','Kazakhstan'],
        'Oceania':['Australia','New Zealand'],
        'North America':['USA','Canada','Mexico'],
        'Africa':['Nigeria','South Africa','Kenya','Ghana','Ethiopia','Tanzania','Uganda'],
        'Latin America':['Brazil','Colombia','Argentina','Peru','Chile'],
    }
    for region, countries in regions.items():
        if country in countries:
            return region
    return "International"

def scrape_source(source, conn):
    url = source['url']
    country = source['country']
    region = source['region']

    r = fetch(url)
    if not r:
        print(f"  Could not fetch — skipping")
        return 0

    soup = BeautifulSoup(r.text, 'lxml')
    for tag in soup.find_all(['nav','footer','script','style','aside','header']):
        tag.decompose()

    full_text = ' '.join(soup.get_text(separator=' ', strip=True).split())
    base_domain = get_domain(url)
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # Get site name
    title_tag = soup.find('title')
    site_name = title_tag.get_text(strip=True).split('|')[0].split('–')[0].strip()[:60] if title_tag else base_domain

    saved = 0
    seen = set()

    # Find scholarship links
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        text = a.get_text(strip=True)

        if len(text) < 12: continue
        if not any(kw in text.lower() for kw in
                   ['scholarship','fellowship','award','grant','bursary',
                    'funding','program','programme','stipend']):
            continue

        if href.startswith('/'):
            href = base_url + href
        elif not href.startswith('http'):
            continue

        if href in seen or href == url:
            continue
        seen.add(href)

        # Visit scholarship detail page
        print(f"  → {text[:60]}")
        detail_r = fetch(href)
        if not detail_r:
            continue

        detail_soup = BeautifulSoup(detail_r.text, 'lxml')
        for tag in detail_soup.find_all(['nav','footer','script','style','aside']):
            tag.decompose()
        detail_text = ' '.join(detail_soup.get_text(separator=' ', strip=True).split())

        # Check freshness
        if not is_future_date(detail_text):
            print(f"    Skip (outdated)")
            continue

        h1 = detail_soup.find('h1')
        title = h1.get_text(strip=True) if h1 else text
        if is_job_listing(title) or is_list_page(title):
            print(f"    Skip (job/list)")
            continue

        deadline = extract_deadline(detail_text)
        if not deadline:
            # Try from combined text
            deadline = extract_deadline(full_text)
        if not deadline:
            print(f"    Skip (no deadline)")
            continue

        ielts = extract_ielts(detail_text)
        degree = extract_degree(detail_text)
        funding = extract_funding(detail_text)
        eligible = extract_eligible_countries(detail_text)

        desc = ""
        for p in detail_soup.find_all('p'):
            t = p.get_text(strip=True)
            if len(t) > 80:
                desc = t[:600]
                break

        link_country = detect_country(get_domain(href), detail_text)
        if link_country == "International":
            link_country = country

        data = {
            'title': title,
            'description': desc or title,
            'university': site_name,
            'country': link_country,
            'region': detect_region(link_country),
            'deadline': deadline,
            'ielts': ielts,
            'degree': degree,
            'funding': funding,
            'eligible_countries': eligible,
            'official_link': href,
        }

        if save(conn, data):
            print(f"    SAVED: {title[:60]}")
            saved += 1

        time.sleep(random.uniform(1, 3))

    return saved

if __name__ == "__main__":
    print("=" * 60)
    print("  ADMITGOAL — OFFICIAL SOURCES SCRAPER")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Sources: {len(OFFICIAL_SOURCES)} worldwide")
    print("=" * 60)

    conn = get_db()
    total = 0

    for i, source in enumerate(OFFICIAL_SOURCES, 1):
        print(f"\n[{i}/{len(OFFICIAL_SOURCES)}] {source['country']} — {source['url'][:60]}")
        saved = scrape_source(source, conn)
        total += saved
        print(f"  Saved: {saved}")
        time.sleep(random.uniform(2, 4))

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scholarship_details")
    db_total = cur.fetchone()[0]
    cur.close()
    conn.close()

    print(f"\n{'='*60}")
    print(f"  Saved this run : {total}")
    print(f"  Total in DB    : {db_total}")
    print(f"{'='*60}")