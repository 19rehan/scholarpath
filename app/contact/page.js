import Link from 'next/link'
import { GraduationCap, Mail, MessageCircle, Handshake, Clock } from 'lucide-react'

export const metadata = {
  title: 'Contact AdmitGoal — Get in Touch',
  description: 'Contact AdmitGoal for partnership inquiries, feedback or support. We respond within 24 hours.',
}

export default function ContactPage() {
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
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '60px 24px', textAlign: 'center' }}>
          <h1 style={{ fontSize: 'clamp(32px, 5vw, 48px)', fontWeight: '900', color: 'white', letterSpacing: '-1px', marginBottom: '16px' }}>
            Get in Touch
          </h1>
          <p style={{ fontSize: '17px', color: 'rgba(255,255,255,0.6)', lineHeight: '1.7' }}>
            Whether you are a student with a question, a partner looking to collaborate, or someone who wants to make AdmitGoal better — we want to hear from you.
          </p>
        </div>
      </div>

      {/* CONTACT OPTIONS */}
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '48px 24px' }}>

        {/* RESPONSE TIME */}
        <div style={{ background: '#f0f4ff', border: '1px solid #c7d2fe', borderRadius: '14px', padding: '16px 20px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Clock size={18} color="#4f46e5" />
          <span style={{ fontSize: '14px', color: '#4338ca', fontWeight: '500' }}>
            We respond to all inquiries within 24 hours, usually much faster.
          </span>
        </div>

        {/* CONTACT CARDS */}
        <div style={{ display: 'grid', gap: '16px', marginBottom: '32px' }}>

          {/* GENERAL */}
          <div style={{ background: 'white', borderRadius: '20px', border: '1px solid #f0f0f0', padding: '32px', display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
            <div style={{ width: '48px', height: '48px', background: '#ede9fe', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Mail size={22} color="#7c3aed" />
            </div>
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.3px', marginBottom: '8px' }}>General Inquiries</h2>
              <p style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.7', marginBottom: '16px' }}>
                Questions about scholarships, how AdmitGoal works, or anything else — reach out and our team will help you.
              </p>
              <a href="mailto:contact@admitgoal.com" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 20px', background: '#4f46e5', color: 'white', borderRadius: '10px', fontSize: '14px', fontWeight: '600', textDecoration: 'none' }}>
                contact@admitgoal.com
              </a>
            </div>
          </div>

          {/* PARTNERSHIPS */}
          <div style={{ background: 'white', borderRadius: '20px', border: '1px solid #f0f0f0', padding: '32px', display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
            <div style={{ width: '48px', height: '48px', background: '#f0fdf4', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Handshake size={22} color="#059669" />
            </div>
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.3px', marginBottom: '8px' }}>Partnership Inquiries</h2>
              <p style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.7', marginBottom: '12px' }}>
                We work with IELTS and PTE preparation academies, student accommodation providers, airlines with student discounts, SIM card providers, universities and education-focused businesses.
              </p>
              <p style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.7', marginBottom: '16px' }}>
                If you offer a product or service that genuinely helps students study abroad, we would love to talk about how we can work together to reach our growing audience.
              </p>
              <a href="mailto:partner@admitgoal.com" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 20px', background: '#059669', color: 'white', borderRadius: '10px', fontSize: '14px', fontWeight: '600', textDecoration: 'none' }}>
                partner@admitgoal.com
              </a>
            </div>
          </div>

          {/* FEEDBACK */}
          <div style={{ background: 'white', borderRadius: '20px', border: '1px solid #f0f0f0', padding: '32px', display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
            <div style={{ width: '48px', height: '48px', background: '#fff7ed', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <MessageCircle size={22} color="#d97706" />
            </div>
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.3px', marginBottom: '8px' }}>Feedback & Suggestions</h2>
              <p style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.7', marginBottom: '16px' }}>
                Found a scholarship with an incorrect deadline? Noticed something broken? Have an idea that would make AdmitGoal better for students? We genuinely want to know. Every piece of feedback helps us improve.
              </p>
              <a href="mailto:feedback@admitgoal.com" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 20px', background: '#d97706', color: 'white', borderRadius: '10px', fontSize: '14px', fontWeight: '600', textDecoration: 'none' }}>
                feedback@admitgoal.com
              </a>
            </div>
          </div>
        </div>

        {/* WHAT WE DON'T DO */}
        <div style={{ background: '#fafafa', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '24px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>Please note</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {[
              'We do not provide individual visa application assistance',
              'We do not fill out scholarship applications on behalf of students',
              'We do not guarantee scholarship results or admission outcomes',
              'We do not charge any fees for our guidance or information',
            ].map((note, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <div style={{ width: '6px', height: '6px', background: '#94a3b8', borderRadius: '50%', marginTop: '7px', flexShrink: 0 }} />
                <span style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.6' }}>{note}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* FOOTER */}
      <footer style={{ background: '#0f172a', color: 'white', marginTop: '40px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '48px 24px', textAlign: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={18} color="white" />
            </div>
            <span style={{ fontSize: '18px', fontWeight: '800' }}>Admit<span style={{ color: '#818cf8' }}>Goal</span></span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '24px' }}>
            {[['Home', '/'], ['About', '/about'], ['Privacy', '/privacy']].map(([l, h]) => (
              <Link key={l} href={h} style={{ color: '#475569', fontSize: '13px', textDecoration: 'none' }}>{l}</Link>
            ))}
          </div>
          <p style={{ color: '#1e293b', fontSize: '12px', marginTop: '24px' }}>© {new Date().getFullYear()} AdmitGoal</p>
        </div>
      </footer>
    </div>
  )
}