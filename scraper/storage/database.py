import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_URL = "postgresql://postgres.deqyxksflvlxjelppgxz:Rehan1819Rehan@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def save_scholarship(data):
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        INSERT INTO scholarship_details 
        (title, scholarship_link, full_description, university_name, country,
         degree_level, deadline, funding_type, benefits, eligible_countries,
         language_requirement, how_to_apply, quality_score, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (scholarship_link) DO UPDATE SET
        title = EXCLUDED.title,
        quality_score = EXCLUDED.quality_score,
        last_updated = NOW()
        RETURNING id;
    """
    
    try:
        cur.execute(query, (
            data.get('title'),
            data.get('official_url'),
            data.get('full_description'),
            data.get('university_name'),
            data.get('country'),
            data.get('degree_level'),
            data.get('deadline'),
            data.get('funding_type'),
            data.get('benefits'),
            data.get('eligible_countries'),
            data.get('language_requirement'),
            data.get('how_to_apply'),
            data.get('quality_score')
        ))
        
        result = cur.fetchone()
        conn.commit()
        return result[0] if result else None
        
    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

def check_duplicate(url):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id FROM scholarship_details WHERE scholarship_link = %s", (url,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return result is not None
