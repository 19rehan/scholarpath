/**
 * Enhanced Recommendation System with 5-Star Match Scoring
 * Prioritizes: Country > Degree > Funding > IELTS > GPA > Eligibility
 */

export function getRecommendations(currentScholarship, allScholarships, limit = 6) {
  if (!currentScholarship || !allScholarships || allScholarships.length === 0) {
    return []
  }

  // Exclude current scholarship
  const otherScholarships = allScholarships.filter(s => s.id !== currentScholarship.id)

  // Calculate match score for each scholarship
  const scoredScholarships = otherScholarships.map(scholarship => {
    let score = 0
    const matchReasons = []

    // 1. COUNTRY MATCH (Highest Priority - 20 points)
    if (scholarship.country && currentScholarship.country) {
      if (scholarship.country.toLowerCase() === currentScholarship.country.toLowerCase()) {
        score += 20
        matchReasons.push('Same Country')
      }
    }

    // 2. DEGREE LEVEL MATCH (High Priority - 18 points)
    if (scholarship.degree_level && currentScholarship.degree_level) {
      const currentDegrees = currentScholarship.degree_level.toLowerCase().split(',').map(d => d.trim())
      const scholarshipDegrees = scholarship.degree_level.toLowerCase().split(',').map(d => d.trim())
      
      const hasMatch = currentDegrees.some(cd => scholarshipDegrees.some(sd => sd.includes(cd) || cd.includes(sd)))
      
      if (hasMatch) {
        score += 18
        matchReasons.push('Same Degree Level')
      }
    }

    // 3. FUNDING TYPE MATCH (High Priority - 15 points)
    if (scholarship.funding_type && currentScholarship.funding_type) {
      const currentFunding = currentScholarship.funding_type.toLowerCase()
      const scholarshipFunding = scholarship.funding_type.toLowerCase()
      
      const bothFullyFunded = currentFunding.includes('full') && scholarshipFunding.includes('full')
      const bothPartial = currentFunding.includes('partial') && scholarshipFunding.includes('partial')
      
      if (bothFullyFunded || bothPartial) {
        score += 15
        matchReasons.push('Same Funding Type')
      }
    }

    // 4. IELTS REQUIREMENT MATCH (Medium Priority - 12 points)
    const currentIelts = currentScholarship.ielts_score || 'not mentioned'
    const scholarshipIelts = scholarship.ielts_score || 'not mentioned'
    
    const currentNoIelts = currentIelts.toLowerCase().includes('not required') || 
                          currentIelts.toLowerCase().includes('not mentioned')
    const scholarshipNoIelts = scholarshipIelts.toLowerCase().includes('not required') || 
                              scholarshipIelts.toLowerCase().includes('not mentioned')
    
    if (currentNoIelts && scholarshipNoIelts) {
      score += 12
      matchReasons.push('No IELTS Required')
    } else if (!currentNoIelts && !scholarshipNoIelts) {
      // Both require IELTS - check if similar scores
      const currentScore = parseFloat(currentIelts.match(/\d+\.?\d*/)?.[0] || 0)
      const scholarshipScore = parseFloat(scholarshipIelts.match(/\d+\.?\d*/)?.[0] || 0)
      
      if (currentScore && scholarshipScore && Math.abs(currentScore - scholarshipScore) <= 0.5) {
        score += 12
        matchReasons.push('Similar IELTS Score')
      } else if (currentScore && scholarshipScore && Math.abs(currentScore - scholarshipScore) <= 1.0) {
        score += 8
        matchReasons.push('IELTS Required')
      }
    }

    // 5. GPA REQUIREMENT MATCH (Medium Priority - 10 points)
    const currentGpa = currentScholarship.gpa_required || 'not mentioned'
    const scholarshipGpa = scholarship.gpa_required || 'not mentioned'
    
    if (currentGpa !== 'not mentioned' && scholarshipGpa !== 'not mentioned' &&
        currentGpa.toLowerCase() !== 'check website' && scholarshipGpa.toLowerCase() !== 'check website') {
      
      const currentGpaNum = parseFloat(currentGpa.match(/\d+\.?\d*/)?.[0] || 0)
      const scholarshipGpaNum = parseFloat(scholarshipGpa.match(/\d+\.?\d*/)?.[0] || 0)
      
      if (currentGpaNum && scholarshipGpaNum && Math.abs(currentGpaNum - scholarshipGpaNum) <= 0.3) {
        score += 10
        matchReasons.push('Similar GPA Required')
      } else if (scholarshipGpaNum < currentGpaNum) {
        score += 6
        matchReasons.push('Lower GPA Requirement')
      }
    }

    // 6. ELIGIBLE COUNTRIES OVERLAP (Low Priority - 8 points)
    if (scholarship.eligible_countries && currentScholarship.eligible_countries) {
      const currentCountries = currentScholarship.eligible_countries.toLowerCase()
      const scholarshipCountries = scholarship.eligible_countries.toLowerCase()
      
      const commonKeywords = ['pakistan', 'india', 'bangladesh', 'africa', 'asia', 'all countries', 'international']
      const hasOverlap = commonKeywords.some(keyword => 
        currentCountries.includes(keyword) && scholarshipCountries.includes(keyword)
      )
      
      if (hasOverlap) {
        score += 8
        matchReasons.push('Your Country Eligible')
      }
    }

    // 7. SAME UNIVERSITY (Bonus - 5 points)
    if (scholarship.university_name && currentScholarship.university_name) {
      if (scholarship.university_name.toLowerCase() === currentScholarship.university_name.toLowerCase()) {
        score += 5
        matchReasons.push('Same University')
      }
    }

    // Calculate match percentage and star rating
    const maxPossibleScore = 20 + 18 + 15 + 12 + 10 + 8 + 5 // 88 points max
    const matchPercentage = Math.min(100, Math.round((score / maxPossibleScore) * 100))
    
    // Star rating based on percentage
    let starRating = 1
    if (matchPercentage >= 90) starRating = 5      // ⭐⭐⭐⭐⭐ Perfect Match
    else if (matchPercentage >= 70) starRating = 4  // ⭐⭐⭐⭐ Great Match
    else if (matchPercentage >= 50) starRating = 3  // ⭐⭐⭐ Good Match
    else if (matchPercentage >= 30) starRating = 2  // ⭐⭐ Possible Match
    
    return {
      ...scholarship,
      matchScore: score,
      matchPercentage,
      starRating,
      matchReasons: matchReasons.slice(0, 5) // Top 5 reasons
    }
  })

  // Sort by score (highest first) and filter out very low matches
  const topRecommendations = scoredScholarships
    .filter(s => s.matchPercentage >= 30) // Only show 30%+ matches
    .sort((a, b) => b.matchScore - a.matchScore)
    .slice(0, limit)

  return topRecommendations
}


/**
 * Helper: Get star emoji string
 */
export function getStarDisplay(starRating) {
  const fullStar = '⭐'
  const emptyStar = '☆'
  return fullStar.repeat(starRating) + emptyStar.repeat(5 - starRating)
}


/**
 * Helper: Get match badge color
 */
export function getMatchColor(matchPercentage) {
  if (matchPercentage >= 90) return { bg: 'linear-gradient(135deg, #059669, #10b981)', text: '#fff', label: 'Perfect Match' }
  if (matchPercentage >= 70) return { bg: 'linear-gradient(135deg, #0891b2, #06b6d4)', text: '#fff', label: 'Great Match' }
  if (matchPercentage >= 50) return { bg: 'linear-gradient(135deg, #f59e0b, #fbbf24)', text: '#fff', label: 'Good Match' }
  return { bg: 'linear-gradient(135deg, #64748b, #94a3b8)', text: '#fff', label: 'Possible Match' }
}
