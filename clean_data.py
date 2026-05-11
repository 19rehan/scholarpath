import psycopg2
import re

DATABASE_URL = 'postgresql://postgres.deqyxksflvlxjelppgxz:Rehan1819Rehan@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'

CURRENT_YEAR = 2026
CURRENT_MONTH = 5

def is_bad(title):
    if not title:
        return True, "no title"
    t = title.lower()
    bad = [
        'position', 'professor', 'lecturer', 'statistician',
        'postdoc', 'instructor', 'faculty', 'director', 'dean',
        'researcher', 'scientist', 'engineer', 'developer',
        'analyst', 'coordinator', 'manager', 'officer',
        'job fair', 'recruitment', 'hiring', 'vacancy',
        'top 10', 'top 5', 'top 20', 'top 25', 'top 50',
        'list of', 'best scholarships', 'countries where',
        'csc evaluation',
        'information for uk host',
    ]
    for b in bad:
        if b in t:
            return True, f"bad keyword: {b}"
    return False, None

def is_outdated(deadline):
    if not deadline:
        return False
    months = {
        'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
        'july':7,'august':8,'september':9,'october':10,'november':11,'december':12
    }
    dl = deadline.lower()
    year_m = re.search(r'(\d{4})', dl)
    if not year_m:
        return False
    year = int(year_m.group(1))
    if year < CURRENT_YEAR:
        return True
    if year == CURRENT_YEAR:
        for month_name, month_num in months.items():
            if month_name in dl:
                if month_num < CURRENT_MONTH:
                    return True
    return False

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

# Step 1: Remove duplicates — keep only the latest entry per title
print("Step 1: Removing duplicates...")
cur.execute("""
    DELETE FROM scholarship_details
    WHERE id NOT IN (
        SELECT MAX(id)
        FROM scholarship_details
        GROUP BY LOWER(title)
    )
""")
print(f"  Duplicates removed")

# Step 2: Remove bad titles and outdated
cur.execute("SELECT id, title, deadline, scholarship_link FROM scholarship_details")
rows = cur.fetchall()
print(f"\nStep 2: Checking {len(rows)} scholarships...")

deleted = 0
kept = 0

for sid, title, deadline, link in rows:
    bad, reason = is_bad(title)
    outdated = is_outdated(deadline)

    if bad or outdated:
        cur.execute("DELETE FROM scholarship_details WHERE id=%s", (sid,))
        cur.execute("DELETE FROM scholarships WHERE link=%s", (link,))
        print(f"  DELETED ({reason or 'outdated'}): {title[:60]}")
        deleted += 1
    else:
        print(f"  KEPT: {title[:60]}")
        kept += 1

cur.execute("SELECT COUNT(*) FROM scholarship_details")
remaining = cur.fetchone()[0]
cur.close()
conn.close()

print(f"\n{'='*55}")
print(f"  Duplicates removed : yes")
print(f"  Bad titles deleted : {deleted}")
print(f"  Clean remaining    : {remaining}")
print(f"{'='*55}")