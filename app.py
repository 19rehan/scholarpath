import psycopg2
import psycopg2.extras
import os
import re
from datetime import datetime
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    import os
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise Exception("DATABASE_URL is None - not set in environment")
    if 'vercel' in db_url.lower():
        raise Exception(f"DATABASE_URL is wrong value: {db_url[:50]}")
    conn = psycopg2.connect(db_url)
    return conn

def cur(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def convert_to_html(text):
    if not text: return ""
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    lines = text.split('\n')
    html_lines = []
    in_table = False
    first_row = True
    for line in lines:
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                html_lines.append('<table>')
                in_table = True
                first_row = True
            if re.match(r'\|[\s\-|]+\|', line):
                continue
            cols = [c.strip() for c in line.strip('|').split('|')]
            if first_row:
                html_lines.append('<thead><tr>' + ''.join(f'<th>{c}</th>' for c in cols) + '</tr></thead><tbody>')
                first_row = False
            else:
                html_lines.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cols) + '</tr>')
        else:
            if in_table:
                html_lines.append('</tbody></table>')
                in_table = False
                first_row = True
            html_lines.append(line)
    if in_table:
        html_lines.append('</tbody></table>')
    text = '\n'.join(html_lines)
    text = re.sub(r'^[-*] (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n?)+', lambda m: f'<ul>{m.group()}</ul>', text, flags=re.DOTALL)
    text = re.sub(r'^---$', '<hr>', text, flags=re.MULTILINE)
    text = re.sub(r'\n\n+', '</p><p>', text)
    return f'<p>{text}</p>'

BASE_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --primary:#4f46e5;--primary-dark:#3730a3;--secondary:#06b6d4;
  --success:#10b981;--dark:#0f172a;--gray:#64748b;
  --light:#f8fafc;--border:#e2e8f0;
  --shadow:0 4px 6px -1px rgba(0,0,0,0.07),0 2px 4px -1px rgba(0,0,0,0.04);
  --shadow-lg:0 20px 25px -5px rgba(0,0,0,0.1),0 10px 10px -5px rgba(0,0,0,0.04);
}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Inter',sans-serif;background:#f1f5f9;color:var(--dark);}
nav{background:white;border-bottom:1px solid var(--border);padding:0 40px;display:flex;align-items:center;justify-content:space-between;height:64px;position:sticky;top:0;z-index:100;box-shadow:0 1px 3px rgba(0,0,0,0.08);}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;}
.logo-icon{width:36px;height:36px;background:var(--primary);border-radius:10px;display:flex;align-items:center;justify-content:center;color:white;font-size:18px;}
.logo-text{font-size:20px;font-weight:800;color:var(--dark);}
.logo-text span{color:var(--primary);}
.nav-links{display:flex;gap:6px;align-items:center;}
.nav-links a{padding:8px 14px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:500;color:var(--gray);transition:all 0.2s;}
.nav-links a:hover{background:var(--light);color:var(--primary);}
.nav-cta{background:var(--primary)!important;color:white!important;border-radius:8px!important;}
@media(max-width:768px){nav{padding:0 16px;}.hide-mobile{display:none!important;}}
</style>"""

NAV = """<nav>
  <a href="/" class="logo">
    <div class="logo-icon">🎓</div>
    <div class="logo-text">Scholar<span>Path</span></div>
  </a>
  <div class="nav-links">
    <a href="/search?q=fully+funded" class="hide-mobile">Fully Funded</a>
    <a href="/search?q=no+ielts" class="hide-mobile">No IELTS</a>
    <a href="/search?q=phd" class="hide-mobile">PhD</a>
    <a href="/about" class="hide-mobile">About</a>
    <a href="/contact" class="nav-cta">Get Help</a>
  </div>
