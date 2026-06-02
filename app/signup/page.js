'use client'
// app/signup/page.js

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import {
  signUpWithEmail,
  signInWithGoogle,
  signInWithFacebook,
  signInWithApple,
  signInWithMicrosoft,
} from '@/lib/supabase-auth'

export default function SignupPage() {
  const router = useRouter()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [socialLoading, setSocialLoading] = useState(null)
  const [error, setError] = useState('')

  async function handleSignup(e) {
    e.preventDefault()
    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    setLoading(true)
    setError('')
    const { error } = await signUpWithEmail(fullName, email, password)
    if (error) {
      setError(error.message)
      setLoading(false)
    } else {
      // Redirect to homepage with new_user flag to trigger profile modal
      router.push('/?new_user=true')
      router.refresh()
    }
  }

  async function handleSocial(provider, fn) {
    setSocialLoading(provider)
    setError('')
    const { error } = await fn()
    if (error) {
      setError(error.message)
      setSocialLoading(null)
    }
  }

  const socialProviders = [
    { id: 'google', label: 'Google', fn: signInWithGoogle, icon: GoogleIcon },
    { id: 'facebook', label: 'Facebook', fn: signInWithFacebook, icon: FacebookIcon },
    { id: 'apple', label: 'Apple', fn: signInWithApple, icon: AppleIcon },
    { id: 'microsoft', label: 'Microsoft', fn: signInWithMicrosoft, icon: MicrosoftIcon },
  ]

  const trustItems = [
    '100% Free — No hidden charges',
    'No agents required',
    'Scholarships updated daily',
    'Used by students worldwide',
  ]

  return (
    <div style={styles.page}>
      <div style={styles.blob1} />
      <div style={styles.blob2} />

      <div style={styles.wrapper}>
        {/* Left panel */}
        <div style={styles.leftPanel}>
          <div style={styles.globeWrap}>
            <div style={styles.orbit2} />
            <div style={styles.orbit1}><div style={styles.orbitDot} /></div>
            <div style={styles.globe}>🎓</div>
          </div>
          <h2 style={styles.leftTitle}>Start Your Journey Today</h2>
          <p style={styles.leftSub}>
            No agents. No fees. Just the right scholarship for you, found in seconds with AI.
          </p>
          <div style={styles.trustList}>
            {trustItems.map(item => (
              <div key={item} style={styles.trustItem}>
                <div style={styles.trustCheck}>✓</div>
                <span style={styles.trustText}>{item}</span>
              </div>
            ))}
          </div>
          <div style={styles.statsRow}>
            {[['200+', 'Scholarships'], ['40+', 'Countries'], ['50K+', 'Students']].map(([n, l]) => (
              <div key={l} style={styles.statCard}>
                <div style={styles.statNum}>{n}</div>
                <div style={styles.statLabel}>{l}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right panel */}
        <div style={styles.rightPanel}>
          <Link href="/" style={styles.logoLink}>
            <span style={styles.logoText}>Admit<span style={styles.logoAccent}>Goal</span></span>
          </Link>

          <h1 style={styles.heading}>Create free account</h1>
          <p style={styles.subheading}>Takes less than 30 seconds</p>

          <div style={styles.socialGrid}>
            {socialProviders.map(({ id, label, fn, icon: Icon }) => (
              <button
                key={id}
                onClick={() => handleSocial(id, fn)}
                disabled={!!socialLoading}
                style={{
                  ...styles.socialBtn,
                  opacity: socialLoading && socialLoading !== id ? 0.5 : 1,
                }}
              >
                <Icon />
                {socialLoading === id ? 'Connecting…' : label}
              </button>
            ))}
          </div>

          <div style={styles.divider}>
            <div style={styles.divLine} />
            <span style={styles.divText}>or sign up with email</span>
            <div style={styles.divLine} />
          </div>

          {error && <div style={styles.errorBox}>{error}</div>}

          <form onSubmit={handleSignup}>
            <div style={styles.field}>
              <label style={styles.label}>Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                placeholder="Your full name"
                required
                style={styles.input}
              />
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@email.com"
                required
                style={styles.input}
              />
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Min. 8 characters"
                required
                minLength={8}
                style={styles.input}
              />
            </div>

            <button type="submit" disabled={loading} style={styles.submitBtn}>
              {loading ? 'Creating account…' : 'Create Free Account →'}
            </button>
          </form>

          <p style={styles.legalText}>
            By signing up you agree to our{' '}
            <Link href="/privacy" style={styles.linkAccent}>Privacy Policy</Link>
          </p>

          <p style={styles.bottomLink}>
            Already have an account?{' '}
            <Link href="/login" style={styles.linkAccent}>Sign In</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

// ─── SVG Social Icons (same as login page) ───────────────────────────────────

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
  )
}
function FacebookIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="#1877F2">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
    </svg>
  )
}
function AppleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701z"/>
    </svg>
  )
}
function MicrosoftIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 23 23">
      <path fill="#f3f3f3" d="M0 0h23v23H0z"/>
      <path fill="#f35325" d="M1 1h10v10H1z"/>
      <path fill="#81bc06" d="M12 1h10v10H12z"/>
      <path fill="#05a6f0" d="M1 12h10v10H1z"/>
      <path fill="#ffba08" d="M12 12h10v10H12z"/>
    </svg>
  )
}

