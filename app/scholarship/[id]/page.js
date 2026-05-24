'use client'
import { useEffect, useState } from 'react'
import { supabase } from '../../../lib/supabase'
import { getRecommendations, getStarDisplay, getMatchColor } from '../../../lib/recommendations'
import Link from 'next/link'
import { GraduationCap, MapPin, Clock, ExternalLink, ChevronRight, ArrowLeft, Globe, DollarSign, FileText } from 'lucide-react'

export default function ScholarshipPage({ params }) {
  const [scholarship, setScholarship] = useState(null)
  const [loading, setLoading] = useState(true)
  const [resolvedId, setResolvedId] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [hasUserProfile, setHasUserProfile] = useState(false)

  useEffect(() => {
    async function resolveParams() {
      const resolved = await params
      setResolvedId(resolved.id)
    }
    resolveParams()
  }, [params])

  useEffect(() => {
    if (resolvedId) {
      setScholarship(null)
      setRecommendations([])
      fetchScholarship()
    }
  }, [resolvedId])

  async function fetchScholarship() {
    try {
      const { data, error } = await supabase
        .from('scholarship_details')
        .select('*')
        .eq('id', resolvedId)
        .single()
      if (error) throw error
      setScholarship(data)
      setLoading(false)
      if (data) {
        const { data: allScholarships } = await supabase
          .from('scholarship_details')
          .select('id, title, country, university_name, degree_level, funding_type, eligible_countries, deadline, ielts_score, gpa_required, scholarship_link, benefits, blog_post, full_description, seo_description')
          .order('last_updated', { ascending: false })
          .limit(100)
        if (allScholarships) {
          const recs = getRecommendations(data, allScholarships, 6)
          setRecommendations(recs)
        }
      }
    } catch (error) {
      console.error('Error fetching scholarship:', error)
      setLoading(false)
    }
  }

  function getTitleColor(scholarship) {
    if (!scholarship) return '#4f46e5'
    const funding = (scholarship.funding_type || '').toLowerCase()
    const title = (scholarship.title || '').toLowerCase()
    if (funding.includes('full') || title.includes('fully funded')) return '#059669'
    if (funding.includes('partial')) return '#f59e0b'
    return '#4f46e5'
  }

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f8fafc' }}>
        <div style={{ color: '#4f46e5', fontWeight: '600', fontSize: '16px' }}>Loading...</div>
      </div>
    )
  }

  if (!scholarship) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f8fafc' }}>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '16px' }}>Scholarship not found</h2>
          <Link href="/" style={{ padding: '12px 24px', background: '#4f46e5', color: 'white', borderRadius: '12px', textDecoration: 'none', fontWeight: '600' }}>Go Back</Link>
        </div>
      </div>
    )
  }

  const s = scholarship
  const isFullyFunded = s.funding_type?.toLowerCase().includes('full') || s.title?.toLowerCase().includes('fully funded')
  const noIelts = s.ielts_score === 'Not required' || s.ielts_score === 'Not mentioned'
  const mainTitleColor = getTitleColor(s)

  return (
    <div style={{ minHeight: '100vh', background: '#fafafa', fontFamily: "'Inter',-apple-system,sans-serif" }}>

      {/* NAVBAR */}
      <nav style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(20px)', borderBottom: '1px solid #f0f0f0', height: '60px', display: 'flex', alignItems: 'center' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
            <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg,#4f46e5,#7c3aed)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={18} color="white" />
            </div>
            <span style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.5px' }}>Admit<span style={{ color: '#4f46e5' }}>Goal</span></span>
          </Link>
          <a href={s.scholarship_link} target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '9px 20px', background: '#059669', color: 'white', borderRadius: '10px', fontSize: '13px', fontWeight: '600', textDecoration: 'none' }}>
            Apply Now <ExternalLink size={14} />
          </a>
        </div>
      </nav>

      {/* HERO */}
      <div style={{ paddingTop: '60px', background: 'linear-gradient(135deg,#0f172a,#1e1b4b,#312e81)' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 24px 40px' }}>

          <button onClick={() => window.history.back()} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'rgba(255,255,255,0.5)', fontSize: '13px', marginBottom: '20px', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', padding: '0' }}>
            <ArrowLeft size={14} /> Back
          </button>

          {/* TWO COLUMN HERO */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '48px', alignItems: 'center' }}>

            {/* LEFT — Title + badges */}
            <div>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '14px', flexWrap: 'wrap' }}>
                {s.university_name && (
                  <span style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.15)', color: 'rgba(255,255,255,0.8)', padding: '3px 12px', borderRadius: '100px', fontSize: '12px', fontWeight: '600' }}>
                    {s.university_name}
                  </span>
                )}
                {s.region && (
                  <span style={{ background: 'rgba(79,70,229,0.3)', border: '1px solid rgba(99,102,241,0.4)', color: '#a5b4fc', padding: '3px 12px', borderRadius: '100px', fontSize: '12px', fontWeight: '600' }}>
                    {s.region}
                  </span>
                )}
              </div>

              <h1 style={{ fontSize: 'clamp(22px,3.5vw,38px)', fontWeight: '800', color: mainTitleColor, lineHeight: '1.25', marginBottom: '24px', letterSpacing: '-0.5px', textShadow: '0 2px 20px rgba(0,0,0,0.3)' }}>
                {s.seo_title || s.title}
              </h1>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {s.country && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.12)', color: 'rgba(255,255,255,0.85)', padding: '6px 14px', borderRadius: '8px', fontSize: '13px', fontWeight: '500' }}>
                    <MapPin size={12} />{s.country}
                  </div>
                )}
                {s.degree_level && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.12)', color: 'rgba(255,255,255,0.85)', padding: '6px 14px', borderRadius: '8px', fontSize: '13px', fontWeight: '500' }}>
                    <GraduationCap size={12} />{s.degree_level}
                  </div>
                )}
                {isFullyFunded && (
                  <div style={{ background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)', color: '#6ee7b7', padding: '6px 14px', borderRadius: '8px', fontSize: '13px', fontWeight: '600' }}>
                    Fully Funded
                  </div>
                )}
                {noIelts && (
                  <div style={{ background: 'rgba(20,184,166,0.15)', border: '1px solid rgba(20,184,166,0.3)', color: '#5eead4', padding: '6px 14px', borderRadius: '8px', fontSize: '13px', fontWeight: '600' }}>
                    No IELTS
                  </div>
                )}
              </div>
            </div>

            {/* RIGHT — Clean rows on hero bg */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ fontSize: '11px', fontWeight: '700', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '1.5px', marginBottom: '4px' }}>
                Scholarship Details
              </div>
              {[
                { label: 'Deadline', value: s.deadline || 'See website', icon: <Clock size={14} />, color: '#fca5a5' },
                { label: 'Funding', value: s.funding_type || 'Check website', icon: <DollarSign size={14} />, color: '#6ee7b7' },
                { label: 'IELTS', value: s.ielts_score || 'Not required', icon: <FileText size={14} />, color: '#fcd34d' },
                { label: 'Min GPA', value: s.gpa_required || 'Check website', icon: <FileText size={14} />, color: '#a5b4fc' },
                { label: 'Language', value: s.language_requirement || 'Check website', icon: <Globe size={14} />, color: '#c4b5fd' },
              ].map(({ label, value, icon, color }) => (
                <div key={label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '14px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'rgba(255,255,255,0.45)', fontSize: '13px', fontWeight: '500' }}>
                    {icon}{label}
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: '700', color }}>
                    {value}
                  </div>
                </div>
              ))}
              <a href={s.scholarship_link} target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginTop: '4px', padding: '13px', background: 'linear-gradient(135deg,#059669,#10b981)', color: 'white', borderRadius: '12px', textDecoration: 'none', fontSize: '14px', fontWeight: '700', boxShadow: '0 6px 20px rgba(16,185,129,0.25)' }}>
                Apply Now — Official Site <ExternalLink size={14} />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '28px' }}>

          {/* LEFT — BLOG */}
          <div>
            {s.blog_post ? (
              <div style={{ background: 'white', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '40px' }}>
                <div className="blog-content" dangerouslySetInnerHTML={{ __html: s.blog_post }} />
              </div>
            ) : s.full_description ? (
              <div style={{ background: 'white', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '40px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#0f172a', marginBottom: '16px' }}>About This Scholarship</h2>
                <p style={{ fontSize: '15px', lineHeight: '1.9', color: '#475569' }}>{s.full_description}</p>
              </div>
            ) : (
              <div style={{ background: 'white', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '40px', textAlign: 'center' }}>
                <p style={{ color: '#94a3b8', fontSize: '15px' }}>Visit the official website for full details.</p>
                <a href={s.scholarship_link} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginTop: '16px', padding: '12px 24px', background: '#4f46e5', color: 'white', borderRadius: '10px', textDecoration: 'none', fontWeight: '600', fontSize: '14px' }}>
                  Visit Official Website <ExternalLink size={14} />
                </a>
              </div>
            )}
          </div>

          {/* RIGHT SIDEBAR */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

            {/* APPLY BUTTON */}
            <a href={s.scholarship_link} target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '14px', background: 'linear-gradient(135deg,#059669,#10b981)', color: 'white', borderRadius: '12px', textDecoration: 'none', fontSize: '15px', fontWeight: '700', boxShadow: '0 8px 24px rgba(16,185,129,0.25)' }}>
              Apply Now <ExternalLink size={15} />
            </a>

            {/* EXPLORE MORE */}
            <div style={{ background: 'white', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '18px' }}>
              <h3 style={{ fontSize: '13px', fontWeight: '700', color: '#0f172a', marginBottom: '14px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Explore More</h3>
              {s.country && (
                <Link href={'/search?q=' + encodeURIComponent(s.country)} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 12px', borderRadius: '10px', background: '#dbeafe', textDecoration: 'none', color: '#3b82f6', fontSize: '12px', fontWeight: '600', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}><Globe size={14} color="#3b82f6" />More from {s.country}</div>
                  <ChevronRight size={14} color="#3b82f6" />
                </Link>
              )}
              {s.degree_level && (
                <Link href={'/search?q=' + encodeURIComponent(s.degree_level.split(',')[0].trim())} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 12px', borderRadius: '10px', background: '#d1fae5', textDecoration: 'none', color: '#10b981', fontSize: '12px', fontWeight: '600', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}><GraduationCap size={14} color="#10b981" />More {s.degree_level.split(',')[0].trim()}</div>
                  <ChevronRight size={14} color="#10b981" />
                </Link>
              )}
              <Link href={isFullyFunded ? '/search?q=fully+funded' : '/search?q=partially+funded'} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 12px', borderRadius: '10px', background: '#fef3c7', textDecoration: 'none', color: '#f59e0b', fontSize: '12px', fontWeight: '600', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}><DollarSign size={14} color="#f59e0b" />{isFullyFunded ? 'More Fully Funded' : 'More Partial'}</div>
                <ChevronRight size={14} color="#f59e0b" />
              </Link>
              <Link href={noIelts ? '/search?q=no+ielts' : '/search?q=ielts+required'} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 12px', borderRadius: '10px', background: '#ede9fe', textDecoration: 'none', color: '#8b5cf6', fontSize: '12px', fontWeight: '600' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}><FileText size={14} color="#8b5cf6" />{noIelts ? 'No IELTS' : 'IELTS Required'}</div>
                <ChevronRight size={14} color="#8b5cf6" />
              </Link>
            </div>

            {/* SHARE BOX */}
            <div style={{ background: 'white', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '18px', textAlign: 'center' }}>
              <p style={{ fontSize: '13px', color: '#64748b', fontWeight: '500', marginBottom: '12px' }}>
                Know someone who needs this?
              </p>
              <button
                onClick={() => {
                  if (navigator.share) {
                    navigator.share({ title: s.title, url: window.location.href })
                  } else {
                    navigator.clipboard.writeText(window.location.href)
                    alert('Link copied!')
                  }
                }}
                style={{ width: '100%', padding: '10px', background: 'linear-gradient(135deg,#4f46e5,#7c3aed)', color: 'white', border: 'none', borderRadius: '10px', fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>
                Share This Scholarship
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* RECOMMENDATIONS */}
      {recommendations.length > 0 && (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px 60px' }}>
          <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: '40px' }}>
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#0f172a', marginBottom: '8px', letterSpacing: '-0.5px' }}>
                Similar Scholarships You May Like
              </h2>
              <p style={{ fontSize: '14px', color: '#64748b' }}>
                Based on {s.country || 'your interest'} • {s.degree_level || 'All levels'}
              </p>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
              {recommendations.map(rec => {
                const recFunded = rec.funding_type?.toLowerCase().includes('full')
                const recNoIelts = rec.ielts_score === 'Not required' || rec.ielts_score === 'Not mentioned'
                const matchColor = getMatchColor(rec.matchPercentage)
                const titleColor = getTitleColor(rec)
                return (
                  <Link key={rec.id} href={'/scholarship/' + rec.id} style={{ textDecoration: 'none' }}>
                    <div style={{ background: 'white', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '24px', transition: 'all 0.3s ease', cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '14px', height: '100%' }}
                      onMouseEnter={e => { e.currentTarget.style.border = '1px solid #c7d2fe'; e.currentTarget.style.boxShadow = '0 12px 40px rgba(79,70,229,0.15)'; e.currentTarget.style.transform = 'translateY(-4px)' }}
                      onMouseLeave={e => { e.currentTarget.style.border = '1px solid #f0f0f0'; e.currentTarget.style.boxShadow = 'none'; e.currentTarget.style.transform = 'translateY(0)' }}>

                      {hasUserProfile && (
                        <div style={{ background: matchColor.bg, color: matchColor.text, borderRadius: '12px', padding: '12px', textAlign: 'center' }}>
                          <div style={{ fontSize: '18px', marginBottom: '6px' }}>{getStarDisplay(rec.starRating)}</div>
                          <div style={{ fontSize: '14px', fontWeight: '800' }}>{rec.matchPercentage}% {matchColor.label}</div>
                        </div>
                      )}

                      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                        {recFunded && <span style={{ background: '#d1fae5', color: '#065f46', fontSize: '11px', fontWeight: '700', padding: '4px 10px', borderRadius: '100px' }}>Fully Funded</span>}
                        {recNoIelts && <span style={{ background: '#ccfbf1', color: '#115e59', fontSize: '11px', fontWeight: '700', padding: '4px 10px', borderRadius: '100px' }}>No IELTS</span>}
                        {rec.degree_level && <span style={{ background: '#e0e7ff', color: '#3730a3', fontSize: '11px', fontWeight: '700', padding: '4px 10px', borderRadius: '100px' }}>{rec.degree_level.split(',')[0].trim()}</span>}
                      </div>

                      <h3 style={{ fontSize: '15px', fontWeight: '800', color: titleColor, lineHeight: '1.4', margin: 0, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                        {rec.title}
                      </h3>

                      {rec.university_name && <div style={{ fontSize: '13px', color: '#64748b', fontWeight: '500' }}>{rec.university_name}</div>}

                      <p style={{ fontSize: '13px', color: '#64748b', lineHeight: '1.6', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden', flex: 1 }}>
                        {rec.seo_description || rec.full_description?.slice(0, 150) || (rec.blog_post ? rec.blog_post.replace(/<[^>]*>/g, '').slice(0, 150) : 'Click to view full scholarship details.')}
                      </p>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: 'auto' }}>
                        {rec.country && <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#475569', fontWeight: '500' }}><MapPin size={12} />{rec.country}</div>}
                        {rec.deadline && rec.deadline !== 'See official website' && <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#dc2626', fontWeight: '600' }}><Clock size={12} />{rec.deadline}</div>}
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '13px', fontWeight: '700', color: '#4f46e5', paddingTop: '12px', borderTop: '1px solid #f0f0f0' }}>
                        View Details <ChevronRight size={14} />
                      </div>
                    </div>
                  </Link>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* FOOTER */}
      <footer style={{ background: '#0f172a', color: 'white' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '48px 24px', textAlign: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg,#4f46e5,#7c3aed)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={18} color="white" />
            </div>
            <span style={{ fontSize: '18px', fontWeight: '800' }}>Admit<span style={{ color: '#818cf8' }}>Goal</span></span>
          </div>
          <p style={{ color: '#475569', fontSize: '13px', marginBottom: '20px' }}>Free AI scholarship finder for students worldwide</p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '24px' }}>
            {[['About', '/about'], ['Privacy', '/privacy'], ['Contact', '/contact']].map(([l, h]) => (
              <Link key={l} href={h} style={{ color: '#475569', fontSize: '13px', textDecoration: 'none' }}>{l}</Link>
            ))}
          </div>
          <p style={{ color: '#1e293b', fontSize: '12px', marginTop: '32px' }}>© {new Date().getFullYear()} AdmitGoal</p>
        </div>
      </footer>
    </div>
  )
}