</nav>"""

@app.route('/')
def home():
    conn = get_db()
    c = cur(conn)
    level = request.args.get('level','')
    region = request.args.get('region','')

    query = "SELECT sd.*, s.source FROM scholarship_details sd LEFT JOIN scholarships s ON sd.scholarship_link=s.link"
    params = []
    conditions = []
    if level:
        conditions.append("sd.degree_level ILIKE %s")
        params.append(f'%{level}%')
    if region:
        conditions.append("sd.region ILIKE %s")
        params.append(f'%{region}%')
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY sd.id DESC LIMIT 60"

    c.execute(query, params)
    rows = c.fetchall()
    c.execute("SELECT COUNT(*) as cnt FROM scholarship_details")
    total = c.fetchone()['cnt']
    c.execute("SELECT COUNT(DISTINCT country) as cnt FROM scholarship_details")
    countries_count = c.fetchone()['cnt']
    c.close()
    conn.close()

    cards_html = ""
    for s in rows:
        is_funded = ('full' in (s['funding_type'] or '').lower() or 'full' in (s['title'] or '').lower())
        funded_badge = '<span class="badge badge-green">💰 Fully Funded</span>' if is_funded else '<span class="badge badge-gray">Funding Available</span>'
        ielts_val = s['ielts_score'] or ''
        ielts_badge = f'<span class="badge badge-orange">IELTS {ielts_val}</span>' if ielts_val and ielts_val not in ['Not required','Not mentioned','Check website'] else '<span class="badge badge-teal">✅ No IELTS</span>'
        degree_badge = f'<span class="badge badge-blue">🎓 {str(s["degree_level"] or "")[:25]}</span>' if s['degree_level'] and s['degree_level'] != 'Not specified' else ''
        deadline_html = f'<div class="deadline-row">📅 Deadline: {s["deadline"]}</div>' if s['deadline'] and s['deadline'] not in ['See link','See official website'] else ''
        cards_html += f"""<div class="card">
          <div class="card-top">
            <span class="card-country">🌍 {s['country'] or 'International'}</span>
            <span class="card-region">{s['region'] or ''}</span>
          </div>
          <h3>{s['seo_title'] or s['title'] or 'Scholarship Opportunity'}</h3>
          <div class="badges">{degree_badge}{ielts_badge}{funded_badge}</div>
          <p class="card-desc">{s['seo_description'] or s['full_description'] or 'International scholarship. Click for full details.'}</p>
          <div class="card-footer">{deadline_html}<a href="/scholarship/{s['id']}" class="card-btn">View Full Guide & Apply →</a></div>
        </div>"""

    active_level = level
    active_region = region
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ScholarPath – Free AI Scholarship Finder | Pakistan India Bangladesh Africa</title>
<meta name="google-site-verification" content="zKOcXjMcvxwhAnjJdQBtkxSOiyBWSJ2sU8fRXl7ZFUI" />
<meta name="description" content="Find fresh scholarships from universities worldwide. Free AI guidance on eligibility, IELTS, SOP writing. No agent needed. Updated daily.">
<meta property="og:title" content="ScholarPath – Find Scholarships Worldwide Free">
<meta property="og:description" content="AI-powered scholarship finder. Fresh daily. IELTS guidance. SOP help. Free.">
<link rel="canonical" href="https://scholarpath.onrender.com/">
{BASE_CSS}
<style>
.hero{{background:linear-gradient(135deg,#1e1b4b 0%,#312e81 40%,#4338ca 70%,#0891b2 100%);color:white;padding:80px 20px 70px;text-align:center;position:relative;overflow:hidden;}}
.hero::before{{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle at 30% 50%,rgba(99,102,241,0.3) 0%,transparent 50%);animation:float 8s ease-in-out infinite;}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-20px)}}}}
.hero-content{{position:relative;z-index:1;}}
.hero-badge{{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.15);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.2);padding:8px 20px;border-radius:100px;font-size:13px;font-weight:500;margin-bottom:24px;}}
.hero h1{{font-size:clamp(28px,5vw,56px);font-weight:800;line-height:1.15;margin-bottom:18px;letter-spacing:-1px;}}
.hero h1 span{{color:#67e8f9;}}
.hero p{{font-size:17px;opacity:0.85;max-width:560px;margin:0 auto 36px;line-height:1.7;}}
.search-wrap{{max-width:580px;margin:0 auto;}}
.search-box{{display:flex;background:white;border-radius:14px;padding:6px;box-shadow:0 25px 50px rgba(0,0,0,0.25);}}
.search-box input{{flex:1;border:none;outline:none;padding:13px 18px;font-size:15px;color:var(--dark);background:transparent;font-family:'Inter',sans-serif;}}
.search-box button{{background:var(--primary);color:white;border:none;padding:13px 24px;border-radius:10px;cursor:pointer;font-size:15px;font-weight:600;white-space:nowrap;}}
.tags{{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-top:18px;}}
.tag{{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);color:white;padding:6px 14px;border-radius:100px;font-size:12px;text-decoration:none;}}
.tag:hover{{background:rgba(255,255,255,0.25);}}
.stats{{display:flex;justify-content:center;background:white;border-bottom:1px solid var(--border);flex-wrap:wrap;}}
.stat{{text-align:center;padding:24px 40px;border-right:1px solid var(--border);}}
.stat:last-child{{border-right:none;}}
.stat-num{{font-size:30px;font-weight:800;color:var(--primary);}}
.stat-label{{font-size:12px;color:var(--gray);margin-top:3px;font-weight:500;}}
.filter-bar{{background:white;border-bottom:1px solid var(--border);padding:14px 40px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;}}
.filter-label{{font-size:12px;font-weight:700;color:var(--gray);text-transform:uppercase;letter-spacing:0.5px;}}
.filter-btn{{padding:7px 16px;border-radius:100px;font-size:13px;font-weight:500;cursor:pointer;border:1.5px solid var(--border);background:white;color:var(--gray);transition:all 0.2s;text-decoration:none;}}
.filter-btn:hover,.filter-btn.active{{background:var(--primary);color:white;border-color:var(--primary);}}
.main{{max-width:1280px;margin:28px auto;padding:0 20px;}}
.regions{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:28px;}}
.rc{{padding:10px 20px;border-radius:10px;font-size:13px;font-weight:600;text-decoration:none;transition:all 0.2s;border:2px solid transparent;display:flex;align-items:center;gap:6px;}}
.rc:hover{{transform:translateY(-2px);box-shadow:var(--shadow);}}
.rc-eu{{background:#eef2ff;color:#4338ca;}}.rc-as{{background:#fef3c7;color:#92400e;}}
.rc-me{{background:#fce7f3;color:#9d174d;}}.rc-oc{{background:#d1fae5;color:#065f46;}}
.rc-na{{background:#dbeafe;color:#1e40af;}}.rc-af{{background:#fef9c3;color:#713f12;}}
.section-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;}}
.section-title{{font-size:20px;font-weight:700;}}
.section-count{{font-size:13px;color:var(--gray);}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px;}}
.card{{background:white;border-radius:14px;padding:22px;box-shadow:var(--shadow);transition:all 0.25s;border:1px solid var(--border);display:flex;flex-direction:column;position:relative;overflow:hidden;}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--primary),var(--secondary));}}
.card:hover{{transform:translateY(-5px);box-shadow:var(--shadow-lg);}}
.card-top{{display:flex;justify-content:space-between;margin-bottom:12px;}}
.card-country{{font-size:11px;font-weight:600;color:var(--primary);background:#eef2ff;padding:3px 10px;border-radius:100px;}}
.card-region{{font-size:11px;color:var(--gray);}}
.card h3{{font-size:14px;font-weight:700;line-height:1.5;margin-bottom:10px;}}
.badges{{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:12px;}}
.badge{{padding:3px 10px;border-radius:100px;font-size:11px;font-weight:500;}}
.badge-blue{{background:#eff6ff;color:#1d4ed8;}}.badge-green{{background:#f0fdf4;color:#15803d;}}
.badge-orange{{background:#fff7ed;color:#c2410c;}}.badge-teal{{background:#ecfeff;color:#0e7490;}}
.badge-gray{{background:#f8fafc;color:#475569;}}
.card-desc{{font-size:12px;color:var(--gray);line-height:1.7;margin-bottom:14px;flex:1;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;}}
.card-footer{{margin-top:auto;}}
.deadline-row{{font-size:11px;font-weight:600;color:#dc2626;margin-bottom:10px;padding:7px 10px;background:#fef2f2;border-radius:6px;}}
.card-btn{{display:block;text-align:center;background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:white;padding:11px;border-radius:9px;text-decoration:none;font-size:13px;font-weight:600;}}
.card-btn:hover{{opacity:0.9;}}
footer{{background:var(--dark);color:rgba(255,255,255,0.6);text-align:center;padding:40px 20px;margin-top:50px;font-size:13px;line-height:2.2;}}
footer a{{color:#818cf8;text-decoration:none;}}
footer strong{{color:white;}}
@media(max-width:640px){{.stat{{padding:18px 20px;}}.filter-bar{{padding:12px 16px;}}.main{{padding:16px;}}.grid{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>
{NAV}
<div class="hero">
  <div class="hero-content">
    <div class="hero-badge">🚀 Scholarships updated daily — {datetime.now().strftime('%B %Y')}</div>
    <h1>Find Your <span>Dream Scholarship</span><br>Anywhere in the World</h1>
    <p>No agent. No fees. AI finds scholarships from universities in Europe, Asia, Middle East, Africa and beyond — matched to you.</p>
    <div class="search-wrap">
      <form method="GET" action="/search">
        <div class="search-box">
          <input type="text" name="q" placeholder="Country, university, field..." autocomplete="off">
          <button type="submit">Search →</button>
        </div>
      </form>
      <div class="tags">
        <a href="/search?q=germany" class="tag">🇩🇪 Germany</a>
        <a href="/search?q=china" class="tag">🇨🇳 China</a>
        <a href="/search?q=turkey" class="tag">🇹🇷 Turkey</a>
        <a href="/search?q=korea" class="tag">🇰🇷 Korea</a>
        <a href="/search?q=saudi" class="tag">🇸🇦 Saudi</a>
        <a href="/search?q=fully funded" class="tag">💰 Fully Funded</a>
        <a href="/search?q=no ielts" class="tag">📝 No IELTS</a>
        <a href="/search?q=phd" class="tag">🔬 PhD</a>
      </div>
    </div>
  </div>
</div>
<div class="stats">
  <div class="stat"><div class="stat-num">{total}+</div><div class="stat-label">Live Scholarships</div></div>
  <div class="stat"><div class="stat-num">{countries_count}+</div><div class="stat-label">Countries</div></div>
  <div class="stat"><div class="stat-num">Free</div><div class="stat-label">No Agent Fee</div></div>
  <div class="stat"><div class="stat-num">Daily</div><div class="stat-label">Updated</div></div>
</div>
<div class="filter-bar">
  <span class="filter-label">Level:</span>
  <a href="/" class="filter-btn {'active' if not active_level else ''}">All</a>
  <a href="/?level=Bachelor" class="filter-btn {'active' if active_level=='Bachelor' else ''}">Bachelor</a>
  <a href="/?level=Master" class="filter-btn {'active' if active_level=='Master' else ''}">Master</a>
  <a href="/?level=PhD" class="filter-btn {'active' if active_level=='PhD' else ''}">PhD</a>
  <a href="/search?q=fully funded" class="filter-btn">Fully Funded</a>
  <a href="/search?q=no ielts" class="filter-btn">No IELTS</a>
</div>
<div class="main">
  <div class="regions">
    <a href="/?region=Europe" class="rc rc-eu">🌍 Europe</a>
    <a href="/?region=Asia" class="rc rc-as">🌏 Asia</a>
    <a href="/?region=Middle East" class="rc rc-me">🕌 Middle East</a>
    <a href="/?region=Oceania" class="rc rc-oc">🦘 Australia</a>
    <a href="/?region=North America" class="rc rc-na">🍁 North America</a>
    <a href="/?region=Africa" class="rc rc-af">🌍 Africa</a>
  </div>
  <div class="section-header">
    <div class="section-title">Latest Open Scholarships</div>
    <div class="section-count">Showing {len(rows)} of {total}</div>
  </div>
  <div class="grid">{cards_html if cards_html else '<div style="text-align:center;padding:60px;color:#94a3b8"><div style="font-size:48px">🔍</div><h3>Run the scraper to load scholarships</h3></div>'}</div>
</div>
<footer>
  <div>🎓 <strong>ScholarPath</strong> — Free AI Scholarship Finder</div>
  <div>Built for students in Pakistan · India · Bangladesh · Africa · and everywhere</div>
  <div style="margin-top:8px"><a href="/about">About</a> &nbsp;·&nbsp; <a href="/privacy">Privacy</a> &nbsp;·&nbsp; <a href="/contact">Contact</a> &nbsp;·&nbsp; <a href="/sitemap.xml">Sitemap</a></div>
  <div style="margin-top:8px;font-size:11px;opacity:0.4">© {datetime.now().year} ScholarPath · Replacing agents with AI</div>
</footer>
</body></html>"""
    return html

