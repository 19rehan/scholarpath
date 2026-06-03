'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getUser } from '@/lib/supabase-auth'
import { supabase } from '@/lib/supabase'
import { GraduationCap, Bookmark, FileCheck, TrendingUp, ChevronLeft, ExternalLink } from 'lucide-react'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [savedCount, setSavedCount] = useState(0)
  const [appliedCount, setAppliedCount] = useState(0)
  const [recentSaved, setRecentSaved] = useState([])
  const [recentApplied, setRecentApplied] = useState([])

  useEffect(() => {
    async function loadDashboard() {
      const currentUser = await getUser()
      if (!currentUser) {
        router.push('/login')
        return
      }
      setUser(currentUser)

      // Load profile
      const { data: userProfile } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('user_id', currentUser.id)
        .single()

      if (!userProfile) {
        router.push('/profile/create')
        return
      }
      setProfile(userProfile)

      // Load saved scholarships count
      const { count: savedTotal } = await supabase
        .from('user_saved_scholarships')
        .select('*', { count: 'exact', head: true })
        .eq('user_id', currentUser.id)
      setSavedCount(savedTotal || 0)

      // Load recent saved (last 3)
      const { data: saved } = await supabase
        .from('user_saved_scholarships')
        .select(`
          id,
          saved_at,
          scholarship_id,
          scholarship_details (id, title, country, deadline, funding_type)
        `)
        .eq('user_id', currentUser.id)
        .order('saved_at', { ascending: false })
        .limit(3)
      setRecentSaved(saved || [])

      // Load applications count
      const { count: appliedTotal } = await supabase
        .from('user_applications')
        .select('*', { count: 'exact', head: true })
        .eq('user_id', currentUser.id)
      setAppliedCount(appliedTotal || 0)

      // Load recent applications (last 3)
      const { data: applied } = await supabase
        .from('user_applications')
        .select(`
          id,
          status,
          applied_at,
          scholarship_id,
          scholarship_details (id, title, country, deadline)
        `)
        .eq('user_id', currentUser.id)
        .order('applied_at', { ascending: false })
        .limit(3)
      setRecentApplied(applied || [])

      setLoading(false)
    }
    loadDashboard()
  }, [router])

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: '#fafafa' }}>
        <div style={{ background: 'white', borderBottom: '1px solid #f0f0f0', padding: '20px 24px' }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto', height: '36px', background: 'linear-gradient(90deg, #f0f0f0 25%, #f8f8f8 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.5s infinite', borderRadius: '8px', width: '200px' }} />
        </div>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '48px 24px' }}>
          <div style={{ height: '48px', background: 'linear-gradient(90deg, #f0f0f0 25%, #f8f8f8 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.5s infinite', borderRadius: '8px', width: '300px', marginBottom: '40px' }} />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '24px' }}>
            {[1,2,3].map(i => (
              <div key={i} style={{ background: 'white', borderRadius: '20px', border: '1px solid #f0f0f0', padding: '24px' }}>
                <div style={{ height: '20px', background: 'linear-gradient(90deg, #f0f0f0 25%, #f8f8f8 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.5s infinite', borderRadius: '6px', width: '80%', marginBottom: '12px' }} />
                <div style={{ height: '60px', background: 'linear-gradient(90deg, #f0f0f0 25%, #f8f8f8 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.5s infinite', borderRadius: '8px', marginBottom: '16px' }} />
                <div style={{ height: '20px', background: 'linear-gradient(90deg, #f0f0f0 25%, #f8f8f8 50%, #f0f0f0 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.5s infinite', borderRadius: '6px', width: '60%' }} />
              </div>
            ))}
          </div>
        </div>
        <style jsx>{`
          @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
          }
        `}</style>
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#fafafa', fontFamily: "'Inter', sans-serif" }}>
      
      {/* Header */}
      <div style={{ background: 'white', borderBottom: '1px solid #f0f0f0', padding: '20px 24px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <button onClick={() => router.back()} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#f8fafc', border: '1px solid #e2e8f0', color: '#475569', padding: '10px 20px', borderRadius: '12px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s' }}>
            <ChevronLeft size={18} /> Back
          </button>
          
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
            <div style={{ width: '36px', height: '36px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={20} color="white" strokeWidth={2.5} />
            </div>
            <span style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.5px' }}>Admit<span style={{ color: '#6366f1' }}>Goal</span></span>
          </Link>
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '48px 24px' }}>
        
        {/* Welcome section */}
        <div style={{ marginBottom: '40px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: '800', color: '#0f172a', marginBottom: '8px', letterSpacing: '-1px' }}>
            Welcome back, {profile?.full_name?.split(' ')[0] || user.email?.split('@')[0]}!
          </h1>
          <p style={{ fontSize: '16px', color: '#64748b', fontWeight: '500' }}>
            Here's your scholarship journey overview
          </p>
        </div>

        {/* Stats cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '48px' }}>
          <Link href="/saved" style={{ textDecoration: 'none' }}>
            <div style={{ background: 'linear-gradient(135deg, #ede9fe, #ddd6fe)', borderRadius: '20px', padding: '32px', transition: 'all 0.3s', cursor: 'pointer' }}
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
            <div style={{ background: 'linear-gradient(135deg, #fef3c7, #fde68a)', borderRadius: '20px', padding: '32px', transition: 'all 0.3s', cursor: 'pointer' }}
              onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
              <div style={{ width: '48px', height: '48px', background: 'linear-gradient(135deg, #f59e0b, #d97706)', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
                <TrendingUp size={24} color="white" strokeWidth={2.5} />
              </div>
              <div style={{ fontSize: '36px', fontWeight: '800', color: '#b45309', marginBottom: '8px' }}>
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
              <Link href="/saved" style={{ fontSize: '14px', color: '#6366f1', textDecoration: 'none', fontWeight: '600' }}>
                View all →
              </Link>
            </div>

            {recentSaved.length === 0 ? (
              <div style={{ background: 'white', borderRadius: '16px', padding: '40px', textAlign: 'center', border: '1px solid #f0f0f0' }}>
                <Bookmark size={32} color="#cbd5e1" strokeWidth={2} style={{ margin: '0 auto 16px' }} />
                <p style={{ fontSize: '14px', color: '#94a3b8', fontWeight: '500' }}>No saved scholarships yet</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {recentSaved.map(({ id, scholarship_details: s }) => s && (
                  <Link key={id} href={`/scholarship/${s.id}`} style={{ textDecoration: 'none' }}>
                    <div style={{ background: 'white', borderRadius: '16px', padding: '20px', border: '1px solid #f0f0f0', transition: 'all 0.2s' }}
                      onMouseEnter={e => { e.currentTarget.style.borderColor = '#c7d2fe'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(99,102,241,0.1)' }}
                      onMouseLeave={e => { e.currentTarget.style.borderColor = '#f0f0f0'; e.currentTarget.style.boxShadow = 'none' }}>
                      <div style={{ fontSize: '15px', fontWeight: '700', color: '#0f172a', marginBottom: '8px', display: '-webkit-box', WebkitLineClamp: 1, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
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
                <FileCheck size={32} color="#cbd5e1" strokeWidth={2} style={{ margin: '0 auto 16px' }} />
                <p style={{ fontSize: '14px', color: '#94a3b8', fontWeight: '500', marginBottom: '16px' }}>No applications tracked yet</p>
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
                        <div style={{ fontSize: '15px', fontWeight: '700', color: '#0f172a', flex: 1, display: '-webkit-box', WebkitLineClamp: 1, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                          {s.title}
                        </div>
                        <span style={{ fontSize: '11px', fontWeight: '700', background: status === 'submitted' ? '#dcfce7' : '#fef3c7', color: status === 'submitted' ? '#15803d' : '#b45309', padding: '4px 10px', borderRadius: '100px', textTransform: 'uppercase', flexShrink: 0, marginLeft: '12px' }}>
                          {status}
                        </span>
                      </div>
                      <div style={{ fontSize: '13px', color: '#64748b' }}>
                        {s.country}
                      </div>
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
            onMouseEnter={e => { e.currentTarget.style.background = '#f0f4ff' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'white' }}>
            Update Profile
          </Link>
        </div>
      </div>
    </div>
  )
}