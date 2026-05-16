from scraper.extraction.title_extractor import extract_clean_title
from scraper.cleaning.garbage_filter import calculate_title_confidence, is_garbage_title
from bs4 import BeautifulSoup

# Test HTML
test_html = """


    DAAD Scholarship 2026 - Study in Germany | DAAD Portal
    


    Select your language
    DAAD Scholarship 2026 for International Students
    The German Academic Exchange Service (DAAD) offers scholarships for master and PhD students.
    Deadline: March 31, 2026


"""

soup = BeautifulSoup(test_html, 'html.parser')

print("="*60)
print("TESTING EXTRACTION ENGINE")
print("="*60)

title = extract_clean_title(soup, 'https://www.daad.de/scholarship')
print(f"\n✅ Extracted Title: {title}")

confidence = calculate_title_confidence(title)
print(f"✅ Confidence: {confidence}/100")

garbage_tests = [
    "Select your language",
    "DAAD Scholarship 2026",
    "Apply Now",
    "Cookie Consent",
    "Chevening Scholarship"
]

print("\n" + "="*60)
print("GARBAGE FILTER TESTS")
print("="*60)

for test_title in garbage_tests:
    is_garbage = is_garbage_title(test_title)
    conf = calculate_title_confidence(test_title)
    status = "❌ BLOCKED" if is_garbage else "✅ PASSED"
    print(f"{status} | {test_title} | Confidence: {conf}")