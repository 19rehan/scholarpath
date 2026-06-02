'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getUser } from '@/lib/supabase-auth'
import { supabase } from '@/lib/supabase'
import { ChevronRight, ChevronLeft, CheckCircle, GraduationCap } from 'lucide-react'

const countries = ['Pakistan', 'India', 'Bangladesh', 'Nigeria', 'Kenya', 'Ghana', 'Egypt', 'Afghanistan', 'Nepal', 'Sri Lanka', 'Philippines', 'Indonesia', 'Vietnam', 'Turkey', 'Iran', 'Iraq', 'Syria', 'Jordan', 'Morocco', 'Tunisia', 'Algeria', 'South Africa', 'Ethiopia', 'Uganda', 'Tanzania', 'Zimbabwe', 'Other']

const preferredCountries = ['USA', 'UK', 'Canada', 'Australia', 'Germany', 'France', 'Netherlands', 'Sweden', 'Norway', 'Denmark', 'Switzerland', 'Austria', 'Italy', 'Spain', 'Japan', 'South Korea', 'Singapore', 'New Zealand', 'Ireland', 'Belgium', 'Finland', 'China', 'UAE', 'Saudi Arabia', 'Qatar']

const degreeLevels = ['Bachelor', 'Master', 'PhD']

const fundingTypes = ['Fully Funded', 'Partial Funding', 'Any']

