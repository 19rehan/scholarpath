'use client'
import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import Link from 'next/link'
import { Search, Sparkles, Globe2, TrendingUp, Zap, ArrowRight, GraduationCap, X, ChevronRight, Filter } from 'lucide-react'
import ScholarshipCard from './components/ScholarshipCard'
import Pagination from './components/Pagination'

const PER_PAGE = 50

export default function Home() {
  const [scholarships, setScholarships] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [activeLevel, setActiveLevel] = useState('')
  const [activeRegion, setActiveRegion] = useState('')
  const [activeFunding, setActiveFunding] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [showProfilePopup, setShowProfilePopup] = useState(false)

  useEffect(() => {
    fetchScholarships()
  }, [activeLevel, activeRegion, activeFunding, currentPage])

  useEffect(() => {
    const hasProfile = localStorage.getItem('admitgoal_has_profile')
    if (!hasProfile) {
      setTimeout(() => setShowProfilePopup(true), 8000)
    }
  }, [])

  async function fetchScholarships() {
    setLoading(true)
    const from = (currentPage - 1) * PER_PAGE
    const to = from + PER_PAGE - 1

    let query = supabase
      .from('scholarship_details')
      .select('*', { count: 'exact' })
      .order('id', { ascending: false })
      .range(from, to)

    if (activeLevel) query = query.ilike('degree_level', `%${activeLevel}%`)
    if (activeRegion) query = query.ilike('region', `%${activeRegion}%`)
    if (activeFunding) query = query.ilike('funding_type', `%${activeFunding}%`)

    const { data, error, count } = await query
    if (error) console.error(error)
    if (data) setScholarships(data)
    if (count !== null) setTotal(count)
    setLoading(false)
  }

  function handleSearch(e) {
    e.preventDefault()
    if (search.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(search)}`
    }
  }

  function handlePageChange(page) {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function closePopup() {
    setShowProfilePopup(false)
  }

  function handleFilterClick(type, value) {
    if (type === 'region') {
      setActiveRegion(activeRegion === value ? '' : value)
    } else if (type === 'level') {
      setActiveLevel(activeLevel === value ? '' : value)
    } else if (type === 'funding') {
      setActiveFunding(activeFunding === value ? '' : value)
    }
    setCurrentPage(1)
  }

  const regions = ['Europe', 'Asia', 'Middle East', 'Oceania', 'North America', 'Africa']
  const totalPages = Math.ceil(total / PER_PAGE)
  const hasActiveFilter = activeLevel || activeRegion || activeFunding

  return (
    <>
      <style jsx global>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(5deg); }
        }
        @keyframes popupIn {
          from { opacity: 0; transform: scale(0.92) translateY(20px); }
          to { opacity: 1; transform: scale(1) translateY(0); }
        }
        .animate-in {
          animation: fadeInUp 0.6s ease-out forwards;
        }
        .card-hover {
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .card-hover:hover {
          transform: translateY(-8px) scale(1.02);
        }
        .filter-btn {
          transition: all 0.2s ease;
        }
        .filter-btn:hover {
          transform: translateY(-2px);
        }
        .logo-float {
          animation: float 6s ease-in-out infinite;
          will-change: transform;
        }
      `}</style>

      <div style={{ minHeight: '100vh', background: '#ffffff' }}>

        {/* PROFILE POPUP */}
        {showProfilePopup && (
          <div onClick={closePopup} style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999, background: 'rgba(15, 23, 42, 0.6)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
            <div onClick={e => e.stopPropagation()} style={{ background: 'white', borderRadius: '28px', maxWidth: '480px', width: '100%', overflow: 'hidden', boxShadow: '0 32px 80px rgba(0,0,0,0.25)', animation: 'popupIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards' }}>
              <div style={{ background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', padding: '40px 40px 36px', position: 'relative' }}>
                <button onClick={closePopup} style={{ position: 'absolute', top: '20px', right: '20px', background: 'rgba(255,255,255,0.15)', border: 'none', cursor: 'pointer', width: '36px', height: '36px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.2s' }} onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.25)'} onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.15)'}>
                  <X size={18} color="white" strokeWidth={2.5} />
                </button>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.2)', padding: '6px 14px', borderRadius: '100px', marginBottom: '20px' }}>
                  <Sparkles size={13} color="white" />
                  <span style={{ fontSize: '12px', fontWeight: '700', color: 'white', letterSpacing: '0.5px', textTransform: 'uppercase' }}>Personalized For You</span>
                </div>
                <h2 style={{ fontSize: '28px', fontWeight: '900', color: 'white', lineHeight: '1.2', letterSpacing: '-0.5px', margin: 0 }}>
                  Find Scholarships<br />You Actually Qualify For
                </h2>
              </div>
              <div style={{ padding: '32px 40px 40px' }}>
                <p style={{ fontSize: '15px', color: '#64748b', lineHeight: '1.7', marginBottom: '28px', fontWeight: '500' }}>
                  Create your free profile and we will match you with scholarships based on your country, degree, GPA and more.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '32px' }}>
                  {[
                    ['Match Score', 'See your eligibility percentage for every scholarship'],
                    ['Smart Filter', 'Only see scholarships you can actually apply to'],
                    ['Deadline Alerts', 'Never miss an application deadline again'],
                  ].map(([title, desc]) => (
                    <div key={title} style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', marginTop: '6px', flexShrink: 0 }} />
                      <div>
                        <div style={{ fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '2px' }}>{title}</div>
                        <div style={{ fontSize: '13px', color: '#94a3b8', fontWeight: '500' }}>{desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <Link href="/profile/create" style={{ textDecoration: 'none' }}>
                    <button style={{ width: '100%', padding: '16px', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', color: 'white', border: 'none', borderRadius: '14px', fontSize: '16px', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', transition: 'all 0.3s', boxShadow: '0 8px 24px rgba(79,70,229,0.3)' }} onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 12px 32px rgba(79,70,229,0.4)' }} onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(79,70,229,0.3)' }}>
                      Create Free Profile <ChevronRight size={18} strokeWidth={2.5} />
                    </button>
                  </Link>
                  <button onClick={closePopup} style={{ width: '100%', padding: '14px', background: 'transparent', color: '#94a3b8', border: '2px solid #f1f5f9', borderRadius: '14px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s' }} onMouseEnter={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.color = '#64748b' }} onMouseLeave={e => { e.currentTarget.style.borderColor = '#f1f5f9'; e.currentTarget.style.color = '#94a3b8' }}>
                    Continue Browsing
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* BETA TOP BANNER */}
        <div style={{ width: '100%', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', color: 'white', textAlign: 'center', padding: '10px 24px', fontSize: '13px', fontWeight: '500', position: 'relative', zIndex: 200 }}>
          AdmitGoal is in Beta — Our AI model is still learning. Some scholarship details may contain mistakes. Please verify information from official university websites.{' '}
          <Link href="/contact" style={{ color: 'white', fontWeight: '700', textDecoration: 'underline' }}>Share your feedback</Link>
        </div>

        {/* NAVBAR — sticky so it scrolls away */}
        <div style={{ padding: '12px 0', background: '#ffffff', position: 'sticky', top: 0, zIndex: 100 }}>
          <nav style={{
            left: '50%',
            width: '96%',
            maxWidth: '1400px',
            margin: '0 auto',
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(79, 70, 229, 0.1)',
            borderRadius: '24px',
            padding: '16px 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 20px 60px rgba(79, 70, 229, 0.08)',
          }}>
            <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '14px', textDecoration: 'none' }}>
              <div className="logo-float" style={{
                width: '48px', height: '48px',
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%)',
                borderRadius: '14px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 8px 24px rgba(139, 92, 246, 0.35)',
              }}>
                <GraduationCap size={26} color="white" strokeWidth={2.5} />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '28px', fontWeight: '900', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '-1.5px' }}>AdmitGoal</span>
                <span style={{ fontSize: '10px', fontWeight: '800', backgroundColor: '#4f46e5', color: 'white', padding: '3px 8px', borderRadius: '6px', letterSpacing: '1px', lineHeight: '18px' }}>BETA</span>
              </div>
            </Link>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {['About', 'Contact'].map(item => (
                <Link key={item} href={`/${item.toLowerCase()}`} style={{ padding: '12px 24px', borderRadius: '14px', fontSize: '16px', fontWeight: '600', color: '#64748b', textDecoration: 'none', transition: 'all 0.3s ease' }}
                  onMouseEnter={e => { e.target.style.background = '#f8fafc'; e.target.style.color = '#4f46e5' }}
                  onMouseLeave={e => { e.target.style.background = 'transparent'; e.target.style.color = '#64748b' }}>
                  {item}
                </Link>
              ))}
              <Link href="/contact" style={{ padding: '14px 32px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', borderRadius: '16px', fontSize: '16px', fontWeight: '700', textDecoration: 'none', boxShadow: '0 8px 24px rgba(139, 92, 246, 0.35)', transition: 'all 0.3s ease' }}
                onMouseEnter={e => { e.target.style.transform = 'translateY(-3px)'; e.target.style.boxShadow = '0 12px 32px rgba(139, 92, 246, 0.5)' }}
                onMouseLeave={e => { e.target.style.transform = 'translateY(0)'; e.target.style.boxShadow = '0 8px 24px rgba(139, 92, 246, 0.35)' }}>
                Get Started →
              </Link>
            </div>
          </nav>
        </div>

        {/* HERO SECTION */}
        <section style={{ paddingTop: '60px', paddingBottom: '90px', background: 'linear-gradient(180deg, #faf5ff 0%, #ffffff 100%)', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: '15%', right: '10%', width: '600px', height: '600px', background: 'radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 70%)', borderRadius: '50%', filter: 'blur(80px)', animation: 'float 12s ease-in-out infinite' }} />
          <div style={{ position: 'absolute', bottom: '10%', left: '5%', width: '500px', height: '500px', background: 'radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%)', borderRadius: '50%', filter: 'blur(80px)', animation: 'float 15s ease-in-out infinite reverse' }} />

          <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '0 24px', position: 'relative', zIndex: 1, textAlign: 'center' }}>

            <div className="animate-in" style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.1))', border: '1.5px solid rgba(139, 92, 246, 0.2)', padding: '10px 24px', borderRadius: '100px', marginBottom: '40px', backdropFilter: 'blur(10px)' }}>
              <Sparkles size={18} color="#8b5cf6" />
              <span style={{ fontSize: '14px', fontWeight: '700', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '0.5px', textTransform: 'uppercase' }}>
                AI-Powered • 100% Free • Updated Daily
              </span>
            </div>

            <h1 className="animate-in" style={{ fontSize: '50px', fontWeight: '900', lineHeight: '1.05', letterSpacing: '-4px', marginBottom: '17px', animationDelay: '0.1s' }}>
              <span style={{ color: '#0f172a' }}>Find Your</span>
              <br />
              <span style={{ background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Dream Scholarship
              </span>
            </h1>

            <p className="animate-in" style={{ fontSize: '24px', color: '#64748b', lineHeight: '1.7', maxWidth: '750px', margin: '0 auto 28px', fontWeight: '500', animationDelay: '0.2s' }}>
              Discover 500+ fully-funded scholarships from top universities worldwide.
              <span style={{ color: '#8b5cf6', fontWeight: '700' }}> No agents, no fees</span>, just opportunities.
            </p>

            {/* SEARCH BAR */}
            <form onSubmit={handleSearch} className="animate-in" style={{ maxWidth: '780px', margin: '0 auto 28px', animationDelay: '0.3s' }}>
              <div style={{ display: 'flex', background: 'white', border: '2px solid #e2e8f0', borderRadius: '24px', padding: '10px', boxShadow: '0 20px 60px rgba(79, 70, 229, 0.12)', transition: 'all 0.3s ease' }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = '#c7d2fe'; e.currentTarget.style.boxShadow = '0 24px 70px rgba(79, 70, 229, 0.18)' }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.boxShadow = '0 20px 60px rgba(79, 70, 229, 0.12)' }}>
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '18px', padding: '0 28px' }}>
                  <Search size={24} color="#94a3b8" strokeWidth={2.5} />
                  <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by country, university, or field..." style={{ flex: 1, border: 'none', outline: 'none', fontSize: '18px', color: '#0f172a', background: 'transparent', fontFamily: 'inherit', fontWeight: '500' }} />
                </div>
                <button type="submit" style={{ padding: '18px 40px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', border: 'none', borderRadius: '18px', fontSize: '17px', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', boxShadow: '0 8px 24px rgba(139, 92, 246, 0.4)', transition: 'all 0.3s ease' }}
                  onMouseEnter={e => { e.target.style.transform = 'translateY(-2px)'; e.target.style.boxShadow = '0 12px 32px rgba(139, 92, 246, 0.5)' }}
                  onMouseLeave={e => { e.target.style.transform = 'translateY(0)'; e.target.style.boxShadow = '0 8px 24px rgba(139, 92, 246, 0.4)' }}>
                  Search <ArrowRight size={20} strokeWidth={2.5} />
                </button>
              </div>
            </form>

            {/* FILTERS UNDER SEARCH */}
            <div className="animate-in" style={{ maxWidth: '780px', margin: '0 auto', animationDelay: '0.4s' }}>
              {/* ROW 1 — REGIONS */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'center', marginBottom: '10px' }}>
                {regions.map(r => (
                  <button key={r} onClick={() => handleFilterClick('region', r)} className="filter-btn" style={{ padding: '9px 20px', background: activeRegion === r ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'white', border: activeRegion === r ? 'none' : '2px solid #e2e8f0', borderRadius: '100px', fontSize: '14px', fontWeight: '600', color: activeRegion === r ? 'white' : '#64748b', cursor: 'pointer', boxShadow: activeRegion === r ? '0 6px 20px rgba(139, 92, 246, 0.3)' : '0 2px 8px rgba(0,0,0,0.04)' }}>
                    {r}
                  </button>
                ))}
              </div>

              {/* ROW 2 — DEGREE + FUNDING */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'center' }}>
                {['Bachelor', 'Master', 'PhD'].map(l => (
                  <button key={l} onClick={() => handleFilterClick('level', l)} className="filter-btn" style={{ padding: '9px 20px', background: activeLevel === l ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'white', border: activeLevel === l ? 'none' : '2px solid #e2e8f0', borderRadius: '100px', fontSize: '14px', fontWeight: '600', color: activeLevel === l ? 'white' : '#64748b', cursor: 'pointer', boxShadow: activeLevel === l ? '0 6px 20px rgba(139, 92, 246, 0.3)' : '0 2px 8px rgba(0,0,0,0.04)' }}>
                    {l}
                  </button>
                ))}
                <button onClick={() => handleFilterClick('funding', 'Fully Funded')} className="filter-btn" style={{ padding: '9px 20px', background: activeFunding ? 'linear-gradient(135deg, #10b981, #059669)' : 'white', border: activeFunding ? 'none' : '2px solid #e2e8f0', borderRadius: '100px', fontSize: '14px', fontWeight: '600', color: activeFunding ? 'white' : '#64748b', cursor: 'pointer', boxShadow: activeFunding ? '0 6px 20px rgba(16,185,129,0.3)' : '0 2px 8px rgba(0,0,0,0.04)' }}>
                  Fully Funded
                </button>
                <button onClick={() => handleFilterClick('level', 'No IELTS')} className="filter-btn" style={{ padding: '9px 20px', background: activeLevel === 'No IELTS' ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'white', border: activeLevel === 'No IELTS' ? 'none' : '2px solid #e2e8f0', borderRadius: '100px', fontSize: '14px', fontWeight: '600', color: activeLevel === 'No IELTS' ? 'white' : '#64748b', cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
                  No IELTS
                </button>
                {hasActiveFilter && (
                  <button onClick={() => { setActiveLevel(''); setActiveRegion(''); setActiveFunding(''); setCurrentPage(1) }} className="filter-btn" style={{ padding: '9px 20px', background: 'white', border: '2px solid #fecaca', borderRadius: '100px', fontSize: '14px', fontWeight: '600', color: '#ef4444', cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
                    Clear All ×
                  </button>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* MAIN WRAPPER */}
        <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 8px' }}>

          {/* BETA NOTICE */}
          <div style={{ margin: '24px 0 0', position: 'relative', zIndex: 2 }}>
            <div style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.04), rgba(139, 92, 246, 0.04))', border: '1.5px solid rgba(139, 92, 246, 0.15)', borderRadius: '20px', padding: '18px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <span style={{ fontSize: '10px', fontWeight: '800', backgroundColor: '#4f46e5', color: 'white', padding: '4px 10px', borderRadius: '6px', letterSpacing: '1px', flexShrink: 0 }}>BETA</span>
                <p style={{ fontSize: '14px', color: '#64748b', fontWeight: '500', margin: 0, lineHeight: '1.6' }}>
                  Our AI is still learning. Scholarship details may occasionally be incomplete or outdated. Always verify important information on the official university website before applying.
                </p>
              </div>
              <Link href="/contact" style={{ fontSize: '13px', fontWeight: '700', color: '#6366f1', textDecoration: 'none', flexShrink: 0, whiteSpace: 'nowrap' }}>
                Report incorrect data →
              </Link>
            </div>
          </div>

          {/* STATS SECTION */}
          <div style={{ margin: '48px 0 0' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
              {[
                { icon: <Globe2 size={32} strokeWidth={2} />, num: `${total}+`, label: 'Live Scholarships', color: '#6366f1' },
                { icon: <TrendingUp size={32} strokeWidth={2} />, num: '50+', label: 'Countries', color: '#8b5cf6' },
                { icon: <Sparkles size={32} strokeWidth={2} />, num: '100%', label: 'Free Forever', color: '#d946ef' },
                { icon: <Zap size={32} strokeWidth={2} />, num: 'AI', label: 'Powered', color: '#f59e0b' },
              ].map((s) => (
                <div key={s.label} className="card-hover" style={{ background: 'white', border: '2px solid #f1f5f9', borderRadius: '28px', padding: '40px 24px', textAlign: 'center', boxShadow: '0 20px 60px rgba(0, 0, 0, 0.06)' }}>
                  <div style={{ color: s.color, marginBottom: '20px', display: 'flex', justifyContent: 'center' }}>{s.icon}</div>
                  <div style={{ fontSize: '48px', fontWeight: '900', color: '#0f172a', letterSpacing: '-2px', marginBottom: '12px' }}>{s.num}</div>
                  <div style={{ fontSize: '14px', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>{s.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* MAIN CONTENT */}
          <div style={{ padding: '80px 0 100px' }}>

            {/* HEADER + TOP PAGINATION */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <h2 style={{ fontSize: '36px', fontWeight: '800', color: '#0f172a', letterSpacing: '-1.5px', margin: 0 }}>
                  {loading ? 'Loading...' : `${total} Scholarships Available`}
                </h2>
                {hasActiveFilter && (
                  <p style={{ fontSize: '14px', color: '#64748b', marginTop: '6px', fontWeight: '500' }}>
                    Showing {scholarships.length} filtered results
                    <button onClick={() => { setActiveLevel(''); setActiveRegion(''); setActiveFunding(''); setCurrentPage(1) }} style={{ marginLeft: '12px', fontSize: '13px', color: '#ef4444', background: 'none', border: 'none', cursor: 'pointer', fontWeight: '600', padding: 0 }}>
                      Clear filters ×
                    </button>
                  </p>
                )}
              </div>

              {/* TOP PAGINATION */}
              {totalPages > 1 && !loading && (
                <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange} />
              )}
            </div>

            {/* ACTIVE FILTER TAGS */}
            {hasActiveFilter && (
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '24px' }}>
                {activeRegion && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#ede9fe', color: '#6d28d9', padding: '6px 14px', borderRadius: '100px', fontSize: '13px', fontWeight: '600' }}>
                    {activeRegion}
                    <button onClick={() => setActiveRegion('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6d28d9', padding: 0, fontSize: '14px', lineHeight: 1 }}>×</button>
                  </span>
                )}
                {activeLevel && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#ede9fe', color: '#6d28d9', padding: '6px 14px', borderRadius: '100px', fontSize: '13px', fontWeight: '600' }}>
                    {activeLevel}
                    <button onClick={() => setActiveLevel('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6d28d9', padding: 0, fontSize: '14px', lineHeight: 1 }}>×</button>
                  </span>
                )}
                {activeFunding && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#d1fae5', color: '#065f46', padding: '6px 14px', borderRadius: '100px', fontSize: '13px', fontWeight: '600' }}>
                    {activeFunding}
                    <button onClick={() => setActiveFunding('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#065f46', padding: 0, fontSize: '14px', lineHeight: 1 }}>×</button>
                  </span>
                )}
              </div>
            )}

            {/* GRID */}
            {loading ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                {[...Array(6)].map((_, i) => (
                  <div key={i} style={{ background: 'white', borderRadius: '20px', padding: '32px', boxShadow: '0 8px 24px rgba(0, 0, 0, 0.06)' }}>
                    <div style={{ height: '18px', background: '#f1f5f9', borderRadius: '10px', width: '60%', marginBottom: '24px' }} />
                    <div style={{ height: '32px', background: '#f1f5f9', borderRadius: '10px', marginBottom: '20px' }} />
                    <div style={{ height: '18px', background: '#f1f5f9', borderRadius: '10px', width: '80%' }} />
                  </div>
                ))}
              </div>
            ) : scholarships.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '120px 32px' }}>
                <div style={{ fontSize: '80px', marginBottom: '28px' }}>🔍</div>
                <h3 style={{ fontSize: '32px', fontWeight: '800', color: '#0f172a', marginBottom: '16px', letterSpacing: '-1px' }}>No scholarships found</h3>
                <p style={{ color: '#64748b', fontSize: '19px', fontWeight: '500' }}>Try adjusting your filters</p>
              </div>
            ) : (
              <>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                  {scholarships.map(s => <ScholarshipCard key={s.id} s={s} />)}
                </div>

                {/* BOTTOM PAGINATION */}
                {totalPages > 1 && (
                  <div style={{ marginTop: '64px' }}>
                    <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange} />
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* FOOTER */}
        <footer style={{ background: 'linear-gradient(180deg, #fafafa 0%, #f1f5f9 100%)', padding: '100px 40px 60px' }}>
          <div style={{ maxWidth: '1400px', margin: '0 auto', textAlign: 'center' }}>
            <div style={{ width: '64px', height: '64px', margin: '0 auto 28px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6, #d946ef)', borderRadius: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 12px 32px rgba(139, 92, 246, 0.3)' }}>
              <GraduationCap size={32} color="white" strokeWidth={2.5} />
            </div>
            <h3 style={{ fontSize: '32px', fontWeight: '900', color: '#0f172a', marginBottom: '20px', letterSpacing: '-1px' }}>AdmitGoal</h3>
            <p style={{ color: '#64748b', fontSize: '18px', maxWidth: '600px', margin: '0 auto 48px', fontWeight: '500', lineHeight: '1.7' }}>
              Empowering students worldwide with free scholarship opportunities. No agents, no fees, just dreams coming true.
            </p>
            <div style={{ display: 'flex', gap: '40px', justifyContent: 'center', marginBottom: '48px' }}>
              {[['About', '/about'], ['Contact', '/contact'], ['Privacy', '/privacy']].map(([l, h]) => (
                <Link key={l} href={h} style={{ color: '#64748b', fontSize: '16px', textDecoration: 'none', fontWeight: '600' }}
                  onMouseEnter={e => e.target.style.color = '#8b5cf6'}
                  onMouseLeave={e => e.target.style.color = '#64748b'}>
                  {l}
                </Link>
              ))}
            </div>
            <p style={{ color: '#94a3b8', fontSize: '15px', fontWeight: '500', marginBottom: '12px' }}>© {new Date().getFullYear()} AdmitGoal · Built with ❤️ for students worldwide</p>
            <p style={{ color: '#cbd5e1', fontSize: '13px' }}>
              Found incorrect scholarship data?{' '}
              <Link href="/contact" style={{ color: '#8b5cf6', textDecoration: 'none', fontWeight: '600' }}>Help us improve →</Link>
            </p>
          </div>
        </footer>
      </div>
    </>
  )
}