// lib/supabase-auth.js
import { supabase } from './supabase'

// ── Cache helpers ──────────────────────────────────────────────────
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

function setCache(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify({ value, ts: Date.now() }))
  } catch {}
}

function getCache(key) {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return null
    const { value, ts } = JSON.parse(raw)
    if (Date.now() - ts > CACHE_TTL) {
      localStorage.removeItem(key)
      return null
    }
    return value
  } catch {
    return null
  }
}

export function clearCache(userId) {
  try {
    localStorage.removeItem(`profile_${userId}`)
    localStorage.removeItem(`dashboard_${userId}`)
    localStorage.removeItem(`saved_${userId}`)
  } catch {}
}

// ── Fast user check (session only - no server roundtrip) ───────────
export async function getUser() {
  const { data: { session } } = await supabase.auth.getSession()
  return session?.user ?? null
}

// ── Profile (cached 5 min) ─────────────────────────────────────────
export async function getUserProfile(userId) {
  const cacheKey = `profile_${userId}`
  const cached = getCache(cacheKey)
  if (cached) return cached

  const { data } = await supabase
    .from('user_profiles')
    .select('*')
    .eq('user_id', userId)
    .single()

  if (data) setCache(cacheKey, data)
  return data
}

// ── Dashboard data (all in ONE parallel batch, cached 5 min) ───────
export async function getDashboardData(userId) {
  const cacheKey = `dashboard_${userId}`
  const cached = getCache(cacheKey)
  if (cached) return cached

  // All 4 queries fire at the SAME TIME
  const [savedCountRes, savedRes, appliedCountRes, appliedRes] = await Promise.all([
    supabase
      .from('user_saved_scholarships')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', userId),

    supabase
      .from('user_saved_scholarships')
      .select('id, saved_at, scholarship_id, scholarship_details(id, title, country, deadline, funding_type)')
      .eq('user_id', userId)
      .order('saved_at', { ascending: false })
      .limit(3),

    supabase
      .from('user_applications')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', userId),

    supabase
      .from('user_applications')
      .select('id, status, applied_at, scholarship_id, scholarship_details(id, title, country, deadline)')
      .eq('user_id', userId)
      .order('applied_at', { ascending: false })
      .limit(3),
  ])

  const result = {
    savedCount: savedCountRes.count || 0,
    recentSaved: savedRes.data || [],
    appliedCount: appliedCountRes.count || 0,
    recentApplied: appliedRes.data || [],
  }

  setCache(cacheKey, result)
  return result
}

// ── Saved scholarships (cached 5 min) ─────────────────────────────
export async function getSavedScholarships(userId) {
  const cacheKey = `saved_${userId}`
  const cached = getCache(cacheKey)
  if (cached) return cached

  const { data } = await supabase
    .from('user_saved_scholarships')
    .select('id, saved_at, scholarship_id, scholarship_details(*)')
    .eq('user_id', userId)
    .order('saved_at', { ascending: false })

  const result = data || []
  setCache(cacheKey, result)
  return result
}

// ── Auth functions ─────────────────────────────────────────────────
export async function signUpWithEmail(fullName, email, password) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { data: { full_name: fullName } },
  })
  return { data, error }
}

export async function signInWithEmail(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password })
  return { data, error }
}

export async function signInWithGoogle() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: `${window.location.origin}/auth/callback` },
  })
  return { data, error }
}

export async function signInWithFacebook() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'facebook',
    options: { redirectTo: `${window.location.origin}/auth/callback` },
  })
  return { data, error }
}

export async function signInWithApple() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'apple',
    options: { redirectTo: `${window.location.origin}/auth/callback` },
  })
  return { data, error }
}

export async function signInWithMicrosoft() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'azure',
    options: {
      scopes: 'email',
      redirectTo: `${window.location.origin}/auth/callback`,
    },
  })
  return { data, error }
}

export async function sendPasswordResetEmail(email) {
  const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${window.location.origin}/auth/reset-password`,
  })
  return { data, error }
}
export async function signOut() {
  const { error } = await supabase.auth.signOut()
  return { error }
}

export async function getSession() {
  const { data: { session } } = await supabase.auth.getSession()
  return session
}
