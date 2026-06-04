/**
 * Recommendation System with 5-Star Match Scoring
 */

export function getRecommendations(currentScholarship, allScholarships, limit = 6) {
  if (!currentScholarship || !allScholarships || allScholarships.length === 0) return []

  const otherScholarships = allScholarships.filter(s => s.id !== currentScholarship.id)

  const scoredScholarships = otherScholarships.map(scholarship => {
    let score = 0
    const matchReasons = []

    // 1. COUNTRY MATCH (20 points)
    if (scholarship.country && currentScholarship.country) {
      if (scholarship.country.toLowerCase() === currentScholarship.country.toLowerCase()) {
        score += 20
        matchReasons.push('Same Country')
      }
    }

    // 2. DEGREE LEVEL MATCH (18 points)
    if (scholarship.degree_level && currentScholarship.degree_level) {
      const currentDegrees = currentScholarship.degree_level.toLowerCase().split(',').map(d => d.trim())
      const scholarshipDegrees = scholarship.degree_level.toLowerCase().split(',').map(d => d.trim())
      const hasMatch = currentDegrees.some(cd => scholarshipDegrees.some(sd => sd.includes(cd) || cd.includes(sd)))
      if (hasMatch) { score += 18; matchReasons.push('Same Degree Level') }
    }

    // 3. FUNDING TYPE MATCH (15 points)
    if (scholarship.funding_type && currentScholarship.funding_type) {
      const currentFunding = currentScholarship.funding_type.toLowerCase()
      const scholarshipFunding = scholarship.funding_type.toLowerCase()
      if ((currentFunding.includes('full') && scholarshipFunding.includes('full')) ||
          (currentFunding.includes('partial') && scholarshipFunding.includes('partial'))) {
        score += 15
        matchReasons.push('Same Funding Type')
      }
    }

    // 4. IELTS MATCH (12 points)
    const currentIelts = currentScholarship.ielts_score || 'not mentioned'
    const scholarshipIelts = scholarship.ielts_score || 'not mentioned'
    const currentNoIelts = currentIelts.toLowerCase().includes('not required') || currentIelts.toLowerCase().includes('not mentioned')
    const scholarshipNoIelts = scholarshipIelts.toLowerCase().includes('not required') || scholarshipIelts.toLowerCase().includes('not mentioned')

    if (currentNoIelts && scholarshipNoIelts) {
      score += 12; matchReasons.push('No IELTS Required')
    } else if (!currentNoIelts && !scholarshipNoIelts) {
      const cs = parseFloat(currentIelts.match(/\d+\.?\d*/)?.[0] || 0)
      const ss = parseFloat(scholarshipIelts.match(/\d+\.?\d*/)?.[0] || 0)
      if (cs && ss && Math.abs(cs - ss) <= 0.5) { score += 12; matchReasons.push('Similar IELTS Score') }
      else if (cs && ss && Math.abs(cs - ss) <= 1.0) { score += 8; matchReasons.push('IELTS Required') }
    }

    // 5. GPA MATCH (10 points)
    const currentGpa = currentScholarship.gpa_required || 'not mentioned'
    const scholarshipGpa = scholarship.gpa_required || 'not mentioned'
    if (currentGpa !== 'not mentioned' && scholarshipGpa !== 'not mentioned') {
      const cg = parseFloat(currentGpa.match(/\d+\.?\d*/)?.[0] || 0)
      const sg = parseFloat(scholarshipGpa.match(/\d+\.?\d*/)?.[0] || 0)
      if (cg && sg && Math.abs(cg - sg) <= 0.3) { score += 10; matchReasons.push('Similar GPA Required') }
      else if (sg < cg) { score += 6; matchReasons.push('Lower GPA Requirement') }
    }

    // 6. ELIGIBLE COUNTRIES (8 points)
    if (scholarship.eligible_countries && currentScholarship.eligible_countries) {
      const cc = currentScholarship.eligible_countries.toLowerCase()
      const sc = scholarship.eligible_countries.toLowerCase()
      const keywords = ['pakistan', 'india', 'bangladesh', 'africa', 'asia', 'all countries', 'international']
      if (keywords.some(k => cc.includes(k) && sc.includes(k))) {
        score += 8; matchReasons.push('Your Country Eligible')
      }
    }

    // 7. SAME UNIVERSITY (5 points)
    if (scholarship.university_name && currentScholarship.university_name &&
        scholarship.university_name.toLowerCase() === currentScholarship.university_name.toLowerCase()) {
      score += 5; matchReasons.push('Same University')
    }

    const maxPossibleScore = 88
    const matchPercentage = Math.min(100, Math.round((score / maxPossibleScore) * 100))
    let starRating = 1
    if (matchPercentage >= 90) starRating = 5
    else if (matchPercentage >= 70) starRating = 4
    else if (matchPercentage >= 50) starRating = 3
    else if (matchPercentage >= 30) starRating = 2

    return { ...scholarship, matchScore: score, matchPercentage, starRating, matchReasons: matchReasons.slice(0, 5) }
  })

  return scoredScholarships
    .filter(s => s.matchPercentage >= 30)
    .sort((a, b) => b.matchScore - a.matchScore)
    .slice(0, limit)
}

