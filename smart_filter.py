import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from datetime import datetime

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

# ─── CHECK IF SCHOLARSHIP IS STILL OPEN ───────────────────
def is_still_open(text, url):
    text_lower = text.lower()
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Hard closed signals
    closed_keywords = [
        'closed', 'expired', 'no longer accepting',
        'applications are closed', 'deadline has passed',
        'not accepting', 'competition is closed'
    ]
    for kw in closed_keywords:
        if kw in text_lower:
            return False, "Closed — keyword found"

    # Find all dates in page
    date_patterns = [
        r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})',
        r'(\d{4})-(\d{2})-(\d{2})',
    ]

    months = {
        'january':1,'february':2,'march':3,'april':4,
        'may':5,'june':6,'july':7,'august':8,
        'september':9,'october':10,'november':11,'december':12
    }

    found_future_date = False
    for pattern in date_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                if len(match) == 3:
                    if match[0].isdigit() and not match[2].isdigit():
                        day, month_name, year = int(match[0]), months.get(match[1], 0), int(match[2])
                    elif match[1].isdigit():
                        month_name_str, day, year = match[0], int(match[1]), int(match[2])
                        day = int(day)
                        month_name = months.get(month_name_str, 0)
                    else:
                        year, month_num, day = int(match[0]), int(match[1]), int(match[2])
                        month_name = month_num

                    if year > current_year:
                        found_future_date = True
                    elif year == current_year and month_name >= current_month:
                        found_future_date = True
            except:
                continue

    if found_future_date:
        return True, "Open — future deadline found"

    # Check if page mentions current or next year
    if str(current_year + 1) in text:
        return True, f"Open — mentions {current_year + 1}"
    if str(current_year) in text:
        return True, f"Possibly open — mentions {current_year}"

    return False, "Likely outdated — no future dates found"

