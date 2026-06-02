'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getUser } from '@/lib/supabase-auth'
import { supabase } from '@/lib/supabase'
import { Bookmark, ChevronLeft, GraduationCap, Trash2, ExternalLink, MapPin, Clock } from 'lucide-react'

export default function SavedScholarshipsPage() {
  const router = useRouter()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [scholarships, setScholarships] = useState([])

  useEffect(() => {
    async function loadSaved() {
      const currentUser = await getUser()
      if (!currentUser) {
        router.push('/login')
        return
      }
      setUser(currentUser)

      // Fetch saved scholarships
      const { data: saved, error } = await supabase
        .from('user_saved_scholarships')
        .select(`
          id,
          saved_at,
          scholarship_id,
          scholarship_details (*)
        `)
        .eq('user_id', currentUser.id)
        .order('saved_at', { ascending: false })

      if (error) {
        console.error('Error fetching saved scholarships:', error)
      } else {
        setScholarships(saved || [])
      }

      setLoading(false)
    }
    loadSaved()
  }, [router])

  async function handleUnsave(savedId, scholarshipTitle) {
    if (!confirm(`Remove "${scholarshipTitle}" from saved?`)) return

    const { error } = await supabase
      .from('user_saved_scholarships')
      .delete()
      .eq('id', savedId)

    if (error) {
      alert('Error removing scholarship')
      console.error(error)
    } else {
      setScholarships(prev => prev.filter(s => s.id !== savedId))
    }
  }

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fafafa' }}>
        <div style={{ color: '#64748b', fontSize: '16px', fontWeight: '600' }}>Loading saved scholarships...</div>
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
        
        <div style={{ marginBottom: '40px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <div style={{ width: '48px', height: '48px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bookmark size={24} color="white" strokeWidth={2.5} />
            </div>
            <div>
              <h1 style={{ fontSize: '32px', fontWeight: '800', color: '#0f172a', margin: 0, letterSpacing: '-1px' }}>
                Saved Scholarships
              </h1>
              <p style={{ fontSize: '15px', color: '#64748b', margin: 0, fontWeight: '500' }}>
                {scholarships.length} scholarship{scholarships.length !== 1 ? 's' : ''} saved
              </p>
            </div>
          </div>
        </div>

        {scholarships.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '80px 24px' }}>
            <div style={{ width: '80px', height: '80px', background: 'linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1))', borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px' }}>
              <Bookmark size={36} color="#6366f1" strokeWidth={2} />
            </div>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>No saved scholarships yet</h3>
            <p style={{ fontSize: '16px', color: '#64748b', marginBottom: '32px', maxWidth: '400px', margin: '0 auto 32px' }}>
              Start browsing scholarships and save the ones you're interested in!
            </p>
            <Link href="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '14px 32px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', borderRadius: '12px', textDecoration: 'none', fontSize: '15px', fontWeight: '700', boxShadow: '0 8px 24px rgba(99,102,241,0.3)' }}>
              Browse Scholarships
            </Link>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '24px' }}>
            {scholarships.map(({ id, saved_at, scholarship_details: s }) => {
              if (!s) return null
              
              const isFullyFunded = s.funding_type?.toLowerCase().includes('full')
              const noIelts = s.ielts_score === 'Not required' || s.ielts_score === 'Not mentioned'
              
              return (
                <div key={id} style={{ background: 'white', borderRadius: '20px', border: '1px solid #f0f0f0', padding: '24px', transition: 'all 0.3s ease', position: 'relative' }}>
                  
                  {/* Saved date badge */}
                  <div style={{ position: 'absolute', top: '16px', right: '16px', background: 'rgba(99,102,241,0.1)', color: '#6366f1', padding: '6px 12px', borderRadius: '8px', fontSize: '11px', fontWeight: '600' }}>
                    Saved {new Date(saved_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </div>

                  {/* Badges */}
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px', marginTop: '32px' }}>
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

                  {/* Title */}
                  <Link href={`/scholarship/${s.id}`} style={{ textDecoration: 'none' }}>
                    <h3 style={{ fontSize: '18px', fontWeight: '800', color: isFullyFunded ? '#059669' : '#0f172a', lineHeight: '1.4', marginBottom: '12px', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', minHeight: '50px' }}>
                      {s.title}
                    </h3>
                  </Link>

                  {/* University */}
                  {s.university_name && (
                    <p style={{ fontSize: '14px', color: '#64748b', fontWeight: '500', marginBottom: '16px' }}>
                      {s.university_name}
                    </p>
                  )}

                  {/* Info rows */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
                    {s.country && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#475569', fontWeight: '500' }}>
                        <MapPin size={14} color="#94a3b8" />
                        {s.country}
                      </div>
                    )}
                    {s.deadline && s.deadline !== 'See official website' && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#dc2626', fontWeight: '600' }}>
                        <Clock size={14} color="#dc2626" />
                        Deadline: {s.deadline}
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div style={{ display: 'flex', gap: '10px', paddingTop: '16px', borderTop: '1px solid #f8fafc' }}>
                    <Link href={`/scholarship/${s.id}`} style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', padding: '12px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', borderRadius: '10px', textDecoration: 'none', fontSize: '14px', fontWeight: '700', transition: 'all 0.2s' }}>
                      View Details
                    </Link>
                    <button onClick={() => handleUnsave(id, s.title)} style={{ padding: '12px 16px', background: '#fef2f2', color: '#ef4444', border: 'none', borderRadius: '10px', cursor: 'pointer', transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', fontWeight: '600' }}>
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}