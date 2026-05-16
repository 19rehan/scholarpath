from bs4 import BeautifulSoup
from scraper.extraction.title_extractor import extract_clean_title
from scraper.extraction.deadline_extractor import extract_deadline
from scraper.extraction.degree_extractor import extract_degree_level
from scraper.extraction.university_extractor import extract_university_name
from scraper.quality.scorer import calculate_quality_score
from scraper.storage.database import save_scholarship, check_duplicate
from scraper.utils.anti_blocking import get_headers, random_delay, get_session
from scraper.cleaning.garbage_filter import calculate_title_confidence

# Better test URLs - scholarship aggregators that list multiple scholarships
TEST_URLS = [
    'https://www.scholars4dev.com/category/scholarships/',
    'https://www.afterschoolafrica.com/scholarships/',
    'https://opportunitydesk.org/scholarships/',
]

def scrape_scholarship(url, session):
    print(f"\n{'='*60}")
    print(f"Scraping: {url}")
    print(f"{'='*60}")
    
    if check_duplicate(url):
        print("❌ Already in database, skipping")
        return None
    
    try:
        response = session.get(url, headers=get_headers(), timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract data
        title = extract_clean_title(soup, url)
        if not title:
            print("❌ No valid title found")
            return None
        
        title_confidence = calculate_title_confidence(title)
        
        if title_confidence < 60:
            print(f"❌ Title confidence too low: {title} ({title_confidence})")
            return None
            
        print(f"✅ Title: {title} (confidence: {title_confidence})")
        
        deadline = extract_deadline(soup)
        print(f"✅ Deadline: {deadline or 'Not found'}")
        
        degree_level = extract_degree_level(soup.get_text())
        print(f"✅ Degree: {degree_level or 'Not specified'}")
        
        university = extract_university_name(soup, url)
        print(f"✅ University: {university or 'Not found'}")
        
        # Build scholarship data
        scholarship_data = {
            'title': title,
            'official_url': url,
            'full_description': soup.get_text()[:1000],
            'university_name': university,
            'degree_level': degree_level,
            'deadline': deadline,
            'title_confidence': title_confidence,
            'source_trust_score': 80
        }
        
        # Calculate quality score
        quality_score = calculate_quality_score(scholarship_data)
        scholarship_data['quality_score'] = quality_score
        
        print(f"✅ Quality Score: {quality_score}/100")
        
        if quality_score >= 75:
            scholarship_id = save_scholarship(scholarship_data)
            if scholarship_id:
                print(f"✅ SAVED to database (ID: {scholarship_id})")
                return scholarship_id
            else:
                print("❌ Failed to save to database")
        else:
            print(f"❌ Quality too low ({quality_score} < 75), not saving")
        
        return None
        
    except Exception as e:
        print(f"❌ Error: {str(e)[:200]}")
        return None

def main():
    print("\n" + "="*60)
    print("SCHOLARSHIP INTELLIGENCE ENGINE - MVP v1.0")
    print("="*60)
    
    session = get_session()
    saved_count = 0
    
    for url in TEST_URLS:
        result = scrape_scholarship(url, session)
        if result:
            saved_count += 1
        random_delay(2, 4)
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETED: {saved_count}/{len(TEST_URLS)} scholarships saved")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()