// ─── Styles ──────────────────────────────────────────────────────────────────

const styles = {
  page: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0f172a, #1e1b4b, #312e81)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    padding: '24px 16px', position: 'relative', overflow: 'hidden',
    fontFamily: "'DM Sans', system-ui, sans-serif",
  },
  blob1: {
    position: 'fixed', width: 400, height: 400, borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(79,70,229,0.12), transparent)',
    top: -100, right: -100, pointerEvents: 'none',
  },
  blob2: {
    position: 'fixed', width: 300, height: 300, borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(5,150,105,0.1), transparent)',
    bottom: -60, left: -60, pointerEvents: 'none',
  },
  wrapper: {
    display: 'grid', gridTemplateColumns: '1fr 1fr',
    maxWidth: 920, width: '100%',
    borderRadius: 24, overflow: 'hidden',
    border: '1px solid rgba(255,255,255,0.08)',
    boxShadow: '0 32px 80px rgba(0,0,0,0.5)',
    position: 'relative', zIndex: 1,
  },
  leftPanel: {
    background: 'linear-gradient(160deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%)',
    padding: '52px 40px',
    display: 'flex', flexDirection: 'column',
    justifyContent: 'center', alignItems: 'center',
  },
  globeWrap: { position: 'relative', width: 120, height: 120, marginBottom: 28 },
  globe: {
    width: 120, height: 120, borderRadius: '50%',
    background: 'rgba(79,70,229,0.2)',
    border: '2px solid rgba(255,255,255,0.15)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: 52, position: 'relative', zIndex: 1,
  },
  orbit1: {
    position: 'absolute', width: 160, height: 160, top: -20, left: -20,
    borderRadius: '50%', border: '1px dashed rgba(255,255,255,0.15)',
  },
  orbit2: {
    position: 'absolute', width: 210, height: 210, top: -45, left: -45,
    borderRadius: '50%', border: '1px dashed rgba(255,255,255,0.08)',
  },
  orbitDot: {
    width: 10, height: 10, borderRadius: '50%', background: '#a5b4fc',
    position: 'absolute', top: 8, left: '50%', transform: 'translateX(-50%)',
  },
  leftTitle: {
    fontFamily: "'Bricolage Grotesque', system-ui, sans-serif",
    fontSize: 24, fontWeight: 700, color: '#fff', textAlign: 'center',
    marginBottom: 12, lineHeight: 1.3,
  },
  leftSub: {
    fontSize: 14, color: 'rgba(255,255,255,0.55)', textAlign: 'center',
    lineHeight: 1.7, maxWidth: 270, marginBottom: 24,
  },
  trustList: { display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 28, alignSelf: 'stretch' },
  trustItem: { display: 'flex', alignItems: 'center', gap: 10 },
  trustCheck: {
    width: 20, height: 20, borderRadius: '50%',
    background: 'rgba(5,150,105,0.2)', border: '1px solid rgba(5,150,105,0.4)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    color: '#34d399', fontSize: 11, flexShrink: 0,
  },
  trustText: { fontSize: 13, color: 'rgba(255,255,255,0.65)' },
  statsRow: { display: 'flex', gap: 12 },
  statCard: {
    background: 'rgba(255,255,255,0.06)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 12, padding: '12px 16px', textAlign: 'center', flex: 1,
  },
  statNum: { fontFamily: "'Bricolage Grotesque', system-ui, sans-serif", fontSize: 22, fontWeight: 700, color: '#a5b4fc' },
  statLabel: { fontSize: 11, color: 'rgba(255,255,255,0.45)', marginTop: 2 },
  rightPanel: {
    background: 'rgba(10,15,35,0.97)', padding: '48px 44px',
    display: 'flex', flexDirection: 'column', justifyContent: 'center',
  },
  logoLink: { textDecoration: 'none', marginBottom: 28, display: 'block' },
  logoText: {
    fontFamily: "'Bricolage Grotesque', system-ui, sans-serif",
    fontSize: 20, fontWeight: 700, color: '#fff', letterSpacing: '-0.3px',
  },
  logoAccent: { color: '#818cf8' },
  heading: {
    fontFamily: "'Bricolage Grotesque', system-ui, sans-serif",
    fontSize: 28, fontWeight: 700, color: '#fff', marginBottom: 6,
  },
  subheading: { fontSize: 14, color: 'rgba(255,255,255,0.45)', marginBottom: 28 },
  socialGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 20 },
  socialBtn: {
    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
    padding: '11px 16px', borderRadius: 12,
    border: '1px solid rgba(255,255,255,0.12)',
    background: 'rgba(255,255,255,0.04)',
    color: '#e2e8f0', fontSize: 13, fontWeight: 500,
    cursor: 'pointer', transition: 'all 0.2s',
    fontFamily: "'DM Sans', system-ui, sans-serif",
  },
  divider: { display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 },
  divLine: { flex: 1, height: 1, background: 'rgba(255,255,255,0.08)' },
  divText: { fontSize: 12, color: 'rgba(255,255,255,0.3)', whiteSpace: 'nowrap' },
  field: { marginBottom: 16 },
  label: {
    display: 'block', fontSize: 12, fontWeight: 500,
    color: 'rgba(255,255,255,0.45)', marginBottom: 6,
    textTransform: 'uppercase', letterSpacing: '0.05em',
  },
  input: {
    width: '100%', padding: '11px 14px', borderRadius: 10,
    border: '1px solid rgba(255,255,255,0.1)',
    background: 'rgba(255,255,255,0.04)',
    color: '#e2e8f0', fontSize: 14,
    fontFamily: "'DM Sans', system-ui, sans-serif",
    outline: 'none', boxSizing: 'border-box',
  },
  errorBox: {
    background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
    borderRadius: 10, padding: '10px 14px',
    fontSize: 13, color: '#fca5a5', marginBottom: 16,
  },
  submitBtn: {
    width: '100%', padding: '13px 0', borderRadius: 12,
    background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
    color: '#fff', fontSize: 15, fontWeight: 600,
    border: 'none', cursor: 'pointer',
    fontFamily: "'Bricolage Grotesque', system-ui, sans-serif",
    marginBottom: 12, transition: 'all 0.2s',
  },
  legalText: { fontSize: 11, color: 'rgba(255,255,255,0.2)', textAlign: 'center', marginBottom: 12 },
  bottomLink: { textAlign: 'center', fontSize: 13, color: 'rgba(255,255,255,0.4)' },
  linkAccent: { color: '#818cf8', textDecoration: 'none', fontWeight: 500 },
}