export function getStarDisplay(starRating) {
  return '★'.repeat(starRating) + '☆'.repeat(5 - starRating)
}

export function getMatchColor(matchPercentage) {
  if (matchPercentage >= 90) return { bg: 'linear-gradient(135deg, #059669, #10b981)', text: '#fff', label: 'Perfect Match' }
  if (matchPercentage >= 70) return { bg: 'linear-gradient(135deg, #0891b2, #06b6d4)', text: '#fff', label: 'Great Match' }
  if (matchPercentage >= 50) return { bg: 'linear-gradient(135deg, #f59e0b, #fbbf24)', text: '#fff', label: 'Good Match' }
  return { bg: 'linear-gradient(135deg, #64748b, #94a3b8)', text: '#fff', label: 'Possible Match' }
}

// ── NEW: Score a scholarship against a USER PROFILE ──────────────────
export function scoreScholarshipForUser(scholarship, profile) {
  if (!profile) return { matchPercentage: 0, matchReasons: [] }

  let score = 0
  const matchReasons = []

  // 1. DEGREE LEVEL (25 points)
  if (profile.degree_level && scholarship.degree_level) {
    const profileDegree = profile.degree_level.toLowerCase().trim()
    const scholarshipDegrees = scholarship.degree_level.toLowerCase()
    if (scholarshipDegrees.includes(profileDegree)) {
      score += 25
      matchReasons.push('Matches your degree')
    }
  }

  // 2. PREFERRED COUNTRY (20 points)
  if (profile.preferred_countries?.length > 0 && scholarship.country) {
    const scholarshipCountry = scholarship.country.toLowerCase()
    const preferred = profile.preferred_countries.map(c => c.toLowerCase())
    if (preferred.some(c => scholarshipCountry.includes(c) || c.includes(scholarshipCountry))) {
      score += 20
      matchReasons.push('Your preferred country')
    }
  }

  // 3. FUNDING PREFERENCE (20 points)
  if (profile.funding_preference && scholarship.funding_type) {
    const pref = profile.funding_preference.toLowerCase()
    const funding = scholarship.funding_type.toLowerCase()
    if (pref === 'any') {
      score += 10
    } else if (pref.includes('full') && funding.includes('full')) {
      score += 20
      matchReasons.push('Fully funded')
    } else if (pref.includes('partial') && funding.includes('partial')) {
      score += 20
      matchReasons.push('Matches funding preference')
    }
  }

  // 4. IELTS SCORE (15 points)
  if (scholarship.ielts_score) {
    const ieltsText = scholarship.ielts_score.toLowerCase()
    const noIelts = ieltsText.includes('not required') || ieltsText.includes('not mentioned')

    if (noIelts) {
      score += 15
      matchReasons.push('No IELTS needed')
    } else if (profile.ielts_score) {
      const required = parseFloat(ieltsText.match(/\d+\.?\d*/)?.[0] || 0)
      const userScore = parseFloat(profile.ielts_score)
      if (required && userScore >= required) {
        score += 15
        matchReasons.push('IELTS score qualifies')
      } else if (required && userScore >= required - 0.5) {
        score += 8
        matchReasons.push('IELTS score close')
      }
    }
  }

  // 5. GPA (10 points)
  if (profile.gpa && scholarship.gpa_required) {
    const gpaText = scholarship.gpa_required.toLowerCase()
    const required = parseFloat(gpaText.match(/\d+\.?\d*/)?.[0] || 0)
    const userGpa = parseFloat(profile.gpa)
    if (required && userGpa >= required) {
      score += 10
      matchReasons.push('GPA qualifies')
    } else if (required && userGpa >= required - 0.3) {
      score += 5
      matchReasons.push('GPA close to requirement')
    }
  }

  // 6. ELIGIBLE COUNTRIES (10 points)
  if (profile.nationality && scholarship.eligible_countries) {
    const eligible = scholarship.eligible_countries.toLowerCase()
    const nationality = profile.nationality.toLowerCase()
    if (
      eligible.includes('all') ||
      eligible.includes('international') ||
      eligible.includes(nationality)
    ) {
      score += 10
      matchReasons.push('You are eligible')
    }
  }

  const maxScore = 100
  const matchPercentage = Math.min(100, Math.round((score / maxScore) * 100))

  return { matchPercentage, matchReasons: matchReasons.slice(0, 3) }
}