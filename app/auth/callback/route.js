// app/auth/callback/route.js
// Handles OAuth redirect callbacks from Supabase

import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

export async function GET(request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/'

  if (code) {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    )
    const { data, error } = await supabase.auth.exchangeCodeForSession(code)

    if (!error) {
      // Check if user has a profile — if not, show the complete-profile modal
      const { data: profile } = await supabase
        .from('user_profiles')
        .select('id')
        .eq('user_id', data.user.id)
        .single()

      const redirectUrl = profile
        ? `${origin}${next}`
        : `${origin}/?new_user=true`

      return NextResponse.redirect(redirectUrl)
    }
  }

  return NextResponse.redirect(`${origin}/login?error=auth_callback_failed`)
}