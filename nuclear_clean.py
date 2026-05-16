import psycopg2
from datetime import datetime

DATABASE_URL = 'postgresql://postgres.deqyxksflvlxjelppgxz:Rehan1819Rehan@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'

print("="*60)
print("🔥 NUCLEAR CLEAN — Deleting ALL scholarship data")
print("="*60)

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

# Count before
cur.execute("SELECT COUNT(*) FROM scholarship_details")
before = cur.fetchone()[0]
print(f"\nBefore: {before} scholarships")

# DELETE EVERYTHING
cur.execute("DELETE FROM scholarship_details")

# Count after
cur.execute("SELECT COUNT(*) FROM scholarship_details")
after = cur.fetchone()[0]
print(f"After: {after} scholarships")

print(f"\n✅ Deleted {before} entries")
print("Database is now CLEAN")

cur.close()
conn.close()
