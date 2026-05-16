import requests
from bs4 import BeautifulSoup
import psycopg2
import re
import time
import random
from datetime import datetime
from urllib.parse import urlparse

CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month

DATABASE_URL = 'postgresql://postgres.deqyxksflvlxjelppgxz:Rehan1819Rehan@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

def fetch(url):
    try:
        time.sleep(random.uniform(2, 3))
        r = requests.get(url, headers=get_headers(), timeout=12)
        return r if r.status_code == 200 else None
    except:
        return None

def is_outdated(deadline_text):
    if not deadline_text or deadline_text in ['See official website', 'See link']:
        return False
    months = {
        'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
        'july':7,'august':8,'september':9,'october':10,'november':11,'december':12
    }
    dl = deadline_text.lower()
    year_m = re.search(r'(\d{4})', dl)
    if not year_m:
        return False
    year = int(year_m.group(1))
    if year < CURRENT_YEAR:
        return True
    if year == CURRENT_YEAR:
        for month_name, month_num in months.items():
            if month_name in dl:
                if month_num < CURRENT_MONTH - 1:
                    return True
    return False

def find_official_link(soup, page_url):
    """
    Smart official link finder.
    When scraping a 3rd party page, find the real official link.
    """
    # Keywords that indicate official apply links
    apply_keywords = [
        'apply now', 'apply here', 'apply online', 'official website',
        'click here to apply', 'submit application', 'application portal',
        'apply for this', 'official link', 'apply at', 'application form',
        'visit official', 'more information', 'learn more', 'read more',
        'official page', 'scholarship page', 'university website'
    ]

    # Domains that are aggregators — NOT official
    aggregator_domains = [
        'scholars4dev', 'scholarshipdb', 'opportunitydesk',
        'afterschoolafrica', 'youthop', 'mastersportal', 'phdportal',
        'opportunitiesforafricans', 'scholarshipsads', 'buddy4study',
        'estudyassistance', 'afterschoolafrica', 'scholarshipregion',
        'scholarshiphunter', 'propakistani', 'hec.gov.pk'
    ]

    # Official domain indicators
    official_indicators = [
        '.edu', '.ac.uk', '.edu.au', '.ac.jp', '.ac.kr', '.edu.cn',
        '.gov', 'university', 'college', 'institute', 'daad.de',
        'chevening.org', 'fulbright', 'erasmus', 'stipendiumhungaricum',
        'turkiyeburslari', 'campuschina', 'studyinkorea', 'mext.go.jp',
        'scholarships.gc.ca', 'studyinaustralia.gov'
    ]

    current_domain = urlparse(page_url).netloc
    candidates = []

    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        link_text = a.get_text(strip=True).lower()

        # Skip empty, anchors, javascript
        if not href or href.startswith('#') or 'javascript' in href:
            continue

        # Make absolute URL
        if href.startswith('/'):
            parsed = urlparse(page_url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        elif not href.startswith('http'):
            continue

        link_domain = urlparse(href).netloc

        # Skip social media
        if any(s in link_domain for s in ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'whatsapp']):
            continue

        # Skip if same aggregator domain
        if any(agg in link_domain for agg in aggregator_domains):
            continue

        score = 0

        # High score for official-looking domains
        for indicator in official_indicators:
            if indicator in link_domain:
                score += 15

        # High score for apply-related text
        for kw in apply_keywords:
            if kw in link_text:
                score += 10

        # Score for scholarship-related URL paths
        if any(kw in href.lower() for kw in ['scholarship', 'fellowship', 'grant', 'funding', 'award', 'apply', 'admission']):
            score += 5

        # Different domain from current = likely external official link
        if link_domain != current_domain and score > 0:
            score += 3

        if score > 5:
            candidates.append((score, href))

    if candidates:
        candidates.sort(reverse=True)
        best_link = candidates[0][1]
        return best_link

    return None

def fix_existing_data():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    # Get all scholarships
    cur.execute("SELECT id, title, scholarship_link, deadline FROM scholarship_details ORDER BY id")
    rows = cur.fetchall()
    print(f"Total scholarships to check: {len(rows)}")

    deleted = 0
    fixed_links = 0
    kept = 0

    for sid, title, link, deadline in rows:
        print(f"\n[{sid}] {title[:60]}")

        # Step 1: Remove outdated
        if is_outdated(deadline):
            print(f"  DELETED — outdated deadline: {deadline}")
            cur.execute("DELETE FROM scholarship_details WHERE id=%s", (sid,))
            cur.execute("DELETE FROM scholarships WHERE link=%s", (link,))
            deleted += 1
            continue

        # Step 2: Check if link is from aggregator
        link_domain = urlparse(link).netloc if link else ""
        aggregator_domains = [
            'scholars4dev', 'scholarshipdb', 'opportunitydesk',
            'afterschoolafrica', 'youthop', 'mastersportal', 'phdportal',
            'opportunitiesforafricans', 'scholarshipsads'
        ]

        is_aggregator = any(agg in link_domain for agg in aggregator_domains)

        if is_aggregator:
            print(f"  Link is from aggregator: {link_domain}")
            print(f"  Fetching to find official link...")

            r = fetch(link)
            if r:
                soup = BeautifulSoup(r.text, 'lxml')
                official_link = find_official_link(soup, link)

                if official_link and official_link != link:
                    print(f"  Found official link: {official_link[:70]}")
                    cur.execute(
                        "UPDATE scholarship_details SET scholarship_link=%s WHERE id=%s",
                        (official_link, sid)
                    )
                    cur.execute(
                        "UPDATE scholarships SET link=%s WHERE link=%s",
                        (official_link, link)
                    )
                    fixed_links += 1
                else:
                    print(f"  No official link found — keeping aggregator link")
                    kept += 1
            else:
                print(f"  Could not fetch page — keeping")
                kept += 1
        else:
            print(f"  Link is official: {link_domain} — keeping")
            kept += 1

        time.sleep(random.uniform(1, 2))

    cur.close()
    conn.close()

    print(f"\n{'='*55}")
    print(f"  Deleted outdated : {deleted}")
    print(f"  Fixed links      : {fixed_links}")
    print(f"  Kept as is       : {kept}")
    print(f"{'='*55}")

if __name__ == "__main__":
    print("="*55)
    print("  FIXING EXISTING DATA")
    print("  1. Removing outdated scholarships")
    print("  2. Replacing aggregator links with official links")
    print("="*55)
    fix_existing_data()