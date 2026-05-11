'use client'
import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import Link from 'next/link'
import { Search, MapPin, Clock, ChevronRight, GraduationCap, Filter, ArrowRight } from 'lucide-react'

export default function Home() {
  const [scholarships, setScholarships] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [activeLevel, setActiveLevel] = useState('')
  const [activeRegion, setActiveRegion] = useState('')
  const [activeFunding, setActiveFunding] = useState('')

  useEffect(() => {
    fetchScholarships()
  }, [activeLevel, activeRegion, activeFunding])

  async function fetchScholarships() {
    setLoading(true)
    let query = supabase
      .from('scholarship_details')
      .select('*')
      .order('id', { ascending: false })
      .limit(200)

    if (activeLevel) query = query.ilike('degree_level', `%${activeLevel}%`)
    if (activeRegion) query = query.ilike('region', `%${activeRegion}%`)
    if (activeFunding) query = query.ilike('funding_type', `%${activeFunding}%`)

    const { data, error } = await query
    if (error) console.error(error)
    if (data) setScholarships(data)

    const { count } = await supabase
      .from('scholarship_details')
      .select('*', { count: 'exact', head: true })
    if (count !== null) setTotal(count)
    setLoading(false)
  }

  function handleSearch(e) {
    e.preventDefault()
    if (search.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(search)}`
    }
  }

  const regions = ['Europe', 'Asia', 'Middle East', 'Oceania', 'North America', 'Africa']
  const popularSearches = ['Germany', 'China', 'Turkey', 'South Korea', 'Fully Funded', 'No IELTS', 'PhD', 'Masters']

  return (
    <div className="min-h-screen" style={{ background: '#fafafa', fontFamily: "'Inter', -apple-system, sans-serif" }}>

      {/* NAVBAR */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(20px)',
        borderBottom: '1px solid #f0f0f0', height: '60px',
        display: 'flex', alignItems: 'center',
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
            <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={18} color="white" />
            </div>
            <span style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.5px' }}>
              Admit<span style={{ color: '#4f46e5' }}>Goal</span>
            </span>
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            {['Fully Funded', 'No IELTS', 'PhD'].map(item => (
              <Link key={item} href={`/search?q=${item}`} style={{
                padding: '7px 14px', borderRadius: '8px', fontSize: '13px',
                fontWeight: '500', color: '#475569', textDecoration: 'none',
                transition: 'all 0.15s',
              }}
                onMouseEnter={e => { e.target.style.background = '#f1f5f9'; e.target.style.color = '#4f46e5' }}
                onMouseLeave={e => { e.target.style.background = 'transparent'; e.target.style.color = '#475569' }}>
                {item}
              </Link>
            ))}
            <Link href="/about" style={{ padding: '7px 14px', borderRadius: '8px', fontSize: '13px', fontWeight: '500', color: '#475569', textDecoration: 'none' }}>About</Link>
            <Link href="/contact" style={{
              marginLeft: '8px', padding: '8px 18px', background: '#4f46e5',
              color: 'white', borderRadius: '10px', fontSize: '13px',
              fontWeight: '600', textDecoration: 'none',
            }}>Get Help</Link>
          </div>
        </div>
      </nav>

      {/* HERO */}
      <section style={{
        paddingTop: '120px', paddingBottom: '80px', textAlign: 'center',
        background: 'linear-gradient(180deg, #ffffff 0%, #f8f7ff 100%)',
        borderBottom: '1px solid #f0f0f0',
      }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '0 24px' }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '8px',
            background: '#ede9fe', color: '#5b21b6',
            padding: '6px 16px', borderRadius: '100px',
            fontSize: '12px', fontWeight: '600',
            letterSpacing: '0.3px', marginBottom: '32px',
            textTransform: 'uppercase',
          }}>
            Updated Every 6 Hours
          </div>
          <h1 style={{
            fontSize: 'clamp(40px, 6vw, 72px)', fontWeight: '900',
            color: '#0f172a', lineHeight: '1.05',
            letterSpacing: '-2px', marginBottom: '20px',
          }}>
            Find Your Dream
            <span style={{
              display: 'block',
              background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            }}>Scholarship</span>
          </h1>
          <p style={{
            fontSize: '18px', color: '#64748b', lineHeight: '1.7',
            maxWidth: '560px', margin: '0 auto 40px', fontWeight: '400',
          }}>
            No agent fees. No hidden costs. Our AI finds scholarships from universities across 50+ countries and guides you through every step of the application.
          </p>

          {/* SEARCH BAR */}
          <form onSubmit={handleSearch} style={{ maxWidth: '600px', margin: '0 auto 24px' }}>
            <div style={{
              display: 'flex', background: 'white',
              border: '1.5px solid #e2e8f0', borderRadius: '16px',
              padding: '6px', boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
            }}>
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '12px', padding: '0 16px' }}>
                <Search size={18} color="#94a3b8" />
                <input
                  type="text"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Search by country, university, or field..."
                  style={{
                    flex: 1, border: 'none', outline: 'none', fontSize: '15px',
                    color: '#0f172a', background: 'transparent',
                    fontFamily: 'inherit',
                  }}
                />
              </div>
              <button type="submit" style={{
                padding: '12px 24px',
                background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
                color: 'white', border: 'none', borderRadius: '12px',
                fontSize: '14px', fontWeight: '600', cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: '6px',
              }}>
                Search <ArrowRight size={16} />
              </button>
            </div>
          </form>

          {/* POPULAR SEARCHES */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center' }}>
            {popularSearches.map(q => (
              <Link key={q} href={`/search?q=${encodeURIComponent(q)}`} style={{
                padding: '7px 16px', background: 'white',
                border: '1.5px solid #e2e8f0', borderRadius: '100px',
                fontSize: '13px', fontWeight: '500', color: '#475569',
                textDecoration: 'none', transition: 'all 0.15s',
              }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = '#4f46e5'; e.currentTarget.style.color = '#4f46e5' }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.color = '#475569' }}>
                {q}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* STATS */}
      <div style={{ background: 'white', borderBottom: '1px solid #f0f0f0' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)' }}>
          {[
            { num: `${total}+`, label: 'Live Scholarships' },
            { num: '50+', label: 'Countries Covered' },
            { num: '100%', label: 'Free Forever' },
            { num: 'AI', label: 'Powered Guidance' },
          ].map(s => (
            <div key={s.label} style={{ textAlign: 'center', padding: '28px 20px', borderRight: '1px solid #f0f0f0' }}>
              <div style={{ fontSize: '32px', fontWeight: '800', color: '#4f46e5', letterSpacing: '-1px' }}>{s.num}</div>
              <div style={{ fontSize: '13px', color: '#94a3b8', fontWeight: '500', marginTop: '4px' }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '48px 24px' }}>

        {/* REGION FILTER */}
        <div style={{ marginBottom: '32px' }}>
          <p style={{ fontSize: '12px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '12px' }}>Browse by Region</p>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {regions.map(r => (
              <button key={r} onClick={() => setActiveRegion(activeRegion === r ? '' : r)} style={{
                padding: '8px 18px', borderRadius: '100px', fontSize: '13px',
                fontWeight: '500', cursor: 'pointer', transition: 'all 0.15s',
                border: activeRegion === r ? '1.5px solid #4f46e5' : '1.5px solid #e2e8f0',
                background: activeRegion === r ? '#4f46e5' : 'white',
                color: activeRegion === r ? 'white' : '#475569',
              }}>
                {r}
              </button>
            ))}
          </div>
        </div>

        {/* LEVEL + FUNDING FILTER */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '36px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginRight: '8px' }}>
            <Filter size={14} color="#94a3b8" />
            <span style={{ fontSize: '12px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px' }}>Filter</span>
          </div>
          {['Bachelor', 'Master', 'PhD'].map(l => (
            <button key={l} onClick={() => setActiveLevel(activeLevel === l ? '' : l)} style={{
              padding: '7px 16px', borderRadius: '100px', fontSize: '13px',
              fontWeight: '500', cursor: 'pointer', transition: 'all 0.15s',
              border: activeLevel === l ? '1.5px solid #4f46e5' : '1.5px solid #e2e8f0',
              background: activeLevel === l ? '#4f46e5' : 'white',
              color: activeLevel === l ? 'white' : '#475569',
            }}>
              {l}
            </button>
          ))}
          <button onClick={() => setActiveFunding(activeFunding === 'Fully Funded' ? '' : 'Fully Funded')} style={{
            padding: '7px 16px', borderRadius: '100px', fontSize: '13px',
            fontWeight: '500', cursor: 'pointer', transition: 'all 0.15s',
            border: activeFunding ? '1.5px solid #4f46e5' : '1.5px solid #e2e8f0',
            background: activeFunding ? '#4f46e5' : 'white',
            color: activeFunding ? 'white' : '#475569',
          }}>
            Fully Funded
          </button>
          {(activeLevel || activeRegion || activeFunding) && (
            <button onClick={() => { setActiveLevel(''); setActiveRegion(''); setActiveFunding('') }} style={{
              padding: '7px 16px', borderRadius: '100px', fontSize: '13px',
              fontWeight: '500', cursor: 'pointer', border: '1.5px solid #fee2e2',
              background: 'white', color: '#ef4444',
            }}>
              Clear all
            </button>
          )}
        </div>

        {/* HEADER */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#0f172a', letterSpacing: '-0.5px' }}>
            {loading ? 'Loading scholarships...' : `${scholarships.length} Scholarships`}
          </h2>
        </div>

        {/* GRID */}
        {loading ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
            {[...Array(6)].map((_, i) => (
              <div key={i} style={{ background: 'white', borderRadius: '16px', padding: '24px', border: '1px solid #f0f0f0', animation: 'pulse 1.5s infinite' }}>
                <div style={{ height: '12px', background: '#f1f5f9', borderRadius: '6px', width: '40%', marginBottom: '16px' }} />
                <div style={{ height: '20px', background: '#f1f5f9', borderRadius: '6px', marginBottom: '12px' }} />
                <div style={{ height: '12px', background: '#f1f5f9', borderRadius: '6px', width: '70%' }} />
              </div>
            ))}
          </div>
        ) : scholarships.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '80px 20px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
            <h3 style={{ fontSize: '20px', fontWeight: '700', color: '#0f172a', marginBottom: '8px' }}>No scholarships found</h3>
            <p style={{ color: '#64748b', fontSize: '14px' }}>Try adjusting your filters</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
            {scholarships.map(s => <ScholarshipCard key={s.id} s={s} />)}
          </div>
        )}
      </div>

      {/* FOOTER */}
      <footer style={{ background: '#0f172a', color: 'white', marginTop: '80px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '60px 24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '48px', marginBottom: '48px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <GraduationCap size={18} color="white" />
                </div>
                <span style={{ fontSize: '18px', fontWeight: '800', letterSpacing: '-0.5px' }}>
                  Admit<span style={{ color: '#818cf8' }}>Goal</span>
                </span>
              </div>
              <p style={{ color: '#64748b', fontSize: '14px', lineHeight: '1.7', maxWidth: '280px' }}>
                Helping students from Pakistan, India, Bangladesh and Africa find life-changing scholarships without paying agents.
              </p>
            </div>
            <div>
              <p style={{ fontSize: '12px', fontWeight: '700', color: '#475569', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '16px' }}>Explore</p>
              {['Fully Funded', 'No IELTS', 'PhD', 'Masters', 'Germany', 'China', 'Turkey', 'Korea'].map(l => (
                <Link key={l} href={`/search?q=${l}`} style={{ display: 'block', color: '#64748b', fontSize: '14px', marginBottom: '10px', textDecoration: 'none' }}>{l}</Link>
              ))}
            </div>
            <div>
              <p style={{ fontSize: '12px', fontWeight: '700', color: '#475569', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '16px' }}>Company</p>
              {[['About', '/about'], ['Contact', '/contact'], ['Privacy Policy', '/privacy'], ['Sitemap', '/sitemap.xml']].map(([l, h]) => (
                <Link key={l} href={h} style={{ display: 'block', color: '#64748b', fontSize: '14px', marginBottom: '10px', textDecoration: 'none' }}>{l}</Link>
              ))}
            </div>
          </div>
          <div style={{ borderTop: '1px solid #1e293b', paddingTop: '24px', textAlign: 'center' }}>
            <p style={{ color: '#334155', fontSize: '13px' }}>
              © {new Date().getFullYear()} AdmitGoal · Replacing agents with AI · Built for students worldwide
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function ScholarshipCard({ s }) {
  const isFullyFunded = s.funding_type?.toLowerCase().includes('full') || s.title?.toLowerCase().includes('fully funded')
  const noIelts = s.ielts_score === 'Not required' || s.ielts_score === 'Not mentioned'

  return (
    <Link href={`/scholarship/${s.id}`} style={{ textDecoration: 'none' }}>
      <div style={{
        background: 'white', borderRadius: '16px',
        border: '1px solid #f0f0f0', padding: '24px',
        transition: 'all 0.2s', cursor: 'pointer',
        display: 'flex', flexDirection: 'column', height: '100%',
      }}
        onMouseEnter={e => {
          e.currentTarget.style.borderColor = '#c7d2fe'
          e.currentTarget.style.boxShadow = '0 12px 40px rgba(79,70,229,0.08)'
          e.currentTarget.style.transform = 'translateY(-3px)'
        }}
        onMouseLeave={e => {
          e.currentTarget.style.borderColor = '#f0f0f0'
          e.currentTarget.style.boxShadow = 'none'
          e.currentTarget.style.transform = 'translateY(0)'
        }}>

        {/* TOP */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', background: '#f0f4ff', color: '#4338ca', padding: '4px 10px', borderRadius: '100px', fontSize: '11px', fontWeight: '600' }}>
            <MapPin size={10} />
            {s.country || 'International'}
          </div>
          <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: '500' }}>{s.region || ''}</span>
        </div>

        {/* TITLE */}
        <h3 style={{
          fontSize: '15px', fontWeight: '700', color: '#0f172a',
          lineHeight: '1.4', marginBottom: '12px',
          display: '-webkit-box', WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical', overflow: 'hidden',
        }}>
          {s.seo_title || s.title}
        </h3>

        {/* BADGES */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '14px' }}>
          {s.degree_level && s.degree_level !== 'Not specified' && (
            <span style={{ fontSize: '11px', fontWeight: '600', background: '#eff6ff', color: '#1d4ed8', padding: '3px 10px', borderRadius: '100px' }}>
              {s.degree_level.slice(0, 25)}
            </span>
          )}
          {isFullyFunded && (
            <span style={{ fontSize: '11px', fontWeight: '600', background: '#f0fdf4', color: '#15803d', padding: '3px 10px', borderRadius: '100px' }}>
              Fully Funded
            </span>
          )}
          {noIelts && (
            <span style={{ fontSize: '11px', fontWeight: '600', background: '#f0fdfa', color: '#0f766e', padding: '3px 10px', borderRadius: '100px' }}>
              No IELTS
            </span>
          )}
          {!noIelts && s.ielts_score && s.ielts_score !== 'Check website' && (
            <span style={{ fontSize: '11px', fontWeight: '600', background: '#fff7ed', color: '#c2410c', padding: '3px 10px', borderRadius: '100px' }}>
              IELTS {s.ielts_score}
            </span>
          )}
        </div>

        {/* DESCRIPTION */}
        <p style={{
          fontSize: '13px', color: '#64748b', lineHeight: '1.65',
          marginBottom: '16px', flex: 1,
          display: '-webkit-box', WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical', overflow: 'hidden',
        }}>
          {s.seo_description || s.full_description || 'Click to view full scholarship details and requirements.'}
        </p>

        {/* DEADLINE */}
        {s.deadline && s.deadline !== 'See official website' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#fef2f2', color: '#dc2626', padding: '7px 12px', borderRadius: '8px', fontSize: '12px', fontWeight: '600', marginBottom: '14px' }}>
            <Clock size={12} />
            Deadline: {s.deadline}
          </div>
        )}

        {/* FOOTER */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '14px', borderTop: '1px solid #f8fafc' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: '500' }}>
            {s.university_name?.slice(0, 30) || 'University'}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', fontWeight: '700', color: '#4f46e5' }}>
            View Guide <ChevronRight size={14} />
          </span>
        </div>
      </div>
    </Link>
  )
}