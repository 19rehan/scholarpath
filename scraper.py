import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import time
import random
from datetime import datetime

# ─── ROTATING HEADERS (bypass blocking) ───────────────────
def get_headers():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    return {
        "User-Agent": random.choice(agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

# ─── SMART FETCH (retries + delays) ───────────────────────
def smart_fetch(url, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(2, 4))
            response = requests.get(url, headers=get_headers(), timeout=15)
            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                print(f"  ⚠ Blocked (403) on attempt {attempt+1}, retrying...")
                time.sleep(random.uniform(5, 10))
            elif response.status_code == 429:
                print(f"  ⚠ Rate limited (429), waiting 15 seconds...")
                time.sleep(15)
            else:
                print(f"  ⚠ Status {response.status_code}, retrying...")
        except Exception as e:
            print(f"  ✗ Connection error: {e}")
            time.sleep(5)
    return None

# ─── SMART TEXT EXTRACTOR ─────────────────────────────────
def extract_text(element):
    if not element:
        return ""
    return ' '.join(element.get_text(separator=' ', strip=True).split())

# ─── SMART TITLE FINDER ───────────────────────────────────
def find_title(soup_element):
    for tag in ['h1', 'h2', 'h3', 'h4']:
        found = soup_element.find(tag)
        if found and found.get_text(strip=True):
            return found.get_text(strip=True)
    # Try common class names
    for cls in ['title', 'post-title', 'entry-title', 'article-title']:
        found = soup_element.find(class_=cls)
        if found:
            return found.get_text(strip=True)
    return None

# ─── SMART LINK FINDER ────────────────────────────────────
def find_link(soup_element, base_url=""):
    for tag in ['h1', 'h2', 'h3', 'h4']:
        heading = soup_element.find(tag)
        if heading:
            a = heading.find('a', href=True)
            if a:
                href = a['href']
                if href.startswith('http'):
                    return href
                return base_url + href
    a = soup_element.find('a', href=True)
    if a:
        href = a['href']
        if href.startswith('http'):
            return href
        return base_url + href
    return ""

# ─── SMART DESCRIPTION FINDER ─────────────────────────────
def find_description(soup_element):
    # Try multiple paragraph tags
    paras = soup_element.find_all('p')
    for p in paras:
        text = p.get_text(strip=True)
        if len(text) > 40:
            return text[:500]
    # Fallback: any div with text
    divs = soup_element.find_all('div')
    for d in divs:
        text = d.get_text(strip=True)
        if len(text) > 40:
            return text[:500]
    return "Visit link for full details."

# ─── DATABASE SETUP ───────────────────────────────────────
def setup_database():
    conn = sqlite3.connect('scholarships.db')
    c = conn.cursor()
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
    conn.commit()
    return conn

# ─── SAVE SCHOLARSHIP ─────────────────────────────────────
def save(conn, title, description, country, deadline, link, source):
    if not title or len(title) < 5:
        return
    if not link:
        return
    try:
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO scholarships
            (title, description, country, deadline, link, source, scraped_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, country, deadline, link, source,
              datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        print(f"  ✓ {title[:70]}")
    except Exception as e:
        print(f"  ✗ Save error: {e}")

# ─── SCRAPER 1: SCHOLARS4DEV ──────────────────────────────
def scrape_scholars4dev(conn):
    print("\n[1] Scraping scholars4dev.com ...")
    pages = [
        "https://www.scholars4dev.com/",
        "https://www.scholars4dev.com/page/2/",
        "https://www.scholars4dev.com/page/3/",
    ]
    count = 0
    for url in pages:
        response = smart_fetch(url)
        if not response:
            continue
        soup = BeautifulSoup(response.text, 'lxml')

        # Try every possible post container
        containers = (
            soup.find_all('article') or
            soup.find_all('div', class_=lambda c: c and 'post' in c.lower()) or
            soup.find_all('div', class_=lambda c: c and 'entry' in c.lower())
        )

        # Fallback: grab all h2 links directly
        if not containers:
            print("  → No containers found, using h2 fallback...")
            for h2 in soup.find_all('h2'):
                a = h2.find('a', href=True)
                if a:
                    title = h2.get_text(strip=True)
                    link = a['href']
                    save(conn, title, "Visit link for full details.", "Various", "See link", link, "scholars4dev")
                    count += 1
            continue

        for item in containers:
            title = find_title(item)
            link = find_link(item, "https://www.scholars4dev.com")
            desc = find_description(item)
            if title and link:
                save(conn, title, desc, "Various", "See link", link, "scholars4dev")
                count += 1

    print(f"  → scholars4dev total: {count}")

# ─── SCRAPER 2: OPPORTUNITYDESK ───────────────────────────
def scrape_opportunitydesk(conn):
    print("\n[2] Scraping opportunitydesk.org ...")
    pages = [
        "https://opportunitydesk.org/category/scholarships/",
        "https://opportunitydesk.org/category/scholarships/page/2/",
    ]
    count = 0
    for url in pages:
        response = smart_fetch(url)
        if not response:
            continue
        soup = BeautifulSoup(response.text, 'lxml')

        containers = (
            soup.find_all('article') or
            soup.find_all('div', class_=lambda c: c and 'post' in c.lower())
        )

        if not containers:
            for h2 in soup.find_all(['h2', 'h3']):
                a = h2.find('a', href=True)
                if a:
                    title = h2.get_text(strip=True)
                    link = a['href']
                    save(conn, title, "Visit link for full details.", "Various", "See link", link, "opportunitydesk")
                    count += 1
            continue

        for item in containers:
            title = find_title(item)
            link = find_link(item, "https://opportunitydesk.org")
            desc = find_description(item)
            if title and link:
                save(conn, title, desc, "Various", "See link", link, "opportunitydesk")
                count += 1

    print(f"  → opportunitydesk total: {count}")

# ─── SCRAPER 3: SCHOLARSHIPDB ─────────────────────────────
def scrape_scholarshipdb(conn):
    print("\n[3] Scraping scholarshipdb.net ...")
    pages = [
        "https://scholarshipdb.net/scholarships",
        "https://scholarshipdb.net/scholarships?page=2",
    ]
    count = 0
    for url in pages:
        response = smart_fetch(url)
        if not response:
            continue
        soup = BeautifulSoup(response.text, 'lxml')

        # scholarshipdb uses list items
        items = (
            soup.find_all('li', class_=lambda c: c and 'scholarship' in str(c).lower()) or
            soup.find_all('div', class_=lambda c: c and 'scholarship' in str(c).lower()) or
            soup.find_all('article') or
            soup.find_all('tr')
        )

        if not items:
            for a in soup.find_all('a', href=True):
                href = a['href']
                title = a.get_text(strip=True)
                if len(title) > 20 and 'scholarship' in title.lower():
                    full_link = href if href.startswith('http') else "https://scholarshipdb.net" + href
                    save(conn, title, "Visit link for full details.", "Various", "See link", full_link, "scholarshipdb")
                    count += 1
            continue

        for item in items:
            title = find_title(item) or extract_text(item.find('a'))
            link_tag = item.find('a', href=True)
            if link_tag:
                href = link_tag['href']
                link = href if href.startswith('http') else "https://scholarshipdb.net" + href
            else:
                link = ""
            desc = find_description(item)
            if title and link:
                save(conn, title, desc, "Various", "See link", link, "scholarshipdb")
                count += 1

    print(f"  → scholarshipdb total: {count}")

# ─── SCRAPER 4: AFTERSCHOOLAFRICA ─────────────────────────
def scrape_afterschoolafrica(conn):
    print("\n[4] Scraping afterschoolafrica.com ...")
    pages = [
        "https://www.afterschoolafrica.com/category/scholarships/",
        "https://www.afterschoolafrica.com/category/scholarships/page/2/",
    ]
    count = 0
    for url in pages:
        response = smart_fetch(url)
        if not response:
            continue
        soup = BeautifulSoup(response.text, 'lxml')

        containers = soup.find_all('article') or soup.find_all('div', class_=lambda c: c and 'post' in str(c).lower())

        if not containers:
            for h in soup.find_all(['h2', 'h3']):
                a = h.find('a', href=True)
                if a:
                    save(conn, h.get_text(strip=True), "Visit link for full details.",
                         "Various", "See link", a['href'], "afterschoolafrica")
                    count += 1
            continue

        for item in containers:
            title = find_title(item)
            link = find_link(item)
            desc = find_description(item)
            if title and link:
                save(conn, title, desc, "Various", "See link", link, "afterschoolafrica")
                count += 1

    print(f"  → afterschoolafrica total: {count}")

# ─── EXPORT TO JSON ───────────────────────────────────────
def export_to_json(conn):
    print("\n[5] Exporting to scholarships.json ...")
    c = conn.cursor()
    c.execute("SELECT * FROM scholarships ORDER BY scraped_date DESC")
    rows = c.fetchall()
    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "country": row[3],
            "deadline": row[4],
            "link": row[5],
            "source": row[6],
            "scraped_date": row[7]
        })
    with open('scholarships.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Exported {len(data)} scholarships")
    return len(data)

# ─── MAIN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("   SMART SCHOLARSHIP SCRAPER v2.0")
    print("=" * 55)

    conn = setup_database()

    scrape_scholars4dev(conn)
    scrape_opportunitydesk(conn)
    scrape_scholarshipdb(conn)
    scrape_afterschoolafrica(conn)

    total = export_to_json(conn)

    print(f"\n{'=' * 55}")
    print(f"   DONE! Total scholarships in database: {total}")
    print(f"   Files: scholarships.db + scholarships.json")
    print(f"{'=' * 55}")

    conn.close()