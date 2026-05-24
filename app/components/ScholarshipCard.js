import Link from 'next/link'
import { MapPin, Clock, ChevronRight, Bell } from 'lucide-react'

export default function ScholarshipCard({ s }) {
  const isFullyFunded = s.funding_type?.toLowerCase().includes('full') || s.title?.toLowerCase().includes('fully funded')
  const noIelts = s.ielts_score === 'Not required' || s.ielts_score === 'Not mentioned'
  const isOpeningSoon = s.application_status === 'opening_soon'

  function getTitleColor() {
    const funding = (s.funding_type || '').toLowerCase()
    const title = (s.title || '').toLowerCase()
    if (funding.includes('full') || title.includes('fully funded')) return '#059669'
    else if (funding.includes('partial')) return '#f59e0b'
    else return '#4f46e5'
  }

  return (
    <Link href={`/scholarship/${s.id}`} style={{ textDecoration: 'none' }}>
      <div style={{
        background: 'white', borderRadius: '20px',
        border: '1px solid #f0f0f0', padding: '32px',      // ⬆️ 24px → 32px
        transition: 'all 0.2s', cursor: 'pointer',
        display: 'flex', flexDirection: 'column', height: '100%',
        position: 'relative',
        boxShadow: '0 4px 16px rgba(0,0,0,0.04)',           // ✅ subtle shadow
      }}
        onMouseEnter={e => {
          e.currentTarget.style.borderColor = '#c7d2fe'
          e.currentTarget.style.boxShadow = '0 20px 60px rgba(79,70,229,0.15)'
          e.currentTarget.style.transform = 'translateY(-4px)'
        }}
        onMouseLeave={e => {
          e.currentTarget.style.borderColor = '#f0f0f0'
          e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.04)'
          e.currentTarget.style.transform = 'translateY(0)'
        }}>

        {isOpeningSoon && (
          <div style={{
            position: 'absolute', top: '16px', right: '16px',
            background: 'linear-gradient(135deg, #f59e0b, #d97706)',
            color: 'white', padding: '7px 14px', borderRadius: '100px',
            fontSize: '12px', fontWeight: '700',
            display: 'flex', alignItems: 'center', gap: '5px',
            boxShadow: '0 4px 12px rgba(245,158,11,0.3)',
          }}>
            <Bell size={12} />
            Opening Soon
          </div>
        )}

        {/* TOP ROW — Country + Region */}
        <div style={{
          display: 'flex', justifyContent: 'space-between',
          alignItems: 'center', marginBottom: '18px',        // ⬆️ 14px → 18px
        }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            background: '#f0f4ff', color: '#4338ca',
            padding: '5px 12px', borderRadius: '100px',
            fontSize: '12px', fontWeight: '600',             // ⬆️ 11px → 12px
          }}>
            <MapPin size={11} />
            {s.country || 'International'}
          </div>
          <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: '500' }}>
            {s.region || ''}
          </span>
        </div>

        {/* TITLE */}
        <h3 style={{
          fontSize: '17px', fontWeight: '700',               // ⬆️ 15px → 17px
          color: getTitleColor(),
          lineHeight: '1.4', marginBottom: '14px',           // ⬆️ 12px → 14px
          display: '-webkit-box', WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical', overflow: 'hidden',
          minHeight: '48px',                                  // ✅ consistent height
        }}>
          {s.seo_title || s.title}
        </h3>

        {/* BADGES */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '7px', marginBottom: '16px' }}> {/* ⬆️ gap 6→7, mb 14→16 */}
          {s.degree_level && s.degree_level !== 'Not specified' && (
            <span style={{
              fontSize: '12px', fontWeight: '600',           // ⬆️ 11px → 12px
              background: '#eff6ff', color: '#1d4ed8',
              padding: '4px 12px', borderRadius: '100px',   // ⬆️ padding slightly bigger
            }}>
              {s.degree_level.slice(0, 25)}
            </span>
          )}
          {isFullyFunded && (
            <span style={{
              fontSize: '12px', fontWeight: '600',
              background: '#f0fdf4', color: '#15803d',
              padding: '4px 12px', borderRadius: '100px',
            }}>
              Fully Funded
            </span>
          )}
          {noIelts && (
            <span style={{
              fontSize: '12px', fontWeight: '600',
              background: '#f0fdfa', color: '#0f766e',
              padding: '4px 12px', borderRadius: '100px',
            }}>
              No IELTS
            </span>
          )}
          {!noIelts && s.ielts_score && s.ielts_score !== 'Check website' && (
            <span style={{
              fontSize: '12px', fontWeight: '600',
              background: '#fff7ed', color: '#c2410c',
              padding: '4px 12px', borderRadius: '100px',
            }}>
              IELTS {s.ielts_score}
            </span>
          )}
        </div>

        {/* DESCRIPTION */}
        <p style={{
          fontSize: '14px', color: '#64748b', lineHeight: '1.7', // ⬆️ 13px → 14px
          marginBottom: '18px', flex: 1,
          display: '-webkit-box', WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical', overflow: 'hidden',
        }}>
          {s.seo_description || s.full_description || 'Click to view full scholarship details and requirements.'}
        </p>

        {/* DEADLINE */}
        {s.deadline && s.deadline !== 'See official website' && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '7px',
            background: isOpeningSoon ? '#fef3c7' : '#fef2f2',
            color: isOpeningSoon ? '#92400e' : '#dc2626',
            padding: '9px 14px', borderRadius: '10px',      // ⬆️ padding bigger
            fontSize: '13px', fontWeight: '600',             // ⬆️ 12px → 13px
            marginBottom: '18px',                            // ⬆️ 14px → 18px
          }}>
            <Clock size={13} />
            {isOpeningSoon ? `Opens: ${s.deadline}` : `Deadline: ${s.deadline}`}
          </div>
        )}

        {/* FOOTER ROW */}
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          paddingTop: '16px', borderTop: '1px solid #f1f5f9', // ⬆️ 14px → 16px
        }}>
          <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: '500' }}>
            {s.university_name?.slice(0, 30) || 'University'}
          </span>
          <span style={{
            display: 'flex', alignItems: 'center', gap: '5px',
            fontSize: '13px', fontWeight: '700', color: '#4f46e5', // ⬆️ 12px → 13px
          }}>
            View Guide <ChevronRight size={15} />
          </span>
        </div>
      </div>
    </Link>
  )
}