const fields = ['Computer Science', 'Engineering', 'Business', 'Medicine', 'Law', 'Arts', 'Sciences', 'Social Sciences', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Economics', 'Psychology', 'Education', 'Agriculture', 'Architecture', 'Other']

export default function ProfileCreatePage() {
  const router = useRouter()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [step, setStep] = useState(1)

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    country: '',
    nationality: '',
    degree_level: '',
    field_of_study: '',
    gpa: '',
    ielts_score: '',
    toefl_score: '',
    gre_score: '',
    preferred_countries: [],
    funding_preference: ''
  })

  useEffect(() => {
    async function checkUser() {
      const currentUser = await getUser()
      if (!currentUser) {
        router.push('/login')
        return
      }
      setUser(currentUser)
      
      // Pre-fill email and name from auth
      setFormData(prev => ({
        ...prev,
        email: currentUser.email,
        full_name: currentUser.user_metadata?.full_name || ''
      }))

      // Check if profile already exists
      const { data: existingProfile } = await supabase
        .from('user_profiles')
        .select('id')
        .eq('user_id', currentUser.id)
        .single()

      if (existingProfile) {
        router.push('/dashboard')
        return
      }

      setLoading(false)
    }
    checkUser()
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

  async function handleSubmit() {
    if (!user) return

    setSaving(true)

    const profileData = {
      user_id: user.id,
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
      funding_preference: formData.funding_preference
    }

    const { error } = await supabase
      .from('user_profiles')
      .insert([profileData])

    if (error) {
      console.error('Error saving profile:', error)
      alert('Error saving profile. Please try again.')
      setSaving(false)
      return
    }

    // Redirect to homepage
    router.push('/')
  }

  function canGoNext() {
    if (step === 1) return formData.full_name && formData.country && formData.nationality
    if (step === 2) return formData.degree_level && formData.field_of_study
    if (step === 3) return true // Test scores are optional
    if (step === 4) return formData.preferred_countries.length > 0 && formData.funding_preference
    return false
  }

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #0f172a, #1e1b4b)' }}>
        <div style={{ color: 'white', fontSize: '16px', fontWeight: '600' }}>Loading...</div>
      </div>
    )
  }

  const totalSteps = 4
  const progress = (step / totalSteps) * 100

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a, #1e1b4b, #312e81)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px 24px', fontFamily: "'Inter', sans-serif" }}>
      
      {/* Logo top left */}
      <Link href="/" style={{ position: 'absolute', top: '32px', left: '32px', display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
        <div style={{ width: '40px', height: '40px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <GraduationCap size={22} color="white" strokeWidth={2.5} />
        </div>
        <span style={{ fontSize: '20px', fontWeight: '800', color: 'white', letterSpacing: '-0.5px' }}>Admit<span style={{ color: '#a5b4fc' }}>Goal</span></span>
      </Link>

      <div style={{ maxWidth: '600px', width: '100%' }}>
        
        {/* Progress bar */}
        <div style={{ background: 'rgba(255,255,255,0.1)', borderRadius: '100px', height: '8px', marginBottom: '32px', overflow: 'hidden' }}>
          <div style={{ width: `${progress}%`, height: '100%', background: 'linear-gradient(90deg, #6366f1, #8b5cf6)', borderRadius: '100px', transition: 'width 0.3s ease' }} />
        </div>

        <div style={{ background: 'rgba(255,255,255,0.05)', backdropFilter: 'blur(20px)', borderRadius: '24px', padding: '48px', border: '1px solid rgba(255,255,255,0.1)' }}>
          
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <h1 style={{ fontSize: '32px', fontWeight: '800', color: 'white', marginBottom: '12px', letterSpacing: '-1px' }}>
              {step === 1 && 'Tell us about yourself'}
              {step === 2 && 'Your education'}
              {step === 3 && 'Test scores (optional)'}
              {step === 4 && 'Preferences'}
            </h1>
            <p style={{ fontSize: '15px', color: 'rgba(255,255,255,0.6)', fontWeight: '500' }}>
              Step {step} of {totalSteps}
            </p>
          </div>

          {/* STEP 1: Basic Info */}
          {step === 1 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Full Name</label>
                <input type="text" value={formData.full_name} onChange={e => handleChange('full_name', e.target.value)} placeholder="Your full name" style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }} />
              </div>

              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Country of Residence</label>
                <select value={formData.country} onChange={e => handleChange('country', e.target.value)} style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }}>
                  <option value="" style={{ background: '#1e1b4b' }}>Select country</option>
                  {countries.map(c => <option key={c} value={c} style={{ background: '#1e1b4b' }}>{c}</option>)}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Nationality</label>
                <select value={formData.nationality} onChange={e => handleChange('nationality', e.target.value)} style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }}>
                  <option value="" style={{ background: '#1e1b4b' }}>Select nationality</option>
                  {countries.map(c => <option key={c} value={c} style={{ background: '#1e1b4b' }}>{c}</option>)}
                </select>
              </div>
            </div>
          )}

          {/* STEP 2: Education */}
          {step === 2 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Degree Level</label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                  {degreeLevels.map(level => (
                    <button key={level} type="button" onClick={() => handleChange('degree_level', level)} style={{ padding: '16px', background: formData.degree_level === level ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.08)', border: formData.degree_level === level ? 'none' : '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s' }}>
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Field of Study</label>
                <select value={formData.field_of_study} onChange={e => handleChange('field_of_study', e.target.value)} style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }}>
                  <option value="" style={{ background: '#1e1b4b' }}>Select field</option>
                  {fields.map(f => <option key={f} value={f} style={{ background: '#1e1b4b' }}>{f}</option>)}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>GPA (0.0 - 4.0)</label>
                <input type="number" step="0.01" min="0" max="4" value={formData.gpa} onChange={e => handleChange('gpa', e.target.value)} placeholder="e.g., 3.5" style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }} />
              </div>
            </div>
          )}

          {/* STEP 3: Test Scores */}
          {step === 3 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '14px', marginBottom: '8px' }}>Skip any tests you haven't taken</p>

              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>IELTS Score (0.0 - 9.0)</label>
                <input type="number" step="0.5" min="0" max="9" value={formData.ielts_score} onChange={e => handleChange('ielts_score', e.target.value)} placeholder="e.g., 7.5" style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }} />
              </div>

              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>TOEFL Score (0 - 120)</label>
                <input type="number" min="0" max="120" value={formData.toefl_score} onChange={e => handleChange('toefl_score', e.target.value)} placeholder="e.g., 100" style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }} />
              </div>

              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>GRE Score (260 - 340)</label>
                <input type="number" min="260" max="340" value={formData.gre_score} onChange={e => handleChange('gre_score', e.target.value)} placeholder="e.g., 320" style={{ width: '100%', padding: '14px 18px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box' }} />
              </div>
            </div>
          )}

          {/* STEP 4: Preferences */}
          {step === 4 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Preferred Countries (select multiple)</label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', maxHeight: '300px', overflowY: 'auto', padding: '4px' }}>
                  {preferredCountries.map(country => (
                    <button key={country} type="button" onClick={() => togglePreferredCountry(country)} style={{ padding: '12px', background: formData.preferred_countries.includes(country) ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.08)', border: formData.preferred_countries.includes(country) ? 'none' : '1px solid rgba(255,255,255,0.15)', borderRadius: '10px', color: 'white', fontSize: '13px', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s', textAlign: 'center' }}>
                      {country}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '13px', fontWeight: '600', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Funding Preference</label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                  {fundingTypes.map(type => (
                    <button key={type} type="button" onClick={() => handleChange('funding_preference', type)} style={{ padding: '16px', background: formData.funding_preference === type ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.08)', border: formData.funding_preference === type ? 'none' : '1px solid rgba(255,255,255,0.15)', borderRadius: '12px', color: 'white', fontSize: '14px', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s' }}>
                      {type}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Navigation buttons */}
          <div style={{ display: 'flex', gap: '12px', marginTop: '40px' }}>
            {step > 1 && (
              <button onClick={() => setStep(step - 1)} style={{ flex: 1, padding: '16px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '14px', color: 'white', fontSize: '16px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', transition: 'all 0.2s' }}>
                <ChevronLeft size={20} /> Back
              </button>
            )}
            
            {step < totalSteps ? (
              <button onClick={() => setStep(step + 1)} disabled={!canGoNext()} style={{ flex: 1, padding: '16px', background: canGoNext() ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '14px', color: canGoNext() ? 'white' : 'rgba(255,255,255,0.3)', fontSize: '16px', fontWeight: '700', cursor: canGoNext() ? 'pointer' : 'not-allowed', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', transition: 'all 0.2s', boxShadow: canGoNext() ? '0 8px 24px rgba(99,102,241,0.4)' : 'none' }}>
                Next <ChevronRight size={20} />
              </button>
            ) : (
              <button onClick={handleSubmit} disabled={!canGoNext() || saving} style={{ flex: 1, padding: '16px', background: canGoNext() && !saving ? 'linear-gradient(135deg, #10b981, #059669)' : 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '14px', color: canGoNext() ? 'white' : 'rgba(255,255,255,0.3)', fontSize: '16px', fontWeight: '700', cursor: canGoNext() && !saving ? 'pointer' : 'not-allowed', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', transition: 'all 0.2s', boxShadow: canGoNext() && !saving ? '0 8px 24px rgba(16,185,129,0.4)' : 'none' }}>
                {saving ? 'Saving...' : (
                  <>Complete Profile <CheckCircle size={20} /></>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}