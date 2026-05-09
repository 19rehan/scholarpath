from flask import Flask, render_template_string, request, jsonify
import sqlite3
import re
import os

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('scholarships.db')
    conn.row_factory = sqlite3.Row
    return conn

def convert_to_html(text):
    if not text:
        return ""
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
    text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n?)+', lambda m: f'<ul>{m.group()}</ul>', text, flags=re.DOTALL)
    text = re.sub(r'^---$', '<hr>', text, flags=re.MULTILINE)
    text = re.sub(r'\n\n+', '</p><p>', text)
    return f'<p>{text}</p>'

# ══════════════════════════════════════════════════════════
#  BEAUTIFUL HOME PAGE
# ══════════════════════════════════════════════════════════
HOME = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ScholarPath – Free AI Scholarship Finder for Pakistani & International Students</title>
<meta name="description" content="Find fresh scholarships from universities worldwide. Free AI guidance on eligibility, IELTS, SOP writing and how to apply. No agent needed.">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {
  --primary: #4f46e5;
  --primary-dark: #3730a3;
  --primary-light: #818cf8;
  --secondary: #06b6d4;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --dark: #0f172a;
  --gray: #64748b;
  --light: #f8fafc;
  --border: #e2e8f0;
  --card-shadow: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04);
  --card-shadow-hover: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:#f1f5f9; color:var(--dark); }

/* NAV */
nav {
  background:white;
  border-bottom:1px solid var(--border);
  padding:0 40px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  height:64px;
  position:sticky;
  top:0;
  z-index:100;
  box-shadow:0 1px 3px rgba(0,0,0,0.08);
}
.logo { display:flex; align-items:center; gap:10px; text-decoration:none; }
.logo-icon { width:36px; height:36px; background:var(--primary); border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-size:18px; }
.logo-text { font-size:20px; font-weight:800; color:var(--dark); }
.logo-text span { color:var(--primary); }
.nav-links { display:flex; gap:8px; align-items:center; }
.nav-links a { padding:8px 16px; border-radius:8px; text-decoration:none; font-size:14px; font-weight:500; color:var(--gray); transition:all 0.2s; }
.nav-links a:hover { background:var(--light); color:var(--primary); }
.nav-cta { background:var(--primary) !important; color:white !important; }
.nav-cta:hover { background:var(--primary-dark) !important; color:white !important; }

/* HERO */
.hero {
  background:linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 70%, #0891b2 100%);
  color:white;
  padding:90px 20px 80px;
  text-align:center;
  position:relative;
  overflow:hidden;
}
.hero::before {
  content:'';
  position:absolute;
  top:-50%;
  left:-50%;
  width:200%;
  height:200%;
  background:radial-gradient(circle at 30% 50%, rgba(99,102,241,0.3) 0%, transparent 50%),
              radial-gradient(circle at 70% 30%, rgba(6,182,212,0.2) 0%, transparent 50%);
  animation:float 8s ease-in-out infinite;
}
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-20px)} }
.hero-content { position:relative; z-index:1; }
.hero-badge {
  display:inline-flex; align-items:center; gap:8px;
  background:rgba(255,255,255,0.15); backdrop-filter:blur(10px);
  border:1px solid rgba(255,255,255,0.2);
  padding:8px 20px; border-radius:100px;
  font-size:13px; font-weight:500; margin-bottom:28px;
  color:rgba(255,255,255,0.9);
}
.hero h1 { font-size:clamp(32px,5vw,58px); font-weight:800; line-height:1.15; margin-bottom:20px; letter-spacing:-1px; }
.hero h1 span { color:#67e8f9; }
.hero p { font-size:18px; opacity:0.85; max-width:580px; margin:0 auto 40px; line-height:1.7; }
.search-wrap { max-width:600px; margin:0 auto; }
.search-box {
  display:flex; background:white; border-radius:16px;
  padding:6px; box-shadow:0 25px 50px rgba(0,0,0,0.25);
}
.search-box input {
  flex:1; border:none; outline:none; padding:14px 20px;
  font-size:15px; color:var(--dark); background:transparent;
  font-family:'Inter',sans-serif;
}
.search-box button {
  background:var(--primary); color:white; border:none;
  padding:14px 28px; border-radius:12px; cursor:pointer;
  font-size:15px; font-weight:600; transition:all 0.2s;
  white-space:nowrap;
}
.search-box button:hover { background:var(--primary-dark); transform:scale(1.02); }
.search-tags { display:flex; gap:10px; flex-wrap:wrap; justify-content:center; margin-top:20px; }
.search-tag {
  background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.25);
  color:white; padding:6px 16px; border-radius:100px; font-size:13px;
  cursor:pointer; transition:all 0.2s; text-decoration:none;
}
.search-tag:hover { background:rgba(255,255,255,0.25); }

