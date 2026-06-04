'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { MapPin, Clock, ChevronRight, Bell, Bookmark, Sparkles } from 'lucide-react'
import { getUser } from '@/lib/supabase-auth'
import { supabase } from '@/lib/supabase'

export default function ScholarshipCard({ s, matchPercentage, matchReasons }) {
  const [user, setUser] = useState(null)
  const [isSaved, setIsSaved] = useState(false)
  const [saving, setSaving] = useState(false)

  const isFullyFunded = s.funding_type?.toLowerCase().includes('full') || s.title?.toLowerCase().includes('fully funded')
  const noIelts = s.ielts_score === 'Not required' || s.ielts_score === 'Not mentioned'
  const isOpeningSoon = s.application_status === 'opening_soon'

  // Match badge color
  function getMatchStyle(pct) {
    if (pct >= 80) return { bg: 'linear-gradient(135deg, #059669, #10b981)', label: `${pct}% Match` }
    if (pct >= 60) return { bg: 'linear-gradient(135deg, #0891b2, #06b6d4)', label: `${pct}% Match` }
    if (pct >= 40) return { bg: 'linear-gradient(135deg, #f59e0b, #fbbf24)', label: `${pct}% Match` }
    return { bg: 'linear-gradient(135deg, #6366f1, #8b5cf6)', label: `${pct}% Match` }
  }

  const showMatch = matchPercentage > 0
  const matchStyle = showMatch ? getMatchStyle(matchPercentage) : null

  useEffect(() => {
    async function checkSaved() {
      const currentUser = await getUser()
      if (currentUser) {
        setUser(currentUser)
        const { data } = await supabase
          .from('user_saved_scholarships')
          .select('id')
          .eq('user_id', currentUser.id)
          .eq('scholarship_id', s.id)
          .single()
        setIsSaved(!!data)
      }
    }
    checkSaved()
  }, [s.id])

  async function handleSave(e) {
    e.preventDefault()
    e.stopPropagation()
    if (!user) { alert('Please login to save scholarships'); return }
    setSaving(true)

    if (isSaved) {
      const { error } = await supabase
        .from('user_saved_scholarships')
        .delete()
        .eq('user_id', user.id)
        .eq('scholarship_id', s.id)
      if (!error) setIsSaved(false)
    } else {
      const { error } = await supabase
        .from('user_saved_scholarships')
        .insert([{ user_id: user.id, scholarship_id: s.id }])
      if (!error) setIsSaved(true)
    }
    setSaving(false)
  }

  function getTitleColor() {
    const funding = (s.funding_type || '').toLowerCase()
    const title = (s.title || '').toLowerCase()
    if (funding.includes('full') || title.includes('fully funded')) return '#059669'
    else if (funding.includes('partial')) return '#f59e0b'
    else return '#4f46e5'
  }

  return (
    <Link href={`/scholarship/${s.id}`} style={{ textDecoration: 'none' }}>
      <div
        style={{
          background: 'white',
          borderRadius: '20px',
          border: showMatch && matchPercentage >= 80
            ? '1.5px solid rgba(5,150,105,0.25)'
            : '1px solid #f0f0f0',
          padding: '32px',
          transition: 'all 0.2s',
          cursor: 'pointer',
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          position: 'relative',
          boxShadow: showMatch && matchPercentage >= 80
            ? '0 4px 20px rgba(5,150,105,0.08)'
            : '0 4px 16px rgba(0,0,0,0.04)',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.borderColor = '#c7d2fe'
          e.currentTarget.style.boxShadow = '0 20px 60px rgba(79,70,229,0.15)'
          e.currentTarget.style.transform = 'translateY(-4px)'
        }}
        onMouseLeave={e => {
          e.currentTarget.style.borderColor = showMatch && matchPercentage >= 80 ? 'rgba(5,150,105,0.25)' : '#f0f0f0'
          e.currentTarget.style.boxShadow = showMatch && matchPercentage >= 80 ? '0 4px 20px rgba(5,150,105,0.08)' : '0 4px 16px rgba(0,0,0,0.04)'
          e.currentTarget.style.transform = 'translateY(0)'
        }}
      >

        {/* TOP RIGHT: Match badge OR Opening Soon */}
        <div style={{ position: 'absolute', top: '16px', right: '16px', display: 'flex', alignItems: 'center', gap: '8px', zIndex: 10 }}>

          {/* Match % Badge */}
          {showMatch && (
            <div style={{
              background: matchStyle.bg,
              color: 'white',
              padding: '5px 12px',
              borderRadius: '100px',
              fontSize: '11px',
              fontWeight: '800',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
              letterSpacing: '0.3px',
            }}>
              <Sparkles size={10} />
              {matchStyle.label}
            </div>
          )}

          {isOpeningSoon && !showMatch && (
            <div style={{
              background: 'linear-gradient(135deg, #f59e0b, #d97706)',
              color: 'white', padding: '7px 14px', borderRadius: '100px',
              fontSize: '12px', fontWeight: '700',
              display: 'flex', alignItems: 'center', gap: '5px',
              boxShadow: '0 4px 12px rgba(245,158,11,0.3)',
            }}>
              <Bell size={12} /> Opening Soon
            </div>
          )}
        </div>

        {/* Save button */}
        {user && (
          <button
            onClick={handleSave}
            disabled={saving}
            style={{
              position: 'absolute',
              top: showMatch ? '48px' : '16px',
              right: '16px',
              background: isSaved ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.9)',
              border: isSaved ? 'none' : '1px solid #e2e8f0',
              color: isSaved ? 'white' : '#64748b',
              padding: '8px',
              borderRadius: '10px',
              cursor: saving ? 'not-allowed' : 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'all 0.2s',
              boxShadow: isSaved ? '0 4px 12px rgba(99,102,241,0.3)' : '0 2px 8px rgba(0,0,0,0.08)',
              zIndex: 10,
            }}
            onMouseEnter={e => { if (!saving) e.currentTarget.style.transform = 'scale(1.1)' }}
            onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)' }}
          >
            <Bookmark size={16} fill={isSaved ? 'white' : 'none'} strokeWidth={2.5} />
          </button>
        )}

        {/* TOP ROW - Country + Region */}
        <div style={{
          display: 'flex', justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '18px',
          marginTop: showMatch ? '28px' : '0',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#f0f4ff', color: '#4338ca', padding: '5px 12px', borderRadius: '100px', fontSize: '12px', fontWeight: '600' }}>
            <MapPin size={11} />
            {s.country || 'International'}
          </div>
          <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: '500' }}>
            {s.region || ''}
          </span>
        </div>

        {/* TITLE */}
        <h3 style={{
          fontSize: '17px', fontWeight: '700',
          color: getTitleColor(),
          lineHeight: '1.4', marginBottom: '14px',
          display: '-webkit-box', WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical', overflow: 'hidden',
          minHeight: '48px',
        }}>
          {s.seo_title || s.title}
        </h3>

        {/* UNIVERSITY */}
        {s.university_name && (
          <div style={{ fontSize: '13px', color: '#64748b', marginBottom: '16px', fontWeight: '500' }}>
            {s.university_name}
          </div>
        )}

        {/* BADGES */}
        <div style={{ display: 'flex', gap: '7px', flexWrap: 'wrap', marginBottom: '18px' }}>
          {isFullyFunded && (
            <span style={{ background: '#d1fae5', color: '#065f46', fontSize: '11px', fontWeight: '700', padding: '5px 12px', borderRadius: '100px' }}>
              Fully Funded
            </span>
          )}
          {noIelts && (
            <span style={{ background: '#ccfbf1', color: '#115e59', fontSize: '11px', fontWeight: '700', padding: '5px 12px', borderRadius: '100px' }}>
              No IELTS
            </span>
          )}
          {s.degree_level && (
            <span style={{ background: '#e0e7ff', color: '#3730a3', fontSize: '11px', fontWeight: '700', padding: '5px 12px', borderRadius: '100px' }}>
              {s.degree_level.split(',')[0].trim()}
            </span>
          )}
        </div>

        {/* MATCH REASONS - only show top 2 */}
        {showMatch && matchReasons?.length > 0 && (
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '14px' }}>
            {matchReasons.slice(0, 2).map((reason, i) => (
              <span key={i} style={{
                background: 'rgba(99,102,241,0.08)',
                color: '#6366f1',
                fontSize: '11px',
                fontWeight: '600',
                padding: '4px 10px',
                borderRadius: '100px',
                border: '1px solid rgba(99,102,241,0.15)',
              }}>
                ✓ {reason}
              </span>
            ))}
          </div>
        )}

        {/* DESCRIPTION */}
        <p style={{
          fontSize: '13px', color: '#64748b', lineHeight: '1.7',
          display: '-webkit-box', WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical', overflow: 'hidden',
          marginBottom: '20px', flex: 1,
        }}>
          {s.seo_description || s.full_description?.slice(0, 150) || (s.blog_post ? s.blog_post.replace(/<[^>]*>/g, '').slice(0, 150) : 'Click to view full scholarship details.')}
        </p>

        {/* DEADLINE */}
        {s.deadline && s.deadline !== 'See official website' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '7px', fontSize: '13px', color: '#dc2626', fontWeight: '600', marginBottom: '20px' }}>
            <Clock size={14} color="#dc2626" strokeWidth={2.5} />
            Deadline: {s.deadline}
          </div>
        )}

        {/* FOOTER */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '18px', borderTop: '1px solid #f8fafc', marginTop: 'auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', fontWeight: '700', color: '#4f46e5' }}>
            View Details <ChevronRight size={16} strokeWidth={2.5} />
          </div>
          {showMatch && matchPercentage >= 80 && (
            <span style={{ fontSize: '11px', fontWeight: '700', color: '#059669' }}>
              ⭐ Top Match
            </span>
          )}
        </div>
      </div>
    </Link>
  )
}