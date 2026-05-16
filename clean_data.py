"""
ADMITGOAL — Database Cleaner
Removes garbage, expired, and duplicate scholarships
"""

import psycopg2
from datetime import datetime

DATABASE_URL = 'postgresql://postgres.deqyxksflvlxjelppgxz:Rehan1819Rehan@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'

CURRENT_YEAR = datetime.now().year

def clean_database():
    print("="*60)
    print("🧹 CLEANING DATABASE")
    print("="*60)
    
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Count before
    cur.execute("SELECT COUNT(*) FROM scholarship_details")
    before = cur.fetchone()[0]
    print(f"\n📊 Before: {before} scholarships")
    
    # 1. Delete garbage titles
    garbage_patterns = [
        "consent", "cookies", "apply now", "read more", "click here",
        "scholars4dev", "opportunitydesk", "afterschool", "scholarshipdb",
        "top 10", "top 20", "top 25", "best scholarships", "list of"
    ]
    
    deleted_garbage = 0
    for pattern in garbage_patterns:
        cur.execute(f"DELETE FROM scholarship_details WHERE LOWER(title) LIKE '%{pattern}%'")
        deleted_garbage += cur.rowcount
    
    print(f"❌ Deleted {deleted_garbage} garbage titles")
    
    # 2. Delete expired deadlines (anything with year < current year in deadline)
    cur.execute(f"""
        DELETE FROM scholarship_details 
        WHERE deadline LIKE '%2017%' OR deadline LIKE '%2018%' 
           OR deadline LIKE '%2019%' OR deadline LIKE '%2020%'
           OR deadline LIKE '%2021%' OR deadline LIKE '%2022%'
           OR deadline LIKE '%2023%' OR deadline LIKE '%2024%'
           OR deadline LIKE '%2025%'
    """)
    deleted_expired = cur.rowcount
    print(f"❌ Deleted {deleted_expired} expired deadlines")
    
    # 3. Delete short titles (< 15 chars)
    cur.execute("DELETE FROM scholarship_details WHERE LENGTH(title) < 15")
    deleted_short = cur.rowcount
    print(f"❌ Deleted {deleted_short} short titles")
    
    # 4. Delete job listings
    job_keywords = ['professor', 'lecturer', 'position', 'vacancy', 'hiring', 'recruitment']
    deleted_jobs = 0
    for keyword in job_keywords:
        cur.execute(f"DELETE FROM scholarship_details WHERE LOWER(title) LIKE '%{keyword}%'")
        deleted_jobs += cur.rowcount
    
    print(f"❌ Deleted {deleted_jobs} job listings")
    
    # 5. Delete duplicates (keep newest)
    cur.execute("""
        DELETE FROM scholarship_details a
        USING scholarship_details b
        WHERE a.id < b.id 
        AND a.scholarship_link = b.scholarship_link
    """)
    deleted_dupes = cur.rowcount
    print(f"❌ Deleted {deleted_dupes} duplicates")
    
    # 6. Delete missing official links
    cur.execute("DELETE FROM scholarship_details WHERE scholarship_link IS NULL OR scholarship_link = ''")
    deleted_no_link = cur.rowcount
    print(f"❌ Deleted {deleted_no_link} missing links")
    
    # Count after
    cur.execute("SELECT COUNT(*) FROM scholarship_details")
    after = cur.fetchone()[0]
    
    print(f"\n📊 After: {after} scholarships")
    print(f"✅ Cleaned: {before - after} removed")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    clean_database()
