import Link from 'next/link'
import { GraduationCap, Target, Users, Zap, Shield, Heart } from 'lucide-react'

export const metadata = {
  title: 'About AdmitGoal — Our Mission to Make Education Accessible',
  description: 'AdmitGoal was built to replace expensive education agents with free AI-powered scholarship guidance for students in Pakistan, India, Bangladesh, Africa and beyond.',
}

export default function AboutPage() {
  return (
    <div style={{ minHeight: '100vh', background: '#fafafa', fontFamily: "'Inter', -apple-system, sans-serif" }}>

      {/* NAV */}
      <nav style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(20px)', borderBottom: '1px solid #f0f0f0', height: '60px', display: 'flex', alignItems: 'center' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
            <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={18} color="white" />
            </div>
            <span style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.5px' }}>
              Admit<span style={{ color: '#4f46e5' }}>Goal</span>
            </span>
          </Link>
          <Link href="/" style={{ padding: '8px 18px', background: '#4f46e5', color: 'white', borderRadius: '10px', fontSize: '13px', fontWeight: '600', textDecoration: 'none' }}>
            Find Scholarships
          </Link>
        </div>
      </nav>

      {/* HERO */}
      <div style={{ paddingTop: '60px', background: 'linear-gradient(135deg, #0f172a, #1e1b4b, #312e81)' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '80px 24px', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.15)', color: 'rgba(255,255,255,0.8)', padding: '6px 16px', borderRadius: '100px', fontSize: '12px', fontWeight: '600', letterSpacing: '0.5px', textTransform: 'uppercase', marginBottom: '24px' }}>
            Our Story
          </div>
          <h1 style={{ fontSize: 'clamp(32px, 5vw, 52px)', fontWeight: '900', color: 'white', lineHeight: '1.1', letterSpacing: '-1.5px', marginBottom: '20px' }}>
            Education Should Not Cost
            <span style={{ display: 'block', background: 'linear-gradient(135deg, #a78bfa, #67e8f9)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              PKR 100,000 in Agent Fees
            </span>
          </h1>
          <p style={{ fontSize: '18px', color: 'rgba(255,255,255,0.65)', lineHeight: '1.7', maxWidth: '600px', margin: '0 auto' }}>
            We built AdmitGoal because we watched brilliant students from Pakistan, India and Africa get exploited by agents charging lakhs of rupees for information that should be free.
          </p>
        </div>
      </div>

      {/* MISSION */}
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '72px 24px' }}>

        {/* THE PROBLEM */}
        <div style={{ background: 'white', borderRadius: '20px', border: '1px solid #f0f0f0', padding: '48px', marginBottom: '24px' }}>
          <div style={{ width: '48px', height: '48px', background: '#fef2f2', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px' }}>
            <Target size={24} color="#ef4444" />
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '16px' }}>
            The Problem We Are Solving
          </h2>
          <p style={{ fontSize: '16px', color: '#475569', lineHeight: '1.8', marginBottom: '16px' }}>
            Every year, hundreds of thousands of students across Pakistan, India, Bangladesh and Africa miss life-changing scholarships — not because they are not smart enough, not because they do not qualify, but simply because they do not know where to look.
          </p>
          <p style={{ fontSize: '16px', color: '#475569', lineHeight: '1.8', marginBottom: '16px' }}>
            Those who do find out are often directed to agents who charge PKR 50,000 to PKR 100,000 — sometimes more — for guidance that is nothing more than filling out forms and sending emails. This is a broken system that benefits agents and hurts students.
          </p>
          <p style={{ fontSize: '16px', color: '#475569', lineHeight: '1.8' }}>
            We are changing that. Completely and permanently.
          </p>
        </div>

        {/* OUR SOLUTION */}
        <div style={{ background: 'white', borderRadius: '20px', border: '1px solid #f0f0f0', padding: '48px', marginBottom: '24px' }}>
          <div style={{ width: '48px', height: '48px', background: '#ede9fe', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px' }}>
            <Zap size={24} color="#7c3aed" />
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '16px' }}>
            What AdmitGoal Does
          </h2>
          <p style={{ fontSize: '16px', color: '#475569', lineHeight: '1.8', marginBottom: '24px' }}>
            AdmitGoal is a free AI-powered scholarship platform that does in seconds what agents charge lakhs for.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            {[
              ['Finds fresh scholarships daily', 'We automatically scrape hundreds of universities and government programs worldwide and update our database every 6 hours.'],
              ['Removes outdated listings', 'Every scholarship is verified for freshness. We never show you a scholarship with a deadline that has already passed.'],
              ['Finds official links', 'We always link directly to the official university or government website — never to a third party aggregator.'],
              ['AI guides your application', 'Our built-in AI assistant answers questions about eligibility, IELTS requirements, SOP writing, documents and more — instantly and for free.'],
            ].map(([title, desc]) => (
              <div key={title} style={{ background: '#fafafa', borderRadius: '14px', padding: '20px' }}>
                <div style={{ fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '8px' }}>{title}</div>
                <div style={{ fontSize: '13px', color: '#64748b', lineHeight: '1.65' }}>{desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* WHO WE SERVE */}
        <div style={{ background: 'white', borderRadius: '20px', border: '1px solid #f0f0f0', padding: '48px', marginBottom: '24px' }}>
          <div style={{ width: '48px', height: '48px', background: '#f0fdf4', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px' }}>
            <Users size={24} color="#059669" />
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '16px' }}>
            Who We Are Built For
          </h2>
          <p style={{ fontSize: '16px', color: '#475569', lineHeight: '1.8', marginBottom: '24px' }}>
            AdmitGoal is built specifically for students in developing countries who have the talent and the drive to study abroad but lack access to the right information and guidance.
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {['Pakistan', 'India', 'Bangladesh', 'Nigeria', 'Kenya', 'Ghana', 'Ethiopia', 'Sri Lanka', 'Nepal', 'Indonesia', 'Philippines', 'Egypt', 'Morocco', 'And every country in between'].map(country => (
              <span key={country} style={{ padding: '6px 16px', background: '#f0f4ff', color: '#4338ca', borderRadius: '100px', fontSize: '13px', fontWeight: '600' }}>
                {country}
              </span>
            ))}
          </div>
        </div>

        {/* OUR PROMISE */}
        <div style={{ background: 'linear-gradient(135deg, #0f172a, #1e1b4b)', borderRadius: '20px', padding: '48px', marginBottom: '24px', color: 'white' }}>
          <div style={{ width: '48px', height: '48px', background: 'rgba(255,255,255,0.1)', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px' }}>
            <Heart size={24} color="#f472b6" />
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: '800', letterSpacing: '-0.5px', marginBottom: '16px' }}>
            Our Promise to You
          </h2>
          <div style={{ display: 'grid', gap: '16px' }}>
            {[
              ['Always free', 'AdmitGoal will always be free for students. We earn through non-intrusive advertising and partner referrals — never by charging students.'],
              ['Always fresh', 'We update our scholarship database every 6 hours. Outdated scholarships are removed automatically. You only see opportunities you can actually apply for.'],
              ['Always honest', 'We link to official sources only. We do not take money to feature scholarships. We do not show fake opportunities. What you see is real.'],
            ].map(([title, desc]) => (
              <div key={title} style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '14px', padding: '20px' }}>
                <div style={{ fontSize: '14px', fontWeight: '700', color: 'white', marginBottom: '8px' }}>{title}</div>
                <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)', lineHeight: '1.65' }}>{desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div style={{ textAlign: 'center', padding: '48px 0' }}>
          <h2 style={{ fontSize: '28px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '12px' }}>
            Ready to find your scholarship?
          </h2>
          <p style={{ fontSize: '16px', color: '#64748b', marginBottom: '28px' }}>
            Join thousands of students who found their path without paying an agent.
          </p>
          <Link href="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '14px 32px', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', color: 'white', borderRadius: '14px', fontSize: '15px', fontWeight: '700', textDecoration: 'none', boxShadow: '0 8px 24px rgba(79,70,229,0.25)' }}>
            Browse Scholarships
          </Link>
        </div>
      </div>

      {/* FOOTER */}
      <footer style={{ background: '#0f172a', color: 'white' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '48px 24px', textAlign: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={18} color="white" />
            </div>
            <span style={{ fontSize: '18px', fontWeight: '800' }}>Admit<span style={{ color: '#818cf8' }}>Goal</span></span>
          </div>
          <p style={{ color: '#475569', fontSize: '13px', marginBottom: '20px' }}>Free AI scholarship finder for students worldwide</p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '24px' }}>
            {[['Home', '/'], ['Privacy Policy', '/privacy'], ['Contact', '/contact']].map(([l, h]) => (
              <Link key={l} href={h} style={{ color: '#475569', fontSize: '13px', textDecoration: 'none' }}>{l}</Link>
            ))}
          </div>
          <p style={{ color: '#1e293b', fontSize: '12px', marginTop: '32px' }}>© {new Date().getFullYear()} AdmitGoal · Replacing agents with AI</p>
        </div>
      </footer>
    </div>
  )
}