/* STATS */
.stats {
  display:flex; justify-content:center; gap:0;
  background:white; border-bottom:1px solid var(--border);
}
.stat {
  text-align:center; padding:28px 48px;
  border-right:1px solid var(--border);
}
.stat:last-child { border-right:none; }
.stat-num { font-size:32px; font-weight:800; color:var(--primary); line-height:1; }
.stat-label { font-size:13px; color:var(--gray); margin-top:4px; font-weight:500; }

/* FILTERS BAR */
.filter-bar {
  background:white; border-bottom:1px solid var(--border);
  padding:16px 40px; display:flex; gap:12px; align-items:center;
  flex-wrap:wrap;
}
.filter-label { font-size:13px; font-weight:600; color:var(--gray); margin-right:4px; }
.filter-btn {
  padding:8px 18px; border-radius:100px; font-size:13px; font-weight:500;
  cursor:pointer; border:1.5px solid var(--border); background:white;
  color:var(--gray); transition:all 0.2s; text-decoration:none;
  display:inline-block;
}
.filter-btn:hover, .filter-btn.active {
  background:var(--primary); color:white; border-color:var(--primary);
}
.filter-select {
  padding:8px 14px; border:1.5px solid var(--border); border-radius:100px;
  font-size:13px; font-family:'Inter',sans-serif; color:var(--dark);
  background:white; cursor:pointer; outline:none;
}
.filter-select:focus { border-color:var(--primary); }

/* MAIN LAYOUT */
.main { max-width:1280px; margin:0 auto; padding:32px 24px; }
.section-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; }
.section-title { font-size:22px; font-weight:700; color:var(--dark); }
.section-count { font-size:14px; color:var(--gray); }

/* SCHOLARSHIP GRID */
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:20px; }

/* CARD */
.card {
  background:white; border-radius:16px; padding:24px;
  box-shadow:var(--card-shadow); transition:all 0.25s;
  border:1px solid var(--border); display:flex; flex-direction:column;
  position:relative; overflow:hidden;
}
.card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:3px;
  background:linear-gradient(90deg,var(--primary),var(--secondary));
}
.card:hover { transform:translateY(-6px); box-shadow:var(--card-shadow-hover); }

