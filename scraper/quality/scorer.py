def calculate_quality_score(scholarship_data):
    score = 0
    
    # Has official URL (25 points)
    if scholarship_data.get('official_url') and scholarship_data.get('official_url').startswith('http'):
        score += 25
    
    # Has deadline (20 points)
    if scholarship_data.get('deadline'):
        score += 20
    
    # Has university (15 points)
    if scholarship_data.get('university_name'):
        score += 15
    
    # Has degree level (10 points)
    if scholarship_data.get('degree_level'):
        score += 10
    
    # Title quality (15 points)
    title_conf = scholarship_data.get('title_confidence', 0)
    score += min(15, title_conf * 0.15)
    
    # Has description (10 points)
    if scholarship_data.get('full_description') and len(scholarship_data['full_description']) > 100:
        score += 10
    
    # Source trust (5 points)
    source_trust = scholarship_data.get('source_trust_score', 50)
    score += min(5, source_trust * 0.05)
    
    return min(100, int(score))