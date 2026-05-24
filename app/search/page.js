'use client'
import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { supabase } from '../../lib/supabase'
import Link from 'next/link'
import { Search, MapPin, Clock, ChevronRight, GraduationCap, ArrowLeft } from 'lucide-react'

function SearchResults() {
  const searchParams = useSearchParams()
  const q = searchParams.get('q') || ''
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState(q)

  useEffect(() => { if (q) fetchResults(q) }, [q])

  async function fetchResults(query) {
    setLoading(true)
    const { data } = await supabase
      .from('scholarship_details')
      .select('*')
      .or(`title.ilike.%${query}%,seo_description.ilike.%${query}%,country.ilike.%${query}%,region.ilike.%${query}%,degree_level.ilike.%${query}%,funding_type.ilike.%${query}%,university_name.ilike.%${query}%`)
      .order('id', { ascending: false })
      .limit(500)
    setResults(data || [])
    setLoading(false)
  }

  return (
    <div style={{ minHeight: '100vh', background: '#fafafa', fontFamily: "'Inter', -apple-system, sans-serif" }}>
      <nav style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(20px)', borderBottom: '1px solid #f0f0f0', height: '60px', display: 'flex', alignItems: 'center' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
            <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={18} color="white" />
            </div>
            <span style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.5px' }}>Admit<span style={{ color: '#4f46e5' }}>Goal</span></span>
          </Link>
          <form onSubmit={e => { e.preventDefault(); window.location.href = `/search?q=${encodeURIComponent(search)}` }}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#f8fafc', border: '1px solid #f0f0f0', borderRadius: '10px', padding: '8px 16px', width: '320px' }}>
            <Search size={14} color="#94a3b8" />
            <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search scholarships..."
              style={{ flex: 1, border: 'none', background: 'transparent', outline: 'none', fontSize: '13px', color: '#0f172a', fontFamily: 'inherit' }} />
          </form>
        </div>
      </nav>

      <div style={{ paddingTop: '96px', maxWidth: '1200px', margin: '0 auto', padding: '96px 24px 60px' }}>
        <Link href="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#94a3b8', fontSize: '13px', textDecoration: 'none', marginBottom: '32px' }}>
          <ArrowLeft size={14} /> Back to all scholarships
        </Link>
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: '800', color: '#0f172a', letterSpacing: '-1px', marginBottom: '8px' }}>
            Results for <span style={{ color: '#4f46e5' }}>"{q}"</span>
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '14px' }}>{loading ? 'Searching...' : `${results.length} scholarships found`}</p>
        </div>

        {loading ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
            {[...Array(6)].map((_, i) => (
              <div key={i} style={{ background: 'white', borderRadius: '16px', padding: '24px', border: '1px solid #f0f0f0' }}>
                <div style={{ height: '12px', background: '#f1f5f9', borderRadius: '6px', width: '40%', marginBottom: '16px' }} />
                <div style={{ height: '20px', background: '#f1f5f9', borderRadius: '6px', marginBottom: '12px' }} />
              </div>
            ))}
          </div>
        ) : results.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
            {results.map(s => (
              <Link key={s.id} href={`/scholarship/${s.id}`} style={{ textDecoration: 'none' }}>
                <div style={{ background: 'white', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '24px', transition: 'all 0.2s', height: '100%', display: 'flex', flexDirection: 'column' }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = '#c7d2fe'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(79,70,229,0.08)'; e.currentTarget.style.transform = 'translateY(-2px)' }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = '#f0f0f0'; e.currentTarget.style.boxShadow = 'none'; e.currentTarget.style.transform = 'translateY(0)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', background: '#f0f4ff', color: '#4338ca', padding: '4px 10px', borderRadius: '100px', fontSize: '11px', fontWeight: '600', marginBottom: '12px', width: 'fit-content' }}>
                    <MapPin size={10} />{s.country || 'International'}
                  </div>
                  <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#0f172a', lineHeight: '1.4', marginBottom: '10px', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {s.title}
                  </h3>
                  <p style={{ fontSize: '13px', color: '#64748b', lineHeight: '1.65', flex: 1, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {s.seo_description || 'Click to view full details.'}
                  </p>
                  {s.deadline && s.deadline !== 'See official website' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#fef2f2', color: '#dc2626', padding: '7px 12px', borderRadius: '8px', fontSize: '12px', fontWeight: '600', marginTop: '14px' }}>
                      <Clock size={12} />Deadline: {s.deadline}
                    </div>
                  )}
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '14px', paddingTop: '14px', borderTop: '1px solid #fafafa' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', fontWeight: '700', color: '#4f46e5' }}>View Guide <ChevronRight size={14} /></span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '80px 20px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
            <h3 style={{ fontSize: '22px', fontWeight: '700', color: '#0f172a', marginBottom: '8px' }}>No results for "{q}"</h3>
            <p style={{ color: '#64748b', marginBottom: '24px' }}>Try a country name, degree level, or scholarship type</p>
            <Link href="/" style={{ padding: '12px 24px', background: '#4f46e5', color: 'white', borderRadius: '12px', textDecoration: 'none', fontWeight: '600', fontSize: '14px' }}>Browse All Scholarships</Link>
          </div>
        )}
      </div>
    </div>
  )
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fafafa', color: '#4f46e5', fontWeight: '600', fontFamily: 'Inter, sans-serif' }}>Loading...</div>}>
      <SearchResults />
    </Suspense>
  )
}