@app.route('/scholarship/<int:sid>')
def scholarship(sid):
    conn = get_db()
    c = cur(conn)
    c.execute("SELECT sd.*,s.source FROM scholarship_details sd LEFT JOIN scholarships s ON sd.scholarship_link=s.link WHERE sd.id=%s", (sid,))
    s = c.fetchone()
    c.close()
    conn.close()
    if not s:
        return "Scholarship not found", 404

    blog_html = convert_to_html(s['blog_post'] or "")
    title = s['seo_title'] or s['title'] or 'Scholarship'
    desc = s['seo_description'] or ''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} – ScholarPath</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<link rel="canonical" href="https://scholarpath.onrender.com/scholarship/{sid}">
{BASE_CSS}
<style>
.layout{{max-width:1100px;margin:28px auto;padding:0 20px;display:grid;grid-template-columns:1fr 300px;gap:20px;}}
.hero-card{{background:linear-gradient(135deg,#1e1b4b,#3730a3);color:white;border-radius:18px;padding:32px;margin-bottom:20px;}}
.hero-card .uni-badge{{display:inline-block;background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.2);padding:5px 14px;border-radius:100px;font-size:11px;font-weight:600;margin-bottom:14px;text-transform:uppercase;}}
.hero-card h1{{font-size:22px;font-weight:800;line-height:1.35;margin-bottom:14px;}}
.qbadges{{display:flex;flex-wrap:wrap;gap:7px;}}
.qb{{padding:5px 12px;border-radius:100px;font-size:11px;font-weight:600;background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.2);}}
.blog-card{{background:white;border-radius:14px;padding:32px;box-shadow:var(--shadow);border:1px solid var(--border);}}
.blog-card h1{{font-size:24px;font-weight:800;color:var(--dark);margin-bottom:20px;}}
.blog-card h2{{font-size:18px;font-weight:700;color:var(--primary);margin:24px 0 10px;padding-left:12px;border-left:4px solid var(--primary);}}
.blog-card h3{{font-size:15px;font-weight:700;color:var(--dark);margin:18px 0 8px;}}
.blog-card p{{font-size:14px;line-height:1.85;color:#374151;margin-bottom:12px;}}
.blog-card table{{width:100%;border-collapse:collapse;margin:18px 0;border-radius:8px;overflow:hidden;border:1px solid var(--border);}}
.blog-card thead th{{background:#f0f4ff;padding:11px 14px;text-align:left;font-size:12px;font-weight:700;color:var(--primary);}}
.blog-card tbody td{{padding:11px 14px;font-size:13px;border-top:1px solid var(--border);}}
.blog-card tbody tr:hover{{background:#fafbff;}}
.blog-card ul,.blog-card ol{{padding-left:20px;margin:12px 0;}}
.blog-card li{{font-size:14px;line-height:2;color:#374151;}}
.blog-card strong{{color:var(--primary);font-weight:700;}}
.blog-card hr{{border:none;border-top:2px solid var(--border);margin:24px 0;}}
.sidebar-card{{background:white;border-radius:14px;padding:20px;box-shadow:var(--shadow);border:1px solid var(--border);margin-bottom:16px;}}
.sidebar-card h3{{font-size:14px;font-weight:700;margin-bottom:14px;}}
.info-row{{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid var(--border);font-size:12px;}}
.info-row:last-child{{border-bottom:none;}}
.info-label{{color:var(--gray);font-weight:500;}}
.info-value{{font-weight:600;text-align:right;max-width:160px;}}
.apply-btn{{display:block;background:linear-gradient(135deg,#059669,#10b981);color:white;text-align:center;padding:14px;border-radius:11px;text-decoration:none;font-size:15px;font-weight:700;margin-bottom:10px;}}
.apply-btn:hover{{opacity:0.9;transform:translateY(-2px);}}
.ai-card{{background:linear-gradient(135deg,#0f172a,#1e1b4b);border-radius:14px;padding:20px;color:white;margin-bottom:16px;}}
.ai-card h3{{font-size:14px;font-weight:700;margin-bottom:5px;}}
.ai-card p{{font-size:12px;opacity:0.65;margin-bottom:14px;line-height:1.6;}}
.ai-inp{{width:100%;padding:10px 12px;border:1px solid rgba(255,255,255,0.2);border-radius:8px;font-size:13px;font-family:'Inter',sans-serif;background:rgba(255,255,255,0.08);color:white;outline:none;}}
.ai-inp::placeholder{{color:rgba(255,255,255,0.35);}}
.ai-btn{{width:100%;margin-top:8px;background:var(--primary);color:white;border:none;padding:11px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;font-family:'Inter',sans-serif;}}
.ai-answer{{margin-top:12px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);border-radius:8px;padding:12px;font-size:12px;line-height:1.8;display:none;}}
.ql{{display:flex;flex-direction:column;gap:7px;}}
.ql a{{display:flex;align-items:center;gap:8px;padding:10px;border-radius:8px;background:var(--light);border:1px solid var(--border);text-decoration:none;color:var(--dark);font-size:12px;font-weight:500;}}
.ql a:hover{{background:#eef2ff;color:var(--primary);}}
.back-link{{display:inline-flex;align-items:center;gap:5px;color:var(--gray);text-decoration:none;font-size:13px;padding:7px 14px;border-radius:7px;border:1px solid var(--border);background:white;margin:0 0 20px 0;}}
@media(max-width:900px){{.layout{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>
{NAV}
<div style="max-width:1100px;margin:20px auto;padding:0 20px">
  <a href="/" class="back-link">← All Scholarships</a>
</div>
<div class="layout">
  <div class="main-col">
    <div class="hero-card">
      <div class="uni-badge">🎓 {s['university_name'] or 'Scholarship'}</div>
      <h1>{title}</h1>
      <div class="qbadges">
        <span class="qb">🌍 {s['country'] or 'International'}</span>
        {'<span class="qb">🎓 ' + (s['degree_level'] or '') + '</span>' if s['degree_level'] else ''}
        {'<span class="qb">📝 IELTS ' + (s['ielts_score'] or '') + '</span>' if s['ielts_score'] and s['ielts_score'] not in ['Not required','Not mentioned'] else '<span class="qb">✅ No IELTS</span>'}
        {'<span class="qb">📅 ' + (s['deadline'] or '') + '</span>' if s['deadline'] else ''}
      </div>
    </div>
    <div class="blog-card">{blog_html}</div>
  </div>
  <div class="side-col">
    <a href="{s['scholarship_link']}" target="_blank" class="apply-btn">🚀 Apply Now – Official Site</a>
    <div class="sidebar-card">
      <h3>📋 Quick Info</h3>
      <div class="info-row"><span class="info-label">Country</span><span class="info-value">{s['country'] or 'International'}</span></div>
      <div class="info-row"><span class="info-label">Deadline</span><span class="info-value" style="color:#dc2626">{s['deadline'] or 'See website'}</span></div>
      <div class="info-row"><span class="info-label">Level</span><span class="info-value">{s['degree_level'] or 'All levels'}</span></div>
      <div class="info-row"><span class="info-label">Funding</span><span class="info-value">{s['funding_type'] or 'Check website'}</span></div>
      <div class="info-row"><span class="info-label">IELTS</span><span class="info-value">{s['ielts_score'] or 'Not required'}</span></div>
      <div class="info-row"><span class="info-label">GPA</span><span class="info-value">{s['gpa_required'] or 'Check website'}</span></div>
    </div>
    <div class="ai-card">
      <h3>🤖 Ask AI About This</h3>
      <p>Instant answers on eligibility, IELTS, SOP, documents and more.</p>
      <input class="ai-inp" type="text" id="q" placeholder="e.g. Can Pakistani students apply?">
      <button class="ai-btn" onclick="askAI()">Ask →</button>
      <div class="ai-answer" id="ans"></div>
    </div>
    <div class="sidebar-card">
      <h3>🔗 Explore More</h3>
      <div class="ql">
        <a href="/search?q={s['country'] or 'international'}">🌍 More from {s['country'] or 'International'}</a>
        <a href="/search?q=fully funded">💰 Fully Funded</a>
        <a href="/search?q=no ielts">📝 No IELTS Required</a>
        <a href="/search?q={s['degree_level'] or 'scholarship'}">🎓 Similar Level</a>
      </div>
    </div>
  </div>
</div>
<script>
function askAI(){{
  const q=document.getElementById('q').value.trim();
  const ans=document.getElementById('ans');
  if(!q)return;
  ans.style.display='block';
  ans.innerHTML='⏳ Thinking...';
  fetch('/ask',{{method:'POST',headers:{{'Content-Type':'application/json'}},
    body:JSON.stringify({{question:q,scholarship_id:{sid}}})
  }}).then(r=>r.json()).then(d=>{{ans.innerHTML=d.answer;}});
}}
document.getElementById('q').addEventListener('keypress',e=>{{if(e.key==='Enter')askAI();}});
</script>
</body></html>"""
    return html

@app.route('/search')
def search():
    q = request.args.get('q','').strip()
    conn = get_db()
    c = cur(conn)
    c.execute("""SELECT sd.*,s.source FROM scholarship_details sd
       LEFT JOIN scholarships s ON sd.scholarship_link=s.link
       WHERE sd.title ILIKE %s OR sd.seo_description ILIKE %s
       OR sd.eligible_countries ILIKE %s OR sd.degree_level ILIKE %s
       OR sd.country ILIKE %s OR sd.region ILIKE %s
       OR sd.funding_type ILIKE %s OR sd.university_name ILIKE %s
       ORDER BY sd.id DESC LIMIT 60""",
       tuple([f'%{q}%']*8))
    results = c.fetchall()
    c.close()
    conn.close()

    cards_html = ""
    for s in results:
        cards_html += f"""<div class="card">
          <div style="display:flex;justify-content:space-between;margin-bottom:10px">
            <span style="font-size:11px;font-weight:600;color:var(--primary);background:#eef2ff;padding:3px 10px;border-radius:100px;">🌍 {s['country'] or 'International'}</span>
          </div>
          <h3 style="font-size:14px;font-weight:700;margin-bottom:8px;line-height:1.5">{s['title'] or 'Scholarship'}</h3>
          <p style="font-size:12px;color:var(--gray);line-height:1.7;margin-bottom:14px">{s['seo_description'] or 'Click to view full details.'}</p>
          <a href="/scholarship/{s['id']}" style="display:block;text-align:center;background:var(--primary);color:white;padding:10px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:600">View Guide →</a>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>"{q}" Scholarships – ScholarPath</title>
<meta name="description" content="Find {q} scholarships worldwide. Free eligibility check and application guidance.">
{BASE_CSS}
<style>
.search-hero{{background:var(--primary);color:white;padding:36px 20px;text-align:center;}}
.search-hero h1{{font-size:24px;font-weight:800;margin-bottom:16px;}}
.sh-box{{display:flex;background:white;border-radius:12px;padding:5px;max-width:500px;margin:0 auto;box-shadow:0 10px 30px rgba(0,0,0,0.2);}}
.sh-box input{{flex:1;border:none;outline:none;padding:11px 16px;font-size:14px;font-family:'Inter',sans-serif;color:var(--dark);}}
.sh-box button{{background:var(--primary);color:white;border:none;padding:11px 20px;border-radius:9px;cursor:pointer;font-size:14px;font-weight:600;}}
.main{{max-width:1280px;margin:28px auto;padding:0 20px;}}
.rh{{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;}}
.rh h2{{font-size:18px;font-weight:700;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;}}
.card{{background:white;border-radius:12px;padding:20px;box-shadow:var(--shadow);border:1px solid var(--border);transition:all 0.2s;}}
.card:hover{{transform:translateY(-3px);box-shadow:var(--shadow-lg);}}
.empty{{text-align:center;padding:70px 20px;color:var(--gray);}}
</style>
</head>
<body>
{NAV}
<div class="search-hero">
  <h1>Results for "{q}"</h1>
  <form method="GET" action="/search">
  <div class="sh-box">
    <input type="text" name="q" value="{q}" placeholder="Search scholarships...">
    <button type="submit">Search</button>
  </div>
  </form>
</div>
<div class="main">
  <div class="rh"><h2>{len(results)} scholarships found</h2><p><a href="/" style="color:var(--primary);text-decoration:none">← Back to all</a></p></div>
  {'<div class="grid">' + cards_html + '</div>' if results else '<div class="empty"><div style="font-size:52px">🔍</div><h3>No results for "' + q + '"</h3><p>Try a country name or degree level.</p><a href="/" style="color:var(--primary);font-weight:600;text-decoration:none">← Browse all</a></div>'}
</div></body></html>"""
    return html

@app.route('/about')
def about():
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>About ScholarPath</title>{BASE_CSS}
<style>.page{{max-width:800px;margin:40px auto;padding:0 20px;}}.card{{background:white;border-radius:14px;padding:40px;box-shadow:var(--shadow);}}.card h1{{font-size:28px;font-weight:800;margin-bottom:20px;color:var(--primary);}}.card h2{{font-size:18px;font-weight:700;margin:24px 0 10px;}}.card p{{font-size:15px;line-height:1.85;color:#374151;margin-bottom:14px;}}</style>
</head><body>{NAV}<div class="page"><div class="card">
<h1>About ScholarPath</h1>
<p>ScholarPath is a free AI-powered scholarship platform built for students in Pakistan, India, Bangladesh, Africa and beyond.</p>
<h2>Our Mission</h2>
<p>Every year thousands of talented students miss life-changing scholarships simply because they do not know where to look. Consultants charge PKR 50,000–100,000 for guidance that should be free. We are changing that.</p>
<h2>What We Do</h2>
<p>We automatically collect fresh scholarships daily from universities and government programs worldwide, check every single one for freshness, remove outdated ones automatically, and use AI to guide each student through the entire application process — completely free.</p>
<h2>Why We Are Different</h2>
<p>We find hidden scholarships from Saudi Arabia, China, Korea, Hungary, Turkey and dozens of other countries that most Pakistani and Indian students never hear about. Our AI guides you on IELTS requirements, SOP writing, document checklists and more.</p>
</div></div></body></html>"""

@app.route('/privacy')
def privacy():
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Privacy Policy – ScholarPath</title>{BASE_CSS}
<style>.page{{max-width:800px;margin:40px auto;padding:0 20px;}}.card{{background:white;border-radius:14px;padding:40px;box-shadow:var(--shadow);}}.card h1{{font-size:28px;font-weight:800;margin-bottom:20px;color:var(--primary);}}.card h2{{font-size:18px;font-weight:700;margin:24px 0 10px;}}.card p{{font-size:15px;line-height:1.85;color:#374151;margin-bottom:14px;}}</style>
</head><body>{NAV}<div class="page"><div class="card">
<h1>Privacy Policy</h1>
<p>Last updated: {datetime.now().strftime('%B %Y')}</p>
<h2>Information We Collect</h2>
<p>We collect search queries and profile data when using our scholarship matching service.</p>
<h2>How We Use Information</h2>
<p>We use information to match you with scholarships and improve our service. We never sell your data.</p>
<h2>Google AdSense</h2>
<p>We use Google AdSense to display advertisements. Google may use cookies to serve relevant ads.</p>
<h2>Contact</h2>
<p>Email: contact@scholarpath.com</p>
</div></div></body></html>"""

@app.route('/contact')
def contact():
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Contact ScholarPath</title>{BASE_CSS}
<style>.page{{max-width:800px;margin:40px auto;padding:0 20px;}}.card{{background:white;border-radius:14px;padding:40px;box-shadow:var(--shadow);}}.card h1{{font-size:28px;font-weight:800;margin-bottom:20px;color:var(--primary);}}.card p{{font-size:15px;line-height:1.85;color:#374151;margin-bottom:14px;}}.info{{background:#f0f4ff;border-radius:10px;padding:20px;margin:16px 0;}}</style>
</head><body>{NAV}<div class="page"><div class="card">
<h1>Contact Us</h1>
<p>Have a question, partnership inquiry or feedback?</p>
<div class="info"><strong>General:</strong> contact@scholarpath.com</div>
<div class="info"><strong>Partnerships:</strong> partner@scholarpath.com</div>
<div class="info"><strong>Response time:</strong> Within 24 hours</div>
</div></div></body></html>"""

@app.route('/ask', methods=['POST'])
def ask_ai():
    data = request.get_json()
    question = data.get('question','').lower()
    sid = data.get('scholarship_id')
    conn = get_db()
    c = cur(conn)
    c.execute("SELECT * FROM scholarship_details WHERE id=%s", (sid,))
    s = c.fetchone()
    c.close()
    conn.close()
    if not s:
        return jsonify({"answer":"Sorry, could not find this scholarship."})

    if any(w in question for w in ['ielts','pte','toefl','english','language','test']):
        answer = f"🎯 <strong>Language Requirement:</strong> {s['language_requirement'] or 'Check website'}<br><br>📝 <strong>IELTS Score:</strong> {s['ielts_score'] or 'Not required'}<br><br>💡 Start IELTS prep 3 months early. British Council and IDP offer tests in Karachi, Lahore and Islamabad."
    elif any(w in question for w in ['deadline','last date','when','closing']):
        answer = f"📅 <strong>Deadline:</strong> {s['deadline'] or 'See official website'}<br><br>⚠️ Always verify on the official website. Apply at least 2 weeks before deadline."
    elif any(w in question for w in ['pakistan','indian','bangladesh','eligible','who can','nationality']):
        answer = f"🌍 <strong>Eligibility:</strong><br>{s['eligible_countries'][:400] if s['eligible_countries'] else 'Check official website'}<br><br>✅ Pakistani, Indian and Bangladeshi students are generally welcomed for international scholarships."
    elif any(w in question for w in ['benefit','cover','fund','money','stipend']):
        answer = f"💰 <strong>Benefits:</strong><br>{s['benefits'][:400] if s['benefits'] else 'Visit official website for funding details.'}"
    elif any(w in question for w in ['sop','statement','essay','personal']):
        answer = "✍️ <strong>SOP Structure:</strong><br><br><strong>Para 1:</strong> Powerful personal story<br><strong>Para 2:</strong> Academic background and GPA<br><strong>Para 3:</strong> Why this scholarship specifically<br><strong>Para 4:</strong> Your 5-year career goals<br><strong>Para 5:</strong> Why you deserve it<br><strong>Para 6:</strong> Strong closing<br><br>📏 Keep it 600–1000 words"
    elif any(w in question for w in ['document','require','need','checklist']):
        answer = "📋 <strong>Documents Required:</strong><br><br>✅ Valid Passport<br>✅ Academic Transcripts<br>✅ IELTS Certificate (if required)<br>✅ Statement of Purpose<br>✅ 2–3 Recommendation Letters<br>✅ Updated CV<br>✅ Passport Photos<br><br>💡 Prepare everything 1 month before deadline."
    else:
        answer = f"ℹ️ <strong>{s['title']}</strong><br><br>{s['full_description'][:300] if s['full_description'] else 'Visit official website.'}<br><br>💬 Ask me about: <em>eligibility, IELTS, deadline, documents, SOP, funding</em>"

    return jsonify({"answer": answer})

@app.route('/sitemap.xml')
def sitemap():
    conn = get_db()
    c = cur(conn)
    c.execute("SELECT id, last_updated FROM scholarship_details")
    rows = c.fetchall()
    c.close()
    conn.close()
    base = "https://scholarpath.onrender.com"
    urls = [f'<url><loc>{base}/scholarship/{r["id"]}</loc><lastmod>{r["last_updated"] or datetime.now().strftime("%Y-%m-%d")}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>' for r in rows]
    for page in ['','about','privacy','contact','search?q=fully+funded','search?q=no+ielts','search?q=phd','search?q=germany','search?q=china','search?q=turkey','search?q=korea']:
        urls.insert(0, f'<url><loc>{base}/{page}</loc><changefreq>daily</changefreq><priority>0.8</priority></url>')
    return Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(urls) + '</urlset>', mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    return Response("User-agent: *\nAllow: /\nDisallow: /ask\nSitemap: https://scholarpath.onrender.com/sitemap.xml", mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"\nScholarPath running on http://127.0.0.1:{port}\n")
    app.run(debug=False, host="0.0.0.0", port=port)