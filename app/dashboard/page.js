'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getUser, getUserProfile, getDashboardData } from '@/lib/supabase-auth'
import { GraduationCap, Bookmark, FileCheck, TrendingUp, ChevronLeft } from 'lucide-react'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [dashData, setDashData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadDashboard() {
      // Step 1: fast session check
      const currentUser = await getUser()
      if (!currentUser) {
        router.push('/login')
        return
      }
      setUser(currentUser)

      // Step 2: profile + dashboard data fire in PARALLEL
      const [userProfile, data] = await Promise.all([
        getUserProfile(currentUser.id),
        getDashboardData(currentUser.id),
      ])

      if (!userProfile) {
        router.push('/profile/create')
        return
      }

      setProfile(userProfile)
      setDashData(data)
      setLoading(false)
    }
    loadDashboard()
  }, [router])

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: '#fafafa' }}>
        <style>{`
          @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
          }
          .skel {
            background: linear-gradient(90deg, #f0f0f0 25%, #f8f8f8 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: 8px;
          }
        `}</style>

        {/* Header skeleton */}
        <div style={{ background: 'white', borderBottom: '1px solid #f0f0f0', padding: '20px 24px' }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="skel" style={{ width: '80px', height: '40px' }} />
            <div className="skel" style={{ width: '160px', height: '36px' }} />
          </div>
        </div>

        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '48px 24px' }}>
          {/* Welcome skeleton */}
          <div className="skel" style={{ width: '300px', height: '40px', marginBottom: '12px' }} />
          <div className="skel" style={{ width: '220px', height: '20px', marginBottom: '48px' }} />

          {/* Stats skeleton */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '48px' }}>
            {[1, 2, 3].map(i => (
              <div key={i} className="skel" style={{ height: '160px', borderRadius: '20px' }} />
            ))}
          </div>

          {/* Cards skeleton */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
            {[1, 2].map(i => (
              <div key={i}>
                <div className="skel" style={{ width: '140px', height: '28px', marginBottom: '20px' }} />
                {[1, 2, 3].map(j => (
                  <div key={j} className="skel" style={{ height: '80px', borderRadius: '16px', marginBottom: '12px' }} />
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const { savedCount, recentSaved, appliedCount, recentApplied } = dashData

  return (
    <div style={{ minHeight: '100vh', background: '#fafafa', fontFamily: "'Inter', sans-serif" }}>

      {/* Header */}
      <div style={{ background: 'white', borderBottom: '1px solid #f0f0f0', padding: '20px 24px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <button onClick={() => router.back()} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#f8fafc', border: '1px solid #e2e8f0', color: '#475569', padding: '10px 20px', borderRadius: '12px', fontSize: '14px', fontWeight: '600', cursor: 'pointer' }}>
            <ChevronLeft size={18} /> Back
          </button>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
            <div style={{ width: '36px', height: '36px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={20} color="white" strokeWidth={2.5} />
            </div>
            <span style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a' }}>Admit<span style={{ color: '#6366f1' }}>Goal</span></span>
          </Link>
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '48px 24px' }}>

        {/* Welcome */}
        <div style={{ marginBottom: '40px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: '800', color: '#0f172a', marginBottom: '8px', letterSpacing: '-1px' }}>
            Welcome back, {profile?.full_name?.split(' ')[0] || user.email?.split('@')[0]}! 👋
          </h1>
          <p style={{ fontSize: '16px', color: '#64748b', fontWeight: '500' }}>
            Here's your scholarship journey overview
          </p>
        </div>

        {/* Stats cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '48px' }}>

          <Link href="/saved" style={{ textDecoration: 'none' }}>
            <div style={{ background: 'linear-gradient(135deg, #ede9fe, #ddd6fe)', borderRadius: '20px', padding: '32px', transition: 'transform 0.3s', cursor: 'pointer' }}
              onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
              <div style={{ width: '48px', height: '48px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
                <Bookmark size={24} color="white" strokeWidth={2.5} />
              </div>
              <div style={{ fontSize: '36px', fontWeight: '800', color: '#5b21b6', marginBottom: '8px' }}>{savedCount}</div>
              <div style={{ fontSize: '15px', color: '#6d28d9', fontWeight: '600' }}>Saved Scholarships</div>
            </div>
          </Link>

          <div style={{ background: 'linear-gradient(135deg, #dcfce7, #bbf7d0)', borderRadius: '20px', padding: '32px' }}>
            <div style={{ width: '48px', height: '48px', background: 'linear-gradient(135deg, #10b981, #059669)', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
              <FileCheck size={24} color="white" strokeWidth={2.5} />
            </div>
            <div style={{ fontSize: '36px', fontWeight: '800', color: '#15803d', marginBottom: '8px' }}>{appliedCount}</div>
            <div style={{ fontSize: '15px', color: '#16a34a', fontWeight: '600' }}>Applications</div>
          </div>

          <Link href="/profile/edit" style={{ textDecoration: 'none' }}>
            <div style={{ background: 'linear-gradient(135deg, #fef3c7, #fde68a)', borderRadius: '20px', padding: '32px', transition: 'transform 0.3s', cursor: 'pointer' }}
              onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
              <div style={{ width: '48px', height: '48px', background: 'linear-gradient(135deg, #f59e0b, #d97706)', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
                <TrendingUp size={24} color="white" strokeWidth={2.5} />
              </div>
              <div style={{ fontSize: '28px', fontWeight: '800', color: '#b45309', marginBottom: '8px' }}>
                {profile?.degree_level?.split(',')[0] || 'N/A'}
              </div>
              <div style={{ fontSize: '15px', color: '#d97706', fontWeight: '600' }}>Your Degree Level</div>
            </div>
          </Link>
        </div>

        {/* Two columns */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>

          {/* Recent Saved */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: '800', color: '#0f172a' }}>Recently Saved</h2>
              <Link href="/saved" style={{ fontSize: '14px', color: '#6366f1', textDecoration: 'none', fontWeight: '600' }}>View all →</Link>
            </div>

            {recentSaved.length === 0 ? (
              <div style={{ background: 'white', borderRadius: '16px', padding: '40px', textAlign: 'center', border: '1px solid #f0f0f0' }}>
                <Bookmark size={32} color="#cbd5e1" style={{ margin: '0 auto 16px', display: 'block' }} />
                <p style={{ fontSize: '14px', color: '#94a3b8', fontWeight: '500' }}>No saved scholarships yet</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {recentSaved.map(({ id, scholarship_details: s }) => s && (
                  <Link key={id} href={`/scholarship/${s.id}`} style={{ textDecoration: 'none' }}>
                    <div style={{ background: 'white', borderRadius: '16px', padding: '20px', border: '1px solid #f0f0f0', transition: 'all 0.2s' }}
                      onMouseEnter={e => { e.currentTarget.style.borderColor = '#c7d2fe'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(99,102,241,0.1)' }}
                      onMouseLeave={e => { e.currentTarget.style.borderColor = '#f0f0f0'; e.currentTarget.style.boxShadow = 'none' }}>
                      <div style={{ fontSize: '15px', fontWeight: '700', color: '#0f172a', marginBottom: '8px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {s.title}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '13px', color: '#64748b' }}>
                        <span>{s.country}</span>
                        {s.deadline && <span>• Deadline: {s.deadline}</span>}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* Recent Applications */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: '800', color: '#0f172a' }}>Your Applications</h2>
            </div>

            {recentApplied.length === 0 ? (
              <div style={{ background: 'white', borderRadius: '16px', padding: '40px', textAlign: 'center', border: '1px solid #f0f0f0' }}>
                <FileCheck size={32} color="#cbd5e1" style={{ margin: '0 auto 16px', display: 'block' }} />
                <p style={{ fontSize: '14px', color: '#94a3b8', fontWeight: '500', marginBottom: '8px' }}>No applications tracked yet</p>
                <p style={{ fontSize: '12px', color: '#cbd5e1' }}>Application tracker coming soon!</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {recentApplied.map(({ id, status, scholarship_details: s }) => s && (
                  <Link key={id} href={`/scholarship/${s.id}`} style={{ textDecoration: 'none' }}>
                    <div style={{ background: 'white', borderRadius: '16px', padding: '20px', border: '1px solid #f0f0f0', transition: 'all 0.2s' }}
                      onMouseEnter={e => { e.currentTarget.style.borderColor = '#c7d2fe'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(99,102,241,0.1)' }}
                      onMouseLeave={e => { e.currentTarget.style.borderColor = '#f0f0f0'; e.currentTarget.style.boxShadow = 'none' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <div style={{ fontSize: '15px', fontWeight: '700', color: '#0f172a', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {s.title}
                        </div>
                        <span style={{ fontSize: '11px', fontWeight: '700', background: status === 'submitted' ? '#dcfce7' : '#fef3c7', color: status === 'submitted' ? '#15803d' : '#b45309', padding: '4px 10px', borderRadius: '100px', textTransform: 'uppercase', flexShrink: 0, marginLeft: '12px' }}>
                          {status}
                        </span>
                      </div>
                      <div style={{ fontSize: '13px', color: '#64748b' }}>{s.country}</div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick actions */}
        <div style={{ marginTop: '48px', display: 'flex', gap: '16px', justifyContent: 'center' }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '14px 28px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', borderRadius: '12px', textDecoration: 'none', fontSize: '15px', fontWeight: '700', boxShadow: '0 8px 24px rgba(99,102,241,0.3)', transition: 'all 0.2s' }}
            onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
            onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
            Browse Scholarships
          </Link>
          <Link href="/profile/edit" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '14px 28px', background: 'white', color: '#6366f1', border: '2px solid #6366f1', borderRadius: '12px', textDecoration: 'none', fontSize: '15px', fontWeight: '700', transition: 'all 0.2s' }}
            onMouseEnter={e => e.currentTarget.style.background = '#f0f4ff'}
            onMouseLeave={e => e.currentTarget.style.background = 'white'}>
            Update Profile
          </Link>
        </div>
      </div>
    </div>
  )
}