'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getUser, getUserProfile, clearCache } from '@/lib/supabase-auth'
import { supabase } from '@/lib/supabase'
import { ChevronLeft, Save, GraduationCap } from 'lucide-react'

const countries = ['Pakistan', 'India', 'Bangladesh', 'Nigeria', 'Kenya', 'Ghana', 'Egypt', 'Afghanistan', 'Nepal', 'Sri Lanka', 'Philippines', 'Indonesia', 'Vietnam', 'Turkey', 'Iran', 'Iraq', 'Syria', 'Jordan', 'Morocco', 'Tunisia', 'Algeria', 'South Africa', 'Ethiopia', 'Uganda', 'Tanzania', 'Zimbabwe', 'Other']
const preferredCountries = ['USA', 'UK', 'Canada', 'Australia', 'Germany', 'France', 'Netherlands', 'Sweden', 'Norway', 'Denmark', 'Switzerland', 'Austria', 'Italy', 'Spain', 'Japan', 'South Korea', 'Singapore', 'New Zealand', 'Ireland', 'Belgium', 'Finland', 'China', 'UAE', 'Saudi Arabia', 'Qatar']
const degreeLevels = ['Bachelor', 'Master', 'PhD']
const fundingTypes = ['Fully Funded', 'Partial Funding', 'Any']
const fields = ['Computer Science', 'Engineering', 'Business', 'Medicine', 'Law', 'Arts', 'Sciences', 'Social Sciences', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Economics', 'Psychology', 'Education', 'Agriculture', 'Architecture', 'Other']

export default function EditProfilePage() {
  const router = useRouter()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [formData, setFormData] = useState({
    full_name: '', email: '', country: '', nationality: '',
    degree_level: '', field_of_study: '', gpa: '',
    ielts_score: '', toefl_score: '', gre_score: '',
    preferred_countries: [], funding_preference: ''
  })

  useEffect(() => {
    async function loadProfile() {
      const currentUser = await getUser()
      if (!currentUser) { router.push('/login'); return }
      setUser(currentUser)

      // Uses cache if available - instant on repeat visits
      const profile = await getUserProfile(currentUser.id)
      if (!profile) { router.push('/profile/create'); return }

      setFormData({
        full_name: profile.full_name || '',
        email: profile.email || currentUser.email,
        country: profile.country || '',
        nationality: profile.nationality || '',
        degree_level: profile.degree_level || '',
        field_of_study: profile.field_of_study || '',
        gpa: profile.gpa || '',
        ielts_score: profile.ielts_score || '',
        toefl_score: profile.toefl_score || '',
        gre_score: profile.gre_score || '',
        preferred_countries: profile.preferred_countries || [],
        funding_preference: profile.funding_preference || ''
      })
      setLoading(false)
    }
    loadProfile()
  }, [router])

  function handleChange(field, value) {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  function togglePreferredCountry(country) {
    setFormData(prev => ({
      ...prev,
      preferred_countries: prev.preferred_countries.includes(country)
        ? prev.preferred_countries.filter(c => c !== country)
        : [...prev.preferred_countries, country]
    }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!user) return
    setSaving(true)

    const profileData = {
      full_name: formData.full_name,
      email: formData.email,
      country: formData.country,
      nationality: formData.nationality,
      degree_level: formData.degree_level,
      field_of_study: formData.field_of_study,
      gpa: formData.gpa ? parseFloat(formData.gpa) : null,
      ielts_score: formData.ielts_score ? parseFloat(formData.ielts_score) : null,
      toefl_score: formData.toefl_score ? parseInt(formData.toefl_score) : null,
      gre_score: formData.gre_score ? parseInt(formData.gre_score) : null,
      preferred_countries: formData.preferred_countries,
      funding_preference: formData.funding_preference,
      updated_at: new Date().toISOString()
    }

    const { error } = await supabase
      .from('user_profiles')
      .update(profileData)
      .eq('user_id', user.id)

    if (error) {
      alert('Error updating profile. Please try again.')
      setSaving(false)
      return
    }

    // Clear profile cache so fresh data loads next time
    clearCache(user.id)
    setSaving(false)
    setSaved(true)
    setTimeout(() => {
      router.push('/dashboard')
    }, 1200)
  }

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a, #1e1b4b)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ width: '48px', height: '48px', border: '4px solid rgba(255,255,255,0.2)', borderTopColor: '#6366f1', borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 16px' }} />
          <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '15px', fontWeight: '600' }}>Loading profile...</div>
        </div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a, #1e1b4b, #312e81)', padding: '40px 24px', fontFamily: "'Inter', sans-serif" }}>

      {/* Top bar */}
      <div style={{ maxWidth: '800px', margin: '0 auto 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <button onClick={() => router.back()} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: 'white', padding: '10px 20px', borderRadius: '12px', fontSize: '14px', fontWeight: '600', cursor: 'pointer' }}>
          <ChevronLeft size={18} /> Back
        </button>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
          <div style={{ width: '36px', height: '36px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <GraduationCap size={20} color="white" strokeWidth={2.5} />
          </div>
          <span style={{ fontSize: '18px', fontWeight: '800', color: 'white' }}>Admit<span style={{ color: '#a5b4fc' }}>Goal</span></span>
        </Link>
      </div>

      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ background: 'rgba(255,255,255,0.05)', backdropFilter: 'blur(20px)', borderRadius: '24px', padding: '48px', border: '1px solid rgba(255,255,255,0.1)' }}>

          <h1 style={{ fontSize: '32px', fontWeight: '800', color: 'white', marginBottom: '12px', letterSpacing: '-1px' }}>Edit Your Profile</h1>
          <p style={{ fontSize: '15px', color: 'rgba(255,255,255,0.6)', marginBottom: '40px', fontWeight: '500' }}>
            Update your information to get better scholarship matches
          </p>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>

            {/* Basic Info */}
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'white', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid rgba(255,255,255,0.1)' }}>Basic Information</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Full Name</label>
                  <input type="text" value={formData.full_name} onChange={e => handleChange('full_name', e.target.value)} required style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                  <div>
                    <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Country</label>
                    <select value={formData.country} onChange={e => handleChange('country', e.target.value)} required style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }}>
                      <option value="" style={{ background: '#1e1b4b' }}>Select</option>
                      {countries.map(c => <option key={c} value={c} style={{ background: '#1e1b4b' }}>{c}</option>)}
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Nationality</label>
                    <select value={formData.nationality} onChange={e => handleChange('nationality', e.target.value)} required style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }}>
                      <option value="" style={{ background: '#1e1b4b' }}>Select</option>
                      {countries.map(c => <option key={c} value={c} style={{ background: '#1e1b4b' }}>{c}</option>)}
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* Education */}
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'white', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid rgba(255,255,255,0.1)' }}>Education</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Degree Level</label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                    {degreeLevels.map(level => (
                      <button key={level} type="button" onClick={() => handleChange('degree_level', level)} style={{ padding: '14px', background: formData.degree_level === level ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.08)', border: formData.degree_level === level ? 'none' : '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '14px', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s' }}>
                        {level}
                      </button>
                    ))}
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                  <div>
                    <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Field of Study</label>
                    <select value={formData.field_of_study} onChange={e => handleChange('field_of_study', e.target.value)} required style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }}>
                      <option value="" style={{ background: '#1e1b4b' }}>Select</option>
                      {fields.map(f => <option key={f} value={f} style={{ background: '#1e1b4b' }}>{f}</option>)}
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>GPA (0-4.0)</label>
                    <input type="number" step="0.01" min="0" max="4" value={formData.gpa} onChange={e => handleChange('gpa', e.target.value)} placeholder="e.g., 3.5" style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Test Scores */}
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'white', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid rgba(255,255,255,0.1)' }}>Test Scores (Optional)</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
                {[['IELTS (0-9)', 'ielts_score', '0.5', '0', '9', '7.5'], ['TOEFL (0-120)', 'toefl_score', '1', '0', '120', '100'], ['GRE (260-340)', 'gre_score', '1', '260', '340', '320']].map(([label, field, step, min, max, placeholder]) => (
                  <div key={field}>
                    <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</label>
                    <input type="number" step={step} min={min} max={max} value={formData[field]} onChange={e => handleChange(field, e.target.value)} placeholder={placeholder} style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }} />
                  </div>
                ))}
              </div>
            </div>

            {/* Preferences */}
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'white', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid rgba(255,255,255,0.1)' }}>Preferences</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Preferred Countries</label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', maxHeight: '200px', overflowY: 'auto', padding: '4px' }}>
                    {preferredCountries.map(country => (
                      <button key={country} type="button" onClick={() => togglePreferredCountry(country)} style={{ padding: '10px', background: formData.preferred_countries.includes(country) ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.08)', border: formData.preferred_countries.includes(country) ? 'none' : '1px solid rgba(255,255,255,0.15)', borderRadius: '10px', color: 'white', fontSize: '12px', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s', textAlign: 'center' }}>
                        {country}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Funding Preference</label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                    {fundingTypes.map(type => (
                      <button key={type} type="button" onClick={() => handleChange('funding_preference', type)} style={{ padding: '14px', background: formData.funding_preference === type ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.08)', border: formData.funding_preference === type ? 'none' : '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '14px', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s' }}>
                        {type}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Save button */}
            <button type="submit" disabled={saving || saved} style={{ padding: '18px', background: saved ? 'linear-gradient(135deg, #10b981, #059669)' : saving ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #10b981, #059669)', border: 'none', borderRadius: '14px', color: 'white', fontSize: '17px', fontWeight: '700', cursor: saving ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginTop: '20px', boxShadow: saving ? 'none' : '0 8px 24px rgba(16,185,129,0.4)', transition: 'all 0.3s' }}>
              {saved ? '✅ Saved! Redirecting...' : saving ? 'Saving...' : <><Save size={20} /> Save Changes</>}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