.card-top { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:14px; }
.card-source {
  font-size:11px; font-weight:600; color:var(--primary);
  background:#eef2ff; padding:4px 10px; border-radius:100px;
  text-transform:uppercase; letter-spacing:0.5px;
}
.card-region {
  font-size:11px; color:var(--gray); font-weight:500;
}
.card h3 {
  font-size:15px; font-weight:700; color:var(--dark);
  line-height:1.5; margin-bottom:12px; flex:1;
}
.badges { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:14px; }
.badge {
  display:inline-flex; align-items:center; gap:4px;
  padding:4px 12px; border-radius:100px; font-size:12px; font-weight:500;
}
.badge-blue { background:#eff6ff; color:#1d4ed8; }
.badge-green { background:#f0fdf4; color:#15803d; }
.badge-orange { background:#fff7ed; color:#c2410c; }
.badge-purple { background:#faf5ff; color:#7e22ce; }
.badge-red { background:#fef2f2; color:#dc2626; }
.badge-gray { background:#f8fafc; color:#475569; }

.card-desc {
  font-size:13px; color:var(--gray); line-height:1.7;
  margin-bottom:16px; flex:1;
  display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;
}
.card-footer { margin-top:auto; }
.deadline-row {
  display:flex; align-items:center; gap:6px;
  font-size:12px; font-weight:600; color:#dc2626;
  margin-bottom:14px; padding:8px 12px;
  background:#fef2f2; border-radius:8px;
}
.card-btn {
  display:block; text-align:center;
  background:linear-gradient(135deg,var(--primary),var(--primary-dark));
  color:white; padding:12px; border-radius:10px;
  text-decoration:none; font-size:14px; font-weight:600;
  transition:all 0.2s; letter-spacing:0.3px;
}
.card-btn:hover { opacity:0.9; transform:scale(1.01); }

/* REGIONS SECTION */
.regions { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:32px; }
.region-chip {
  padding:12px 24px; border-radius:12px; font-size:14px; font-weight:600;
  cursor:pointer; text-decoration:none; transition:all 0.2s;
  border:2px solid transparent; display:flex; align-items:center; gap:8px;
}
.region-eu { background:#eef2ff; color:#4338ca; }
.region-eu:hover { border-color:#4338ca; }
.region-asia { background:#fef3c7; color:#92400e; }
.region-asia:hover { border-color:#92400e; }
.region-me { background:#fce7f3; color:#9d174d; }
.region-me:hover { border-color:#9d174d; }
.region-aus { background:#d1fae5; color:#065f46; }
.region-aus:hover { border-color:#065f46; }
.region-na { background:#dbeafe; color:#1e40af; }
.region-na:hover { border-color:#1e40af; }
.region-af { background:#fef9c3; color:#713f12; }
.region-af:hover { border-color:#713f12; }

/* EMPTY STATE */
.empty { text-align:center; padding:60px 20px; color:var(--gray); }
.empty-icon { font-size:48px; margin-bottom:16px; }
.empty h3 { font-size:20px; font-weight:700; margin-bottom:8px; color:var(--dark); }

/* FOOTER */
footer {
  background:var(--dark); color:rgba(255,255,255,0.7);
  text-align:center; padding:40px 20px; margin-top:60px;
  font-size:14px; line-height:2;
}
footer a { color:var(--primary-light); text-decoration:none; }

@media(max-width:768px){
  nav { padding:0 16px; }
  .stats { flex-wrap:wrap; }
  .stat { padding:20px 24px; }
  .filter-bar { padding:12px 16px; }
  .main { padding:20px 16px; }
  .grid { grid-template-columns:1fr; }
  .regions { gap:8px; }
}
</style>
</head>
<body>

<nav>
  <a href="/" class="logo">
    <div class="logo-icon">🎓</div>
    <div class="logo-text">Scholar<span>Path</span></div>
  </a>
  <div class="nav-links">
    <a href="/">Home</a>
    <a href="/search?q=fully+funded">Fully Funded</a>
    <a href="/search?q=phd">PhD</a>
    <a href="/about.html">About</a>
    <a href="/contact.html" class="nav-cta">Get Help</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-content">
    <div class="hero-badge">🚀 Fresh scholarships updated daily</div>
    <h1>Find Your <span>Dream Scholarship</span><br>Worldwide — For Free</h1>
    <p>No agent needed. No fees. Our AI finds the best scholarships from universities across Europe, Asia, Middle East & beyond — matched to your profile.</p>
    <div class="search-wrap">
      <form method="GET" action="/search">
        <div class="search-box">
          <input type="text" name="q" placeholder="Search by country, field, university..." autocomplete="off">
          <button type="submit">🔍 Search</button>
        </div>
      </form>
      <div class="search-tags">
        <a href="/search?q=germany" class="search-tag">🇩🇪 Germany</a>
        <a href="/search?q=china" class="search-tag">🇨🇳 China</a>
        <a href="/search?q=turkey" class="search-tag">🇹🇷 Turkey</a>
        <a href="/search?q=korea" class="search-tag">🇰🇷 Korea</a>
        <a href="/search?q=fully funded" class="search-tag">💰 Fully Funded</a>
        <a href="/search?q=phd" class="search-tag">🎓 PhD</a>
      </div>
    </div>
  </div>
</div>

<div class="stats">
  <div class="stat">
    <div class="stat-num">{{ total }}+</div>
    <div class="stat-label">Live Scholarships</div>
  </div>
  <div class="stat">
    <div class="stat-num">50+</div>
    <div class="stat-label">Countries</div>
  </div>
  <div class="stat">
    <div class="stat-num">Free</div>
    <div class="stat-label">No Agent Fee</div>
  </div>
  <div class="stat">
    <div class="stat-num">AI</div>
    <div class="stat-label">Guided Applications</div>
  </div>
</div>

<div class="filter-bar">
  <span class="filter-label">Filter:</span>
  <a href="/" class="filter-btn {% if not request.args.get('level') %}active{% endif %}">All</a>
  <a href="/?level=Bachelor" class="filter-btn {% if request.args.get('level')=='Bachelor' %}active{% endif %}">Bachelor</a>
  <a href="/?level=Master" class="filter-btn {% if request.args.get('level')=='Master' %}active{% endif %}">Master's</a>
  <a href="/?level=PhD" class="filter-btn {% if request.args.get('level')=='PhD' %}active{% endif %}">PhD</a>
  <a href="/search?q=fully funded" class="filter-btn">Fully Funded</a>
  <a href="/search?q=no ielts" class="filter-btn">No IELTS</a>
</div>

<div class="main">
  <!-- REGION CHIPS -->
  <div class="regions">
    <a href="/search?q=europe" class="region-chip region-eu">🌍 Europe</a>
    <a href="/search?q=asia" class="region-chip region-asia">🌏 Asia</a>
    <a href="/search?q=middle east" class="region-chip region-me">🕌 Middle East</a>
    <a href="/search?q=australia" class="region-chip region-aus">🦘 Australia</a>
    <a href="/search?q=canada" class="region-chip region-na">🍁 Canada</a>
    <a href="/search?q=africa" class="region-chip region-af">🌍 Africa</a>
  </div>

  <div class="section-header">
    <div class="section-title">Latest Scholarships</div>
    <div class="section-count">{{ total }} opportunities found</div>
  </div>

  {% if scholarships %}
  <div class="grid">
    {% for s in scholarships %}
    <div class="card">
      <div class="card-top">
        <span class="card-source">{{ (s['source'] or 'University')|replace('uni_','') }}</span>
        <span class="card-region">{{ s['country'] or 'International' }}</span>
      </div>
      <h3>{{ s['seo_title'] or s['title'] }}</h3>
      <div class="badges">
        {% if s['degree_level'] and s['degree_level'] != 'Not specified' %}
        <span class="badge badge-blue">🎓 {{ s['degree_level'][:25] }}</span>
        {% endif %}
        {% if s['ielts_score'] and s['ielts_score'] not in ['Not required','Not mentioned'] %}
        <span class="badge badge-orange">IELTS {{ s['ielts_score'] }}</span>
        {% endif %}
        {% if 'full' in (s['benefits'] or '').lower() or 'full' in (s['title'] or '').lower() %}
        <span class="badge badge-green">💰 Fully Funded</span>
        {% else %}
        <span class="badge badge-gray">Funding Available</span>
        {% endif %}
      </div>
      <p class="card-desc">{{ s['seo_description'] or s['full_description'] or 'International scholarship opportunity. Click to view full details, requirements and how to apply.' }}</p>
      <div class="card-footer">
        {% if s['deadline'] and s['deadline'] not in ['See link','See official website'] %}
        <div class="deadline-row">📅 Deadline: {{ s['deadline'] }}</div>
        {% endif %}
        <a href="/scholarship/{{ s['id'] }}" class="card-btn">View Full Guide & Apply →</a>
      </div>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <div class="empty">
    <div class="empty-icon">🔍</div>
    <h3>No scholarships yet</h3>
    <p>Run the scraper to populate scholarships.</p>
  </div>
  {% endif %}
</div>

<footer>
  <div>🎓 <strong style="color:white">ScholarPath</strong> — Free AI Scholarship Finder</div>
  <div>Built for students in Pakistan, India, Bangladesh, Africa & beyond</div>
  <div style="margin-top:12px">
    <a href="/about.html">About</a> &nbsp;·&nbsp;
    <a href="/privacy.html">Privacy Policy</a> &nbsp;·&nbsp;
    <a href="/contact.html">Contact</a>
  </div>
  <div style="margin-top:12px;font-size:12px;opacity:0.5">© 2025 ScholarPath · Helping students find scholarships without agents</div>
</footer>

</body>
</html>'''

# ══════════════════════════════════════════════════════════
#  DETAIL PAGE
# ══════════════════════════════════════════════════════════
DETAIL = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{{ s['seo_title'] or s['title'] }} – ScholarPath</title>
<meta name="description" content="{{ s['seo_description'] or '' }}">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{--primary:#4f46e5;--primary-dark:#3730a3;--secondary:#06b6d4;--success:#10b981;--dark:#0f172a;--gray:#64748b;--light:#f8fafc;--border:#e2e8f0;}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Inter',sans-serif;background:#f1f5f9;color:var(--dark);}
nav{background:white;border-bottom:1px solid var(--border);padding:0 40px;display:flex;align-items:center;justify-content:space-between;height:64px;position:sticky;top:0;z-index:100;box-shadow:0 1px 3px rgba(0,0,0,0.08);}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;}
.logo-icon{width:36px;height:36px;background:var(--primary);border-radius:10px;display:flex;align-items:center;justify-content:center;color:white;font-size:18px;}
.logo-text{font-size:20px;font-weight:800;color:var(--dark);}
.logo-text span{color:var(--primary);}
.back-btn{display:inline-flex;align-items:center;gap:6px;color:var(--gray);text-decoration:none;font-size:14px;font-weight:500;padding:8px 16px;border-radius:8px;border:1px solid var(--border);background:white;transition:all 0.2s;}
.back-btn:hover{background:var(--light);color:var(--primary);}
.layout{max-width:1100px;margin:32px auto;padding:0 24px;display:grid;grid-template-columns:1fr 320px;gap:24px;}
.main-col{}
.side-col{}

/* HERO CARD */
.hero-card{background:linear-gradient(135deg,#1e1b4b,#3730a3);color:white;border-radius:20px;padding:36px;margin-bottom:24px;}
.hero-card .uni-badge{display:inline-block;background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.2);padding:6px 16px;border-radius:100px;font-size:12px;font-weight:600;margin-bottom:16px;letter-spacing:0.5px;}
.hero-card h1{font-size:26px;font-weight:800;line-height:1.3;margin-bottom:16px;}
.quick-badges{display:flex;flex-wrap:wrap;gap:8px;}
.qbadge{padding:6px 14px;border-radius:100px;font-size:12px;font-weight:600;background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.2);}

/* BLOG CONTENT */
.blog-card{background:white;border-radius:16px;padding:36px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.07);border:1px solid var(--border);}
.blog-card h1{font-size:28px;font-weight:800;color:var(--dark);margin-bottom:24px;line-height:1.3;}
.blog-card h2{font-size:19px;font-weight:700;color:var(--primary);margin:28px 0 12px;padding-left:14px;border-left:4px solid var(--primary);}
.blog-card h3{font-size:16px;font-weight:700;color:var(--dark);margin:20px 0 8px;}
.blog-card p{font-size:15px;line-height:1.85;color:#374151;margin-bottom:14px;}
.blog-card table{width:100%;border-collapse:collapse;margin:20px 0;border-radius:10px;overflow:hidden;border:1px solid var(--border);}
.blog-card thead th{background:#f0f4ff;padding:12px 16px;text-align:left;font-size:13px;font-weight:700;color:var(--primary);}
.blog-card tbody td{padding:12px 16px;font-size:14px;border-top:1px solid var(--border);}
.blog-card tbody tr:hover{background:#fafbff;}
.blog-card ul,.blog-card ol{padding-left:20px;margin:14px 0;}
.blog-card li{font-size:15px;line-height:2;color:#374151;}
.blog-card strong{color:var(--primary);font-weight:700;}
.blog-card hr{border:none;border-top:2px solid var(--border);margin:28px 0;}

/* SIDEBAR */
.sidebar-card{background:white;border-radius:16px;padding:24px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.07);border:1px solid var(--border);margin-bottom:20px;}
.sidebar-card h3{font-size:15px;font-weight:700;margin-bottom:16px;color:var(--dark);}
.info-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);font-size:13px;}
.info-row:last-child{border-bottom:none;}
.info-label{color:var(--gray);font-weight:500;}
.info-value{font-weight:600;color:var(--dark);text-align:right;max-width:160px;}
.apply-btn{display:block;background:linear-gradient(135deg,#059669,#10b981);color:white;text-align:center;padding:16px;border-radius:12px;text-decoration:none;font-size:16px;font-weight:700;margin-bottom:12px;transition:all 0.2s;letter-spacing:0.3px;}
.apply-btn:hover{opacity:0.9;transform:translateY(-2px);}
.save-btn{display:block;background:var(--light);color:var(--primary);text-align:center;padding:14px;border-radius:12px;text-decoration:none;font-size:14px;font-weight:600;border:2px solid var(--border);transition:all 0.2s;}
.save-btn:hover{border-color:var(--primary);}

/* AI BOX */
.ai-card{background:linear-gradient(135deg,#0f172a,#1e1b4b);border-radius:16px;padding:24px;color:white;margin-bottom:20px;}
.ai-card h3{font-size:16px;font-weight:700;margin-bottom:6px;}
.ai-card p{font-size:13px;opacity:0.7;margin-bottom:16px;line-height:1.6;}
.ai-input{width:100%;padding:12px 14px;border:none;border-radius:10px;font-size:14px;font-family:'Inter',sans-serif;background:rgba(255,255,255,0.1);color:white;outline:none;border:1px solid rgba(255,255,255,0.2);}
.ai-input::placeholder{color:rgba(255,255,255,0.4);}
.ai-input:focus{border-color:var(--primary-light);}
.ai-btn{width:100%;margin-top:10px;background:var(--primary);color:white;border:none;padding:12px;border-radius:10px;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s;font-family:'Inter',sans-serif;}
.ai-btn:hover{background:#4338ca;}
.ai-answer{margin-top:14px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-radius:10px;padding:14px;font-size:13px;line-height:1.8;display:none;}
.ai-thinking{display:flex;gap:6px;align-items:center;font-size:13px;opacity:0.7;}
.dot{width:6px;height:6px;border-radius:50%;background:var(--primary-light);animation:bounce 1.2s infinite;}
.dot:nth-child(2){animation-delay:0.2s;}
.dot:nth-child(3){animation-delay:0.4s;}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}

/* QUICK LINKS */
.quick-links{display:flex;flex-direction:column;gap:8px;}
.quick-link{display:flex;align-items:center;gap:10px;padding:12px;border-radius:10px;background:var(--light);border:1px solid var(--border);text-decoration:none;color:var(--dark);font-size:13px;font-weight:500;transition:all 0.2s;}
.quick-link:hover{background:#eef2ff;border-color:var(--primary);color:var(--primary);}

@media(max-width:900px){
  .layout{grid-template-columns:1fr;}
  .side-col{order:-1;}
}
</style>
</head>
<body>
<nav>
  <a href="/" class="logo">
    <div class="logo-icon">🎓</div>
    <div class="logo-text">Scholar<span>Path</span></div>
  </a>
  <a href="/" class="back-btn">← All Scholarships</a>
</nav>

<div style="max-width:1100px;margin:24px auto;padding:0 24px">
  <a href="/" class="back-btn" style="margin-bottom:20px;display:inline-flex">← Back to scholarships</a>
</div>

<div class="layout">
  <!-- MAIN COLUMN -->
  <div class="main-col">
    <div class="hero-card">
      <div class="uni-badge">🎓 {{ s['source']|replace('uni_','')|upper if s['source'] else 'SCHOLARSHIP' }}</div>
      <h1>{{ s['seo_title'] or s['title'] }}</h1>
      <div class="quick-badges">
        {% if s['degree_level'] and s['degree_level'] != 'Not specified' %}
        <span class="qbadge">🎓 {{ s['degree_level'] }}</span>
        {% endif %}
        {% if s['ielts_score'] and s['ielts_score'] != 'Not mentioned' %}
        <span class="qbadge">📝 IELTS {{ s['ielts_score'] }}</span>
        {% endif %}
        {% if s['deadline'] %}
        <span class="qbadge">📅 {{ s['deadline'] }}</span>
        {% endif %}
      </div>
    </div>
    <div class="blog-card">
      {{ blog_html|safe }}
    </div>
  </div>

  <!-- SIDEBAR -->
  <div class="side-col">
    <a href="{{ s['scholarship_link'] }}" target="_blank" class="apply-btn">🚀 Apply Now – Official Site</a>
    <a href="#" class="save-btn" onclick="alert('Login feature coming soon!')">🔖 Save Scholarship</a>

    <div class="sidebar-card">
      <h3>📋 Quick Info</h3>
      <div class="info-row">
        <span class="info-label">Deadline</span>
        <span class="info-value" style="color:#dc2626">{{ s['deadline'] or 'See website' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Level</span>
        <span class="info-value">{{ s['degree_level'] or 'All levels' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">IELTS</span>
        <span class="info-value">{{ s['ielts_score'] or 'Check website' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Language</span>
        <span class="info-value">{{ s['language_requirement'] or 'See website' }}</span>
      </div>
    </div>

    <div class="ai-card">
      <h3>🤖 Ask AI Assistant</h3>
      <p>Get instant answers about eligibility, IELTS, SOP and more.</p>
      <input class="ai-input" type="text" id="q" placeholder="e.g. Can Pakistani students apply?">
      <button class="ai-btn" onclick="askAI()">Ask AI →</button>
      <div class="ai-answer" id="answer"></div>
    </div>

    <div class="sidebar-card">
      <h3>🔗 Quick Links</h3>
      <div class="quick-links">
        <a href="{{ s['scholarship_link'] }}" target="_blank" class="quick-link">🌐 Official Website</a>
        <a href="/search?q={{ s['degree_level'] or 'scholarship' }}" class="quick-link">🔍 Similar Scholarships</a>
        <a href="/search?q=fully funded" class="quick-link">💰 Fully Funded Options</a>
        <a href="/search?q=no ielts" class="quick-link">📝 No IELTS Required</a>
      </div>
    </div>
  </div>
</div>

<script>
function askAI() {
  const q = document.getElementById('q').value.trim();
  const ans = document.getElementById('answer');
  if (!q) return;
  ans.style.display = 'block';
  ans.innerHTML = '<div class="ai-thinking"><div class="dot"></div><div class="dot"></div><div class="dot"></div> Thinking...</div>';
  fetch('/ask', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({question:q, scholarship_id:{{ s['id'] }}})
  })
  .then(r=>r.json())
  .then(d=>{ ans.innerHTML = d.answer; });
}
document.getElementById('q').addEventListener('keypress',e=>{ if(e.key==='Enter') askAI(); });
</script>
</body>
</html>'''

# ══════════════════════════════════════════════════════════
#  SEARCH PAGE
# ══════════════════════════════════════════════════════════
SEARCH_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Search "{{ query }}" – ScholarPath</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{--primary:#4f46e5;--dark:#0f172a;--gray:#64748b;--light:#f8fafc;--border:#e2e8f0;}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Inter',sans-serif;background:#f1f5f9;color:var(--dark);}
nav{background:white;border-bottom:1px solid var(--border);padding:0 40px;display:flex;align-items:center;justify-content:space-between;height:64px;position:sticky;top:0;z-index:100;box-shadow:0 1px 3px rgba(0,0,0,0.08);}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;}
.logo-icon{width:36px;height:36px;background:var(--primary);border-radius:10px;display:flex;align-items:center;justify-content:center;color:white;font-size:18px;}
.logo-text{font-size:20px;font-weight:800;color:var(--dark);}
.logo-text span{color:var(--primary);}
.search-bar{display:flex;background:var(--light);border:1.5px solid var(--border);border-radius:10px;overflow:hidden;}
.search-bar input{border:none;background:transparent;padding:10px 16px;font-size:14px;font-family:'Inter',sans-serif;outline:none;width:240px;}
.search-bar button{background:var(--primary);color:white;border:none;padding:10px 20px;cursor:pointer;font-size:14px;font-weight:600;}
.main{max-width:1280px;margin:32px auto;padding:0 24px;}
.results-header{margin-bottom:24px;}
.results-header h2{font-size:22px;font-weight:700;}
.results-header p{color:var(--gray);font-size:14px;margin-top:4px;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px;}
.card{background:white;border-radius:16px;padding:24px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.07);border:1px solid var(--border);transition:all 0.25s;position:relative;overflow:hidden;}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--primary),#06b6d4);}
.card:hover{transform:translateY(-4px);box-shadow:0 20px 25px -5px rgba(0,0,0,0.1);}
.card h3{font-size:15px;font-weight:700;color:var(--dark);margin-bottom:10px;line-height:1.5;}
.card p{font-size:13px;color:var(--gray);line-height:1.7;margin-bottom:14px;}
.card a.btn{display:block;text-align:center;background:var(--primary);color:white;padding:11px;border-radius:10px;text-decoration:none;font-size:14px;font-weight:600;}
.empty{text-align:center;padding:80px 20px;color:var(--gray);}
.empty-icon{font-size:56px;margin-bottom:16px;}
.empty h3{font-size:22px;font-weight:700;color:var(--dark);margin-bottom:8px;}
</style>
</head>
<body>
<nav>
  <a href="/" class="logo">
    <div class="logo-icon">🎓</div>
    <div class="logo-text">Scholar<span>Path</span></div>
  </a>
  <form method="GET" action="/search">
  <div class="search-bar">
    <input type="text" name="q" value="{{ query }}" placeholder="Search scholarships...">
    <button type="submit">Search</button>
  </div>
  </form>
</nav>
<div class="main">
  <div class="results-header">
    <h2>Results for "{{ query }}"</h2>
    <p>{{ results|length }} scholarships found</p>
  </div>
  {% if results %}
  <div class="grid">
    {% for s in results %}
    <div class="card">
      <h3>{{ s['title'] }}</h3>
      <p>{{ s['seo_description'] or s['full_description'] or 'Click to view full details.' }}</p>
      <a href="/scholarship/{{ s['id'] }}" class="btn">View Full Guide →</a>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <div class="empty">
    <div class="empty-icon">🔍</div>
    <h3>No results found for "{{ query }}"</h3>
    <p>Try searching for a country, field of study, or scholarship type.</p>
    <a href="/" style="color:var(--primary);font-weight:600;text-decoration:none;">← Back to all scholarships</a>
  </div>
  {% endif %}
</div>
</body>
</html>'''

# ══════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════
@app.route('/')
def home():
    conn = get_db()
    level = request.args.get('level','')
    if level:
        rows = conn.execute(
            "SELECT sd.*, s.country, s.source FROM scholarship_details sd LEFT JOIN scholarships s ON sd.scholarship_link=s.link WHERE sd.degree_level LIKE ? ORDER BY sd.id DESC",
            (f'%{level}%',)).fetchall()
    else:
        rows = conn.execute(
            "SELECT sd.*, s.country, s.source FROM scholarship_details sd LEFT JOIN scholarships s ON sd.scholarship_link=s.link ORDER BY sd.id DESC"
        ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM scholarship_details").fetchone()[0]
    conn.close()
    return render_template_string(HOME, scholarships=rows, total=total, request=request)

@app.route('/scholarship/<int:sid>')
def scholarship(sid):
    conn = get_db()
    s = conn.execute("SELECT sd.*, s.country, s.source FROM scholarship_details sd LEFT JOIN scholarships s ON sd.scholarship_link=s.link WHERE sd.id=?", (sid,)).fetchone()
    conn.close()
    if not s:
        return "Scholarship not found", 404
    blog_html = convert_to_html(s['blog_post'] or "")
    return render_template_string(DETAIL, s=s, blog_html=blog_html)

@app.route('/search')
def search():
    query = request.args.get('q','')
    conn = get_db()
    results = conn.execute(
        """SELECT sd.*, s.country, s.source FROM scholarship_details sd
           LEFT JOIN scholarships s ON sd.scholarship_link=s.link
           WHERE sd.title LIKE ? OR sd.seo_description LIKE ?
           OR sd.eligible_countries LIKE ? OR sd.degree_level LIKE ?
           OR s.country LIKE ? OR s.source LIKE ?
           ORDER BY sd.id DESC""",
        tuple([f'%{query}%']*6)).fetchall()
    conn.close()
    return render_template_string(SEARCH_PAGE, query=query, results=results)

@app.route('/ask', methods=['POST'])
def ask_ai():
    data = request.get_json()
    question = data.get('question','').lower()
    sid = data.get('scholarship_id')
    conn = get_db()
    s = conn.execute("SELECT * FROM scholarship_details WHERE id=?", (sid,)).fetchone()
    conn.close()
    if not s:
        return jsonify({"answer":"Sorry, could not find this scholarship."})

    answer = ""
    if any(w in question for w in ['ielts','pte','toefl','english','language']):
        answer = f"🎯 <strong>Language Requirement:</strong> {s['language_requirement']}<br><br>📝 <strong>IELTS Score Required:</strong> {s['ielts_score']}<br><br>💡 <strong>Tip:</strong> Start IELTS preparation at least 3 months before the deadline. Many test centers in Pakistan offer preparation courses for PKR 15,000–25,000."

    elif any(w in question for w in ['deadline','last date','when','closing','date']):
        answer = f"📅 <strong>Application Deadline:</strong> {s['deadline']}<br><br>⚠️ Always verify the deadline on the official website as dates can change. We recommend applying 2 weeks before the deadline."

    elif any(w in question for w in ['pakistan','indian','bangladesh','african','eligible','who can','nationality','country']):
        answer = f"🌍 <strong>Eligibility:</strong><br>{s['eligible_countries'][:400]}<br><br>✅ Pakistani, Indian and Bangladeshi students are generally welcomed for international scholarships. Always verify nationality requirements on the official website."

    elif any(w in question for w in ['benefit','cover','fund','money','stipend','pay','include']):
        answer = f"💰 <strong>Scholarship Benefits:</strong><br>{s['benefits'][:400]}<br><br>Always check the official website for the most updated funding breakdown."

    elif any(w in question for w in ['sop','statement of purpose','essay','personal statement']):
        answer = """✍️ <strong>How to Write a Strong SOP:</strong><br><br>
        <strong>1. Opening (Hook):</strong> Start with a powerful story or achievement that defines you<br>
        <strong>2. Academic Background:</strong> Mention your degrees, GPA, and key achievements<br>
        <strong>3. Why This Scholarship:</strong> Be very specific — research the university<br>
        <strong>4. Career Goals:</strong> Show how this scholarship fits your 5-year plan<br>
        <strong>5. Why You Deserve It:</strong> Leadership, research, community work<br>
        <strong>6. Closing:</strong> Strong, confident ending<br><br>
        📏 <strong>Length:</strong> 600–1000 words unless stated otherwise<br>
        ✅ <strong>Key:</strong> Make it personal, specific and honest — committees read thousands."""

    elif any(w in question for w in ['document','require','need','submit','checklist']):
        answer = """📋 <strong>Documents Usually Required:</strong><br><br>
        ✅ Valid Passport (check expiry)<br>
        ✅ Academic Transcripts (all degrees)<br>
        ✅ IELTS / TOEFL Certificate<br>
        ✅ Statement of Purpose (SOP)<br>
        ✅ 2–3 Recommendation Letters<br>
        ✅ Updated CV / Resume<br>
        ✅ Passport-size Photos<br>
        ✅ Research Proposal (PhD only)<br>
        ✅ Proof of Admission (sometimes)<br><br>
        💡 Prepare all documents at least 1 month before the deadline."""

    elif any(w in question for w in ['gpa','grade','cgpa','marks','percentage']):
        answer = f"📊 <strong>GPA/Grade Requirement:</strong> {s['gpa_required'] if hasattr(s,'gpa_required') else 'Check official website'}<br><br>💡 Most international scholarships require a minimum 3.0/4.0 GPA or equivalent. A 2:1 UK degree classification is generally acceptable."

    elif any(w in question for w in ['degree','level','bachelor','master','phd']):
        answer = f"🎓 <strong>Available for:</strong> {s['degree_level']}<br><br>Make sure your intended program falls under the eligible degree levels before applying."

    else:
        answer = f"ℹ️ <strong>About this scholarship:</strong><br>{s['full_description'][:350] if s['full_description'] else 'Please visit the official website for full details.'}<br><br>💬 You can ask me about: <em>eligibility, IELTS requirements, deadline, documents needed, how to write SOP, or scholarship benefits.</em>"

    return jsonify({"answer": answer})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*50)
    print("  ScholarPath is running!")
    print("  Open: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=False, host="0.0.0.0", port=port)