# ─── SCRAPE FRESH OPEN SCHOLARSHIPS ───────────────────────
def scrape_fresh_sources(conn):
    print("\n[FRESH] Scraping sources known for open scholarships...")

    # These sources specifically list currently open scholarships
    fresh_sources = [
        {
            "url": "https://www.scholars4dev.com/",
            "name": "scholars4dev",
            "base": "https://www.scholars4dev.com"
        },
        {
            "url": "https://www.scholars4dev.com/page/2/",
            "name": "scholars4dev",
            "base": "https://www.scholars4dev.com"
        },
        {
            "url": "https://www.scholars4dev.com/page/3/",
            "name": "scholars4dev",
            "base": "https://www.scholars4dev.com"
        },
        {
            "url": "https://scholarshipdb.net/scholarships-in-United-Kingdom",
            "name": "scholarshipdb_uk",
            "base": "https://scholarshipdb.net"
        },
        {
            "url": "https://scholarshipdb.net/scholarships-in-Australia",
            "name": "scholarshipdb_au",
            "base": "https://scholarshipdb.net"
        },
        {
            "url": "https://scholarshipdb.net/scholarships-in-Canada",
            "name": "scholarshipdb_ca",
            "base": "https://scholarshipdb.net"
        },
        {
            "url": "https://scholarshipdb.net/scholarships-in-Germany",
            "name": "scholarshipdb_de",
            "base": "https://scholarshipdb.net"
        },
        {
            "url": "https://scholarshipdb.net/scholarships-in-USA",
            "name": "scholarshipdb_usa",
            "base": "https://scholarshipdb.net"
        },
    ]

    c = conn.cursor()
    saved = 0

    for source in fresh_sources:
        print(f"\n  Fetching: {source['url'][:60]}")
        try:
            time.sleep(random.uniform(2, 4))
            r = requests.get(source['url'], headers=get_headers(), timeout=15)
            if r.status_code != 200:
                print(f"  ⚠ Status {r.status_code}")
                continue

            soup = BeautifulSoup(r.text, 'lxml')

            # Remove noise
            for tag in soup.find_all(['nav','footer','script','style','aside']):
                tag.decompose()

            # Find all scholarship links
            links_found = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                title = a.get_text(strip=True)
                if len(title) < 15:
                    continue
                if any(skip in href.lower() for skip in ['category','tag','page','#','mailto','javascript']):
                    continue
                if not href.startswith('http'):
                    href = source['base'] + href
                links_found.append((title, href))

            # Also grab h2/h3 links
            for heading in soup.find_all(['h2','h3']):
                a = heading.find('a', href=True)
                if a:
                    href = a['href']
                    title = heading.get_text(strip=True)
                    if not href.startswith('http'):
                        href = source['base'] + href
                    links_found.append((title, href))

            print(f"  Found {len(links_found)} links")

            # Visit each link and check if open
            for title, link in links_found[:15]:  # Max 15 per source
                # Skip if already in db
                existing = c.execute(
                    "SELECT id FROM scholarships WHERE link=?", (link,)
                ).fetchone()
                if existing:
                    continue

                time.sleep(random.uniform(2, 3))
                try:
                    detail_r = requests.get(link, headers=get_headers(), timeout=12)
                    if detail_r.status_code != 200:
                        continue

                    page_text = detail_r.text
                    soup2 = BeautifulSoup(page_text, 'lxml')
                    clean_text = soup2.get_text(separator=' ', strip=True)

                    is_open, reason = is_still_open(clean_text, link)

                    if is_open:
                        # Get description
                        paras = soup2.find_all('p')
                        desc = ""
                        for p in paras:
                            t = p.get_text(strip=True)
                            if len(t) > 60:
                                desc = t[:400]
                                break

                        c.execute('''
                            INSERT OR IGNORE INTO scholarships
                            (title, description, country, deadline, link, source, scraped_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            title,
                            desc or "Visit link for full details.",
                            "Various",
                            "See official website",
                            link,
                            source['name'],
                            datetime.now().strftime("%Y-%m-%d")
                        ))
                        conn.commit()
                        saved += 1
                        print(f"  ✓ OPEN: {title[:60]}")
                        print(f"         Reason: {reason}")
                    else:
                        print(f"  ✗ SKIP: {title[:50]} ({reason})")

                except Exception as e:
                    print(f"  ✗ Error visiting {link[:50]}: {e}")

        except Exception as e:
            print(f"  ✗ Error fetching source: {e}")

    return saved

# ─── REMOVE OUTDATED FROM DATABASE ────────────────────────
def clean_outdated(conn):
    print("\n[CLEAN] Checking existing scholarships for outdated ones...")
    c = conn.cursor()
    c.execute("SELECT id, title, link FROM scholarships")
    all_scholarships = c.fetchall()

    removed = 0
    kept = 0

    for sid, title, link in all_scholarships:
        if not link or not link.startswith('http'):
            c.execute("DELETE FROM scholarships WHERE id=?", (sid,))
            c.execute("DELETE FROM scholarship_details WHERE scholarship_link=?", (link,))
            conn.commit()
            removed += 1
            continue

        try:
            time.sleep(random.uniform(1, 2))
            r = requests.get(link, headers=get_headers(), timeout=12)
            if r.status_code == 404:
                print(f"  ✗ REMOVED (404): {title[:50]}")
                c.execute("DELETE FROM scholarships WHERE id=?", (sid,))
                c.execute("DELETE FROM scholarship_details WHERE scholarship_link=?", (link,))
                conn.commit()
                removed += 1
                continue

            soup = BeautifulSoup(r.text, 'lxml')
            clean_text = soup.get_text(separator=' ', strip=True)
            is_open, reason = is_still_open(clean_text, link)

            if not is_open:
                print(f"  ✗ REMOVED: {title[:50]} ({reason})")
                c.execute("DELETE FROM scholarships WHERE id=?", (sid,))
                c.execute("DELETE FROM scholarship_details WHERE scholarship_link=?", (link,))
                conn.commit()
                removed += 1
            else:
                print(f"  ✓ KEPT: {title[:50]}")
                kept += 1

        except Exception as e:
            print(f"  ⚠ Could not check {title[:40]}: {e}")
            kept += 1

    return removed, kept

# ─── MAIN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("   SCHOLARSHIP FRESHNESS FILTER")
    print("=" * 55)

    conn = sqlite3.connect('scholarships.db')

    # Step 1: Remove outdated
    removed, kept = clean_outdated(conn)

    # Step 2: Add fresh open ones
    added = scrape_fresh_sources(conn)

    # Summary
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM scholarships").fetchone()[0]

    print(f"\n{'=' * 55}")
    print(f"  Removed outdated : {removed}")
    print(f"  Kept open        : {kept}")
    print(f"  Newly added      : {added}")
    print(f"  Total in database: {total}")
    print(f"{'=' * 55}")

    conn.close()