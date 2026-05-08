from flask import Flask, render_template_string, request
import sqlite3
import json

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('scholarships.db')
    conn.row_factory = sqlite3.Row
    return conn

# ─── HOME PAGE ────────────────────────────────────────────
HOME = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ScholarPath – Find Scholarships Worldwide</title>
<meta name="description" content="Find the latest scholarships worldwide. Free guidance on eligibility, IELTS requirements, and how to apply.">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'Segoe UI', sans-serif; background:#f4f7fb; color:#222; }
header { background:#1a56db; color:white; padding:20px 40px; display:flex; justify-content:space-between; align-items:center; }
header h1 { font-size:24px; }
header span { font-size:13px; opacity:0.8; }
.hero { background:linear-gradient(135deg,#1a56db,#0e9f6e); color:white; text-align:center; padding:60px 20px; }
.hero h2 { font-size:36px; margin-bottom:10px; }
.hero p { font-size:18px; opacity:0.9; margin-bottom:30px; }
.search-box { display:flex; max-width:500px; margin:0 auto; }
.search-box input { flex:1; padding:14px 20px; border:none; border-radius:8px 0 0 8px; font-size:16px; }
.search-box button { padding:14px 24px; background:#0e9f6e; color:white; border:none; border-radius:0 8px 8px 0; cursor:pointer; font-size:16px; }
.stats { display:flex; justify-content:center; gap:40px; padding:30px; background:white; border-bottom:1px solid #eee; }
.stat { text-align:center; }
.stat strong { display:block; font-size:28px; color:#1a56db; }
.stat span { font-size:14px; color:#666; }
.container { max-width:1100px; margin:30px auto; padding:0 20px; }
.filters { display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap; }
.filters select { padding:8px 14px; border:1px solid #ddd; border-radius:6px; font-size:14px; background:white; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:20px; }
.card { background:white; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.08); transition:transform 0.2s; }
.card:hover { transform:translateY(-4px); box-shadow:0 6px 20px rgba(0,0,0,0.12); }
.card h3 { font-size:16px; margin-bottom:10px; color:#1a56db; line-height:1.4; }
.badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:12px; margin:2px; }
.badge.green { background:#d1fae5; color:#065f46; }
.badge.blue { background:#dbeafe; color:#1e40af; }
.badge.orange { background:#fed7aa; color:#9a3412; }
.card p { font-size:13px; color:#666; margin:10px 0; line-height:1.5; }
.card a { display:block; text-align:center; background:#1a56db; color:white; padding:10px; border-radius:8px; text-decoration:none; font-size:14px; margin-top:12px; }
.card a:hover { background:#1648c0; }
.deadline { font-size:12px; color:#e53e3e; font-weight:600; margin-top:8px; }
footer { text-align:center; padding:30px; color:#888; font-size:13px; margin-top:40px; border-top:1px solid #eee; }
</style>
</head>
<body>
<header>
  <h1>🎓 ScholarPath</h1>
  <span>Your Free Scholarship Guide</span>
</header>
<div class="hero">
  <h2>Find Your Perfect Scholarship</h2>
  <p>Thousands of scholarships. Free AI guidance. Zero cost to you.</p>
  <form method="GET" action="/search">
  <div class="search-box">
    <input type="text" name="q" placeholder="Search scholarships, countries, universities...">
    <button type="submit">Search</button>
  </div>
  </form>
</div>
<div class="stats">
  <div class="stat"><strong>{{ total }}</strong><span>Scholarships</span></div>
  <div class="stat"><strong>50+</strong><span>Countries</span></div>
  <div class="stat"><strong>Free</strong><span>AI Guidance</span></div>
</div>
<div class="container">
  <div class="filters">
    <select onchange="window.location='/?level='+this.value">
      <option value="">All Levels</option>
      <option value="Bachelor">Bachelor's</option>
      <option value="Master">Master's</option>
      <option value="PhD">PhD</option>
    </select>
  </div>
  <div class="grid">
    {% for s in scholarships %}
    <div class="card">
      <h3>{{ s['seo_title'] or s['title'] }}</h3>
      {% if s['degree_level'] and s['degree_level'] != 'Not specified' %}
      <span class="badge blue">{{ s['degree_level'][:30] }}</span>
      {% endif %}
      {% if s['ielts_score'] and s['ielts_score'] != 'Not required' %}
      <span class="badge orange">IELTS: {{ s['ielts_score'] }}</span>
      {% endif %}
      <span class="badge green">Open</span>
      <p>{{ s['seo_description'] or s['full_description'][:120] }}</p>
      {% if s['deadline'] %}
      <div class="deadline">📅 Deadline: {{ s['deadline'] }}</div>
      {% endif %}
      <a href="/scholarship/{{ s['id'] }}">View Full Guide & Apply →</a>
    </div>
    {% endfor %}
  </div>
</div>
<footer>© 2025 ScholarPath · Free scholarship guidance for students worldwide</footer>
</body>
</html>
'''

# ─── DETAIL PAGE ──────────────────────────────────────────
DETAIL = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ s['seo_title'] }}</title>
<meta name="description" content="{{ s['seo_description'] }}">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',sans-serif; background:#f4f7fb; color:#222; }
header { background:#1a56db; color:white; padding:16px 40px; }
header a { color:white; text-decoration:none; font-size:20px; font-weight:bold; }
.container { max-width:860px; margin:30px auto; padding:0 20px; }
.blog { background:white; border-radius:12px; padding:40px; box-shadow:0 2px 8px rgba(0,0,0,0.08); }
.blog h1 { font-size:28px; color:#1a56db; margin-bottom:20px; line-height:1.3; }
.blog h2 { font-size:20px; color:#1e3a8a; margin:30px 0 12px; border-left:4px solid #1a56db; padding-left:12px; }
.blog p { font-size:15px; line-height:1.8; color:#444; margin-bottom:14px; }
.blog table { width:100%; border-collapse:collapse; margin:20px 0; }
.blog table td, .blog table th { padding:12px 16px; border:1px solid #e2e8f0; font-size:14px; }
.blog table th { background:#f0f4ff; font-weight:600; }
.blog table tr:nth-child(even) { background:#f9fafb; }
.blog ul, .blog ol { padding-left:24px; margin:14px 0; }
.blog li { font-size:15px; line-height:2; color:#444; }
.blog strong { color:#1a56db; }
.ai-box { background:#f0f9ff; border:1px solid #bae6fd; border-radius:10px; padding:20px; margin:30px 0; }
.ai-box h3 { color:#0369a1; margin-bottom:10px; }
.ai-box input { width:100%; padding:10px 14px; border:1px solid #bae6fd; border-radius:6px; font-size:14px; margin:8px 0; }
.ai-box button { background:#1a56db; color:white; border:none; padding:10px 24px; border-radius:6px; cursor:pointer; font-size:14px; }
.ai-box #answer { margin-top:14px; font-size:14px; line-height:1.7; color:#1e3a8a; background:white; padding:14px; border-radius:6px; display:none; }
.apply-btn { display:block; text-align:center; background:#0e9f6e; color:white; padding:16px; border-radius:10px; text-decoration:none; font-size:18px; font-weight:bold; margin:30px 0; }
.apply-btn:hover { background:#059669; }
.back { display:inline-block; margin-bottom:20px; color:#1a56db; text-decoration:none; font-size:14px; }
</style>
</head>
<body>
<header><a href="/">🎓 ScholarPath</a></header>
<div class="container">
  <a href="/" class="back">← Back to all scholarships</a>
  <div class="blog">
    <div id="blog-content">{{ blog_html | safe }}</div>
    <a href="{{ s['scholarship_link'] }}" target="_blank" class="apply-btn">
      🚀 Apply Now – Official Website
    </a>
    <div class="ai-box">
      <h3>🤖 Ask AI About This Scholarship</h3>
      <p>Have a question? Our AI will answer instantly.</p>
      <input type="text" id="q" placeholder="e.g. Can Pakistani students apply? What IELTS score do I need?">
      <button onclick="askAI()">Ask AI</button>
      <div id="answer"></div>
    </div>
  </div>
</div>
<script>
function askAI() {
  const q = document.getElementById('q').value;
  const ans = document.getElementById('answer');
  if (!q) return;
  ans.style.display = 'block';
  ans.innerHTML = '⏳ Thinking...';
  fetch('/ask', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({question: q, scholarship_id: {{ s['id'] }} })
  })
  .then(r => r.json())
  .then(d => { ans.innerHTML = d.answer; });
}
document.getElementById('q').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') askAI();
});
</script>
</body>
</html>
'''

# ─── SEARCH PAGE ──────────────────────────────────────────
SEARCH = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Search: {{ query }} – ScholarPath</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',sans-serif; background:#f4f7fb; }
header { background:#1a56db; color:white; padding:16px 40px; }
header a { color:white; text-decoration:none; font-size:20px; font-weight:bold; }
.container { max-width:1100px; margin:30px auto; padding:0 20px; }
h2 { margin-bottom:20px; color:#333; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:20px; }
.card { background:white; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.08); }
.card h3 { font-size:16px; color:#1a56db; margin-bottom:10px; }
.card p { font-size:13px; color:#666; }
.card a { display:block; text-align:center; background:#1a56db; color:white; padding:10px; border-radius:8px; text-decoration:none; margin-top:12px; font-size:14px; }
</style>
</head>
<body>
<header><a href="/">🎓 ScholarPath</a></header>
<div class="container">
  <h2>Search results for: "{{ query }}" ({{ results|length }} found)</h2>
  <div class="grid">
  {% for s in results %}
    <div class="card">
      <h3>{{ s['title'] }}</h3>
      <p>{{ s['seo_description'] or s['full_description'][:120] }}</p>
      <a href="/scholarship/{{ s['id'] }}">View Full Guide →</a>
    </div>
  {% endfor %}
  {% if not results %}
    <p>No scholarships found for "{{ query }}". <a href="/">Go back</a></p>
  {% endif %}
  </div>
</div>
</body>
</html>
'''

# ─── ROUTES ───────────────────────────────────────────────
@app.route('/')
def home():
    conn = get_db()
    level = request.args.get('level', '')
    if level:
        rows = conn.execute(
            "SELECT * FROM scholarship_details WHERE degree_level LIKE ? ORDER BY id DESC",
            (f'%{level}%',)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM scholarship_details ORDER BY id DESC"
        ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM scholarship_details").fetchone()[0]
    conn.close()
    return render_template_string(HOME, scholarships=rows, total=total)

@app.route('/scholarship/<int:sid>')
def scholarship(sid):
    conn = get_db()
    s = conn.execute(
        "SELECT * FROM scholarship_details WHERE id=?", (sid,)
    ).fetchone()
    conn.close()
    if not s:
        return "Scholarship not found", 404

    # Convert markdown-style blog to basic HTML
    blog_text = s['blog_post'] or ""
    blog_html = convert_to_html(blog_text)
    return render_template_string(DETAIL, s=s, blog_html=blog_html)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    conn = get_db()
    results = conn.execute(
        """SELECT * FROM scholarship_details 
           WHERE title LIKE ? OR seo_description LIKE ? OR eligible_countries LIKE ?
           ORDER BY id DESC""",
        (f'%{query}%', f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    return render_template_string(SEARCH, query=query, results=results)

@app.route('/ask', methods=['POST'])
def ask_ai():
    import json
    data = request.get_json()
    question = data.get('question', '').lower()
    sid = data.get('scholarship_id')

    conn = get_db()
    s = conn.execute(
        "SELECT * FROM scholarship_details WHERE id=?", (sid,)
    ).fetchone()
    conn.close()

    if not s:
        return json.dumps({"answer": "Sorry, I could not find this scholarship."})

    # Smart rule-based AI answers
    answer = ""

    if any(w in question for w in ['ielts', 'english', 'language', 'pte', 'toefl']):
        answer = f"For this scholarship, the language requirement is: <strong>{s['language_requirement']}</strong>. IELTS score required: <strong>{s['ielts_score']}</strong>. If you are from Pakistan, you will need to provide an official IELTS or TOEFL certificate unless your previous education was in English."

    elif any(w in question for w in ['deadline', 'last date', 'when', 'date', 'closing']):
        answer = f"The application deadline for this scholarship is: <strong>{s['deadline']}</strong>. We recommend applying at least 2 weeks before the deadline to avoid last-minute issues."

    elif any(w in question for w in ['eligible', 'who can', 'apply', 'pakistan', 'nationality', 'country', 'countries']):
        answer = f"Eligibility details: <strong>{s['eligible_countries'][:300]}</strong>. Pakistani students are generally welcome to apply for international scholarships. Always verify on the official website."

    elif any(w in question for w in ['benefit', 'cover', 'fund', 'money', 'stipend', 'tuition']):
        answer = f"Scholarship benefits: <strong>{s['benefits'][:300]}</strong>. Check the official website for the complete and updated funding details."

    elif any(w in question for w in ['degree', 'level', 'bachelor', 'master', 'phd']):
        answer = f"This scholarship is available for: <strong>{s['degree_level']}</strong>."

    elif any(w in question for w in ['sop', 'statement', 'essay', 'write']):
        answer = """Here is how to write a strong SOP for this scholarship:<br><br>
        1. <strong>Opening paragraph:</strong> Start with a compelling story or achievement<br>
        2. <strong>Academic background:</strong> Mention your degrees and grades<br>
        3. <strong>Why this scholarship:</strong> Be specific about why you chose this program<br>
        4. <strong>Career goals:</strong> Explain how this scholarship helps your future plans<br>
        5. <strong>Why you deserve it:</strong> Highlight unique qualities and achievements<br>
        6. <strong>Closing:</strong> Thank the committee and restate your commitment<br><br>
        Keep it between 600-1000 words unless specified otherwise."""

    elif any(w in question for w in ['document', 'require', 'need', 'submit']):
        answer = """Documents usually required:<br>
        ✅ Valid Passport<br>
        ✅ Academic Transcripts<br>
        ✅ IELTS/TOEFL Certificate<br>
        ✅ Statement of Purpose (SOP)<br>
        ✅ 2-3 Recommendation Letters<br>
        ✅ Updated CV/Resume<br>
        ✅ Passport-size photos<br>
        ✅ Research Proposal (PhD only)"""

    else:
        answer = f"Based on available information about <strong>{s['title']}</strong>: {s['full_description'][:300]}... For more specific details, please visit the official scholarship website."

    return json.dumps({"answer": answer})

# ─── MARKDOWN TO HTML CONVERTER ───────────────────────────
def convert_to_html(text):
    import re
    # Headers
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Table rows
    lines = text.split('\n')
    html_lines = []
    in_table = False
    for line in lines:
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                html_lines.append('<table>')
                in_table = True
            if re.match(r'\|[\s\-|]+\|', line):
                continue
            cols = [c.strip() for c in line.strip('|').split('|')]
            html_lines.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cols) + '</tr>')
        else:
            if in_table:
                html_lines.append('</table>')
                in_table = False
            html_lines.append(line)
    if in_table:
        html_lines.append('</table>')
    text = '\n'.join(html_lines)
    # Lists
    text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', text, flags=re.MULTILINE)
    # Horizontal rule
    text = re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)
    # Paragraphs
    text = re.sub(r'\n\n', r'</p><p>', text)
    text = f'<p>{text}</p>'
    return text

# ─── RUN ──────────────────────────────────────────────────
if __name__ == '__main__':
    print("\n" + "="*50)
    print("  ScholarPath website running!")
    print("  Open your browser and go to:")
    print("  http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)