# Run this once to create required legal pages
pages = {
    "privacy.html": """<!DOCTYPE html>
<html><head><title>Privacy Policy - ScholarPath</title>
<style>body{font-family:Arial,sans-serif;max-width:800px;margin:40px auto;padding:0 20px;line-height:1.8;color:#333}h1{color:#1a56db}h2{color:#1e3a8a;margin-top:30px}</style>
</head><body>
<h1>Privacy Policy</h1>
<p>Last updated: June 2025</p>
<h2>Information We Collect</h2>
<p>We collect information you provide directly such as name, email, country, and field of study when you use our scholarship matching service.</p>
<h2>How We Use Information</h2>
<p>We use collected information to match you with relevant scholarships, send deadline alerts, and improve our services.</p>
<h2>Google AdSense</h2>
<p>We use Google AdSense to display advertisements. Google may use cookies to serve ads based on your visits to this and other websites.</p>
<h2>Cookies</h2>
<p>We use cookies to improve your experience. You can disable cookies in your browser settings.</p>
<h2>Third Party Links</h2>
<p>Our website contains links to external scholarship websites. We are not responsible for their content or privacy practices.</p>
<h2>Contact Us</h2>
<p>For privacy concerns email us at: contact@scholarpath.com</p>
</body></html>""",

    "about.html": """<!DOCTYPE html>
<html><head><title>About Us - ScholarPath</title>
<style>body{font-family:Arial,sans-serif;max-width:800px;margin:40px auto;padding:0 20px;line-height:1.8;color:#333}h1{color:#1a56db}h2{color:#1e3a8a;margin-top:30px}</style>
</head><body>
<h1>About ScholarPath</h1>
<p>ScholarPath is a free AI-powered scholarship discovery platform built for students in Pakistan, India, Bangladesh, Africa and beyond.</p>
<h2>Our Mission</h2>
<p>Every year thousands of talented students with strong GPAs miss life-changing scholarships simply because they do not know where to look or how to apply. Consultants charge PKR 50,000 to 100,000 for guidance that should be free. We are changing that.</p>
<h2>What We Do</h2>
<p>We automatically collect fresh scholarships daily from trusted sources worldwide, rewrite them in simple language, and use AI to match each student with opportunities they actually qualify for — completely free.</p>
<h2>Our AI Assistant</h2>
<p>Our built-in AI guides students through every step — from checking eligibility to writing a Statement of Purpose, finding IELTS preparation centers, and planning their move abroad.</p>
<h2>Who We Are</h2>
<p>We are a team passionate about making quality education accessible to every deserving student regardless of their financial background.</p>
</body></html>""",

    "contact.html": """<!DOCTYPE html>
<html><head><title>Contact Us - ScholarPath</title>
<style>body{font-family:Arial,sans-serif;max-width:800px;margin:40px auto;padding:0 20px;line-height:1.8;color:#333}h1{color:#1a56db}input,textarea{width:100%;padding:10px;margin:8px 0;border:1px solid #ddd;border-radius:6px;font-size:14px}button{background:#1a56db;color:white;padding:12px 30px;border:none;border-radius:6px;cursor:pointer;font-size:16px}</style>
</head><body>
<h1>Contact ScholarPath</h1>
<p>Have a question or want to partner with us? We would love to hear from you.</p>
<p><strong>Email:</strong> contact@scholarpath.com</p>
<p><strong>Response time:</strong> Within 24 hours</p>
<p><strong>For partnership inquiries</strong> (IELTS centers, universities, hostels): partner@scholarpath.com</p>
</body></html>"""
}

import os
for filename, content in pages.items():
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {filename}")

print("\nAll pages created successfully!")