import sqlite3
from datetime import datetime

def generate_sitemap():
    conn = sqlite3.connect('scholarships.db')
    c = conn.cursor()
    rows = c.execute(
        "SELECT id, last_updated FROM scholarship_details"
    ).fetchall()
    conn.close()

    urls = []
    base = "https://www.scholarpath.com"

    # Static pages
    static = ['', '/about', '/contact', '/privacy',
              '/search?q=fully+funded', '/search?q=no+ielts',
              '/search?q=phd', '/search?q=masters',
              '/search?q=germany', '/search?q=china',
              '/search?q=turkey', '/search?q=korea',
              '/search?q=australia', '/search?q=canada',
              '/search?q=uk', '/search?q=usa',
              '/search?q=saudi+arabia', '/search?q=malaysia']

    for path in static:
        urls.append(f"""  <url>
    <loc>{base}{path}</loc>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>""")

    # Dynamic scholarship pages
    for sid, updated in rows:
        urls.append(f"""  <url>
    <loc>{base}/scholarship/{sid}</loc>
    <lastmod>{updated or datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>""")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    with open('static/sitemap.xml', 'w') as f:
        f.write(sitemap)
    print(f"sitemap.xml generated with {len(urls)} URLs")

def generate_robots():
    robots = """User-agent: *
Allow: /
Disallow: /ask

Sitemap: https://www.scholarpath.com/sitemap.xml"""
    with open('static/robots.txt', 'w') as f:
        f.write(robots)
    print("robots.txt generated")

if __name__ == "__main__":
    import os
    os.makedirs('static', exist_ok=True)
    generate_sitemap()
    generate_robots()
    print("SEO files ready")