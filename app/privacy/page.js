import Link from 'next/link'
import { GraduationCap, Shield } from 'lucide-react'

export const metadata = {
  title: 'Privacy Policy — AdmitGoal',
  description: 'AdmitGoal privacy policy. How we collect, use and protect your data.',
}

export default function PrivacyPage() {
  const sections = [
    {
      title: 'Information We Collect',
      content: [
        {
          subtitle: 'Information you provide',
          text: 'When you use our scholarship search and matching features, we may collect information such as your country of origin, field of study, degree level and language test scores. This information is used solely to match you with relevant scholarships and improve our recommendations.'
        },
        {
          subtitle: 'Information collected automatically',
          text: 'When you visit AdmitGoal, we automatically collect certain information including your IP address, browser type, pages visited, time spent on pages and referring URLs. This data is used in aggregate form to understand how our platform is being used and to improve the experience.'
        },
        {
          subtitle: 'Cookies',
          text: 'We use cookies and similar tracking technologies to improve your experience on our platform. Cookies help us remember your preferences and understand how you interact with our content. You can disable cookies through your browser settings, though this may affect certain features.'
        }
      ]
    },
    {
      title: 'How We Use Your Information',
      content: [
        {
          subtitle: 'Scholarship matching',
          text: 'Information you provide about your academic background and preferences is used to show you relevant scholarships and filter results based on your eligibility.'
        },
        {
          subtitle: 'Platform improvement',
          text: 'We analyse usage patterns to understand which scholarships are most relevant to our users, improve our AI guidance system and fix issues with the platform.'
        },
        {
          subtitle: 'Communications',
          text: 'If you opt in to notifications, we may send you alerts about new scholarships matching your profile or upcoming deadlines. You can unsubscribe at any time.'
        }
      ]
    },
    {
      title: 'Advertising',
      content: [
        {
          subtitle: 'Google AdSense',
          text: 'AdmitGoal uses Google AdSense to display non-intrusive advertisements. Google may use cookies to serve ads based on your visits to this and other websites. You can opt out of personalised advertising by visiting Google\'s Ads Settings page. We do not allow advertisers to pay to have their scholarships featured or promoted — our scholarship listings are based entirely on quality and relevance.'
        },
        {
          subtitle: 'Partner referrals',
          text: 'We may earn a referral fee when users sign up for services such as IELTS preparation courses or student accommodation through links on our platform. These partnerships never influence which scholarships we show or how we rank them.'
        }
      ]
    },
    {
      title: 'Data Sharing',
      content: [
        {
          subtitle: 'We do not sell your data',
          text: 'AdmitGoal does not sell, rent or trade your personal information to third parties. Ever. Your data is used only to improve your experience on our platform.'
        },
        {
          subtitle: 'Service providers',
          text: 'We use trusted third-party services including Supabase for database hosting and Vercel for platform hosting. These providers are bound by strict data protection agreements and only process data as necessary to provide their services.'
        },
        {
          subtitle: 'Legal requirements',
          text: 'We may disclose information if required to do so by law or in response to valid legal requests from public authorities.'
        }
      ]
    },
    {
      title: 'Data Security',
      content: [
        {
          subtitle: 'How we protect your data',
          text: 'We implement industry-standard security measures including encrypted connections (HTTPS), secure database storage and regular security audits. While no system is completely secure, we take every reasonable precaution to protect your information.'
        }
      ]
    },
    {
      title: 'Your Rights',
      content: [
        {
          subtitle: 'Access and deletion',
          text: 'You have the right to access the personal information we hold about you and to request its deletion. To make such a request, contact us at privacy@admitgoal.com.'
        },
        {
          subtitle: 'Opt out',
          text: 'You can opt out of analytics tracking by using browser privacy settings or a tracking blocker. You can opt out of personalised ads through Google\'s Ads Settings.'
        }
      ]
    },
    {
      title: 'Changes to This Policy',
      content: [
        {
          subtitle: 'Updates',
          text: 'We may update this privacy policy from time to time. When we do, we will update the "Last Updated" date at the top of this page. We encourage you to review this policy periodically.'
        }
      ]
    }
  ]

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
      <div style={{ paddingTop: '60px', background: 'linear-gradient(135deg, #0f172a, #1e1b4b)' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '60px 24px', textAlign: 'center' }}>
          <div style={{ width: '56px', height: '56px', background: 'rgba(255,255,255,0.1)', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
            <Shield size={28} color="white" />
          </div>
          <h1 style={{ fontSize: '40px', fontWeight: '900', color: 'white', letterSpacing: '-1px', marginBottom: '12px' }}>
            Privacy Policy
          </h1>
          <p style={{ fontSize: '15px', color: 'rgba(255,255,255,0.5)' }}>
            Last updated: May 2026
          </p>
        </div>
      </div>

      {/* CONTENT */}
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '48px 24px' }}>

        {/* INTRO */}
        <div style={{ background: 'white', borderRadius: '20px', border: '1px solid #f0f0f0', padding: '32px', marginBottom: '16px' }}>
          <p style={{ fontSize: '16px', color: '#475569', lineHeight: '1.8' }}>
            AdmitGoal is committed to protecting your privacy. This policy explains clearly what data we collect, why we collect it, how we use it and what rights you have. We believe in transparency — if you have any questions after reading this, contact us directly at <a href="mailto:privacy@admitgoal.com" style={{ color: '#4f46e5', textDecoration: 'none', fontWeight: '600' }}>privacy@admitgoal.com</a>.
          </p>
        </div>

        {/* SECTIONS */}
        {sections.map((section, i) => (
          <div key={i} style={{ background: 'white', borderRadius: '20px', border: '1px solid #f0f0f0', padding: '32px', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.3px', marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid #f0f0f0' }}>
              {section.title}
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {section.content.map((item, j) => (
                <div key={j}>
                  <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '8px' }}>
                    {item.subtitle}
                  </h3>
                  <p style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.75' }}>
                    {item.text}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* CONTACT */}
        <div style={{ background: 'linear-gradient(135deg, #0f172a, #1e1b4b)', borderRadius: '20px', padding: '32px', textAlign: 'center', color: 'white' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '800', marginBottom: '12px' }}>Questions about your privacy?</h2>
          <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.6)', marginBottom: '20px', lineHeight: '1.7' }}>
            We are always happy to explain how we handle your data. Reach out and we will respond within 24 hours.
          </p>
          <a href="mailto:privacy@admitgoal.com" style={{ display: 'inline-block', padding: '12px 28px', background: '#4f46e5', color: 'white', borderRadius: '12px', fontSize: '14px', fontWeight: '600', textDecoration: 'none' }}>
            privacy@admitgoal.com
          </a>
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
            {[['Home', '/'], ['About', '/about'], ['Contact', '/contact']].map(([l, h]) => (
              <Link key={l} href={h} style={{ color: '#475569', fontSize: '13px', textDecoration: 'none' }}>{l}</Link>
            ))}
          </div>
          <p style={{ color: '#1e293b', fontSize: '12px', marginTop: '24px' }}>© {new Date().getFullYear()} AdmitGoal</p>
        </div>
      </footer>
    </div>
  )
}