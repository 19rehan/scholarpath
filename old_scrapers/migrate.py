import sqlite3
import psycopg2
import os

# Paste your Supabase connection string here
SUPABASE_URL = "postgresql://postgres:[admin1234]@db.deqyxksflvlxjelppgxz.supabase.co:5432/postgres"

def migrate():
    print("Connecting to SQLite...")
    sqlite_conn = sqlite3.connect('scholarships.db')
    sqlite_conn.row_factory = sqlite3.Row
    sc = sqlite_conn.cursor()

    print("Connecting to Supabase...")
    pg_conn = psycopg2.connect(SUPABASE_URL)
    pc = pg_conn.cursor()

    # Migrate scholarships
    rows = sc.execute("SELECT * FROM scholarships").fetchall()
    print(f"Migrating {len(rows)} scholarships...")
    for row in rows:
        try:
            pc.execute('''INSERT INTO scholarships
                (title,description,country,deadline,link,source,scraped_date)
                VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (link) DO NOTHING''',
                (row['title'],row['description'],row['country'],
                 row['deadline'],row['link'],row['source'],row['scraped_date']))
        except Exception as e:
            print(f"  Skip: {e}")

    # Migrate scholarship_details
    rows = sc.execute("SELECT * FROM scholarship_details").fetchall()
    print(f"Migrating {len(rows)} scholarship details...")
    for row in rows:
        try:
            pc.execute('''INSERT INTO scholarship_details
                (scholarship_link,title,full_description,eligible_countries,
                 eligible_students,degree_level,deadline,language_requirement,
                 ielts_score,benefits,how_to_apply,blog_post,seo_title,
                 seo_description,university_name,country,region,
                 funding_type,gpa_required,last_updated)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (scholarship_link) DO NOTHING''',
                (row['scholarship_link'],row['title'],row['full_description'],
                 row['eligible_countries'],row['eligible_students'],
                 row['degree_level'],row['deadline'],row['language_requirement'],
                 row['ielts_score'],row['benefits'],row['how_to_apply'],
                 row['blog_post'],row['seo_title'],row['seo_description'],
                 row['university_name'] if 'university_name' in row.keys() else '',
                 row['country'] if 'country' in row.keys() else '',
                 row['region'] if 'region' in row.keys() else '',
                 row['funding_type'] if 'funding_type' in row.keys() else '',
                 row['gpa_required'] if 'gpa_required' in row.keys() else '',
                 row['last_updated']))
        except Exception as e:
            print(f"  Skip: {e}")

    pg_conn.commit()
    pc.execute("SELECT COUNT(*) FROM scholarship_details")
    total = pc.fetchone()[0]
    print(f"\nMigration complete! {total} scholarships in Supabase.")
    sqlite_conn.close()
    pg_conn.close()

if __name__ == "__main__":
    migrate()