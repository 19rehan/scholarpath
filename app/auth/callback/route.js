// app/auth/callback/route.js
import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

export async function GET(request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/'

  if (!code) {
    return NextResponse.redirect(`${origin}/login?error=no_code`)
  }

  try {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    )

    const { data, error } = await supabase.auth.exchangeCodeForSession(code)

    if (error || !data?.user) {
      console.error('OAuth error:', error)
      return NextResponse.redirect(`${origin}/login?error=auth_failed`)
    }

    // Check if user already has a profile
    const { data: profile } = await supabase
      .from('user_profiles')
      .select('id')
      .eq('user_id', data.user.id)
      .single()

    // New user → create profile first
    // Existing user → go to homepage
    const redirectUrl = profile
      ? `${origin}${next}`
      : `${origin}/profile/create`

    return NextResponse.redirect(redirectUrl)

  } catch (err) {
    console.error('Callback error:', err)
    return NextResponse.redirect(`${origin}/login?error=server_error`)
  }
}