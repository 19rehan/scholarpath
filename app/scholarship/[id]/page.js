'use client'
import { useEffect, useState } from 'react'
import { supabase } from '../../../lib/supabase'
import Link from 'next/link'
import { GraduationCap, MapPin, Clock, ExternalLink, ChevronRight, ArrowLeft, Send } from 'lucide-react'

export default function ScholarshipPage({ params }) {
  const [scholarship, setScholarship] = useState(null)
  const [loading, setLoading] = useState(true)
  const [resolvedId, setResolvedId] = useState(null)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [asking, setAsking] = useState(false)

  useEffect(() => {
    async function resolveParams() {
      const resolved = await params
      setResolvedId(resolved.id)
    }
    resolveParams()
  }, [])

  useEffect(() => {
    if (resolvedId) fetchScholarship()
  }, [resolvedId])

  async function fetchScholarship() {
    const { data, error } = await supabase
      .from('scholarship_details')
      .select('*')
      .eq('id', resolvedId)
      .single()
    if (error) console.error(error)
    setScholarship(data)
    setLoading(false)
  }

  async function askAI() {
    if (!question.trim() || !scholarship) return
    setAsking(true)
    setAnswer('')
    const q = question.toLowerCase()
    const s = scholarship
    let ans = ''

    if (q.includes('ielts') || q.includes('english') || q.includes('language')) {
      ans = `<strong>Language Requirement:</strong> ${s.language_requirement || 'Check website'}<br><br><strong>IELTS Score:</strong> ${s.ielts_score || 'Not required'}<br><br>Start IELTS preparation at least 3 months before the deadline. British Council and IDP offer tests in Karachi, Lahore and Islamabad.`
    } else if (q.includes('deadline') || q.includes('last date') || q.includes('when')) {
      ans = `<strong>Application Deadline:</strong> ${s.deadline || 'See official website'}<br><br>Always verify on the official website as deadlines can change. Apply at least 2 weeks before to avoid last minute issues.`
    } else if (q.includes('pakistan') || q.includes('eligible') || q.includes('who can') || q.includes('nationality')) {
      ans = `<strong>Eligibility:</strong><br>${s.eligible_countries?.slice(0, 400) || 'Check official website'}<br><br>Pakistani, Indian and Bangladeshi students are generally welcomed for international scholarships.`
    } else if (q.includes('sop') || q.includes('statement') || q.includes('essay')) {
      ans = `<strong>SOP Structure:</strong><br><br>Para 1: Powerful personal story<br>Para 2: Academic background and GPA<br>Para 3: Why this specific scholarship<br>Para 4: Your 5-year career goals<br>Para 5: Why you deserve it<br>Para 6: Strong confident closing<br><br>Keep it 600 to 1000 words.`
    } else if (q.includes('document') || q.includes('require') || q.includes('need')) {
      ans = `<strong>Documents Required:</strong><br><br>Valid Passport<br>Academic Transcripts<br>Degree Certificate<br>IELTS Certificate (if required)<br>Statement of Purpose<br>2 to 3 Recommendation Letters<br>Updated CV<br>Passport Photos<br><br>Prepare everything 1 month before deadline.`
    } else if (q.includes('fund') || q.includes('cover') || q.includes('money') || q.includes('stipend')) {
      ans = `<strong>Funding:</strong> ${s.funding_type || 'Check official website'}<br><br>${s.benefits?.slice(0, 300) || 'Visit the official website for complete funding details.'}`
    } else {
      ans = `Based on available information about <strong>${s.title}</strong>:<br><br>${s.full_description?.slice(0, 350) || 'Please visit the official website.'}<br><br>You can ask about: eligibility, IELTS requirements, deadline, documents, SOP writing, or funding.`
    }
    setAnswer(ans)
    setAsking(false)
  }

  function convertToHtml(text) {
    if (!text) return ''
    text = text.replace(/^# (.+)$/gm, '<h1 style="font-size:26px;font-weight:800;color:#0f172a;margin:0 0 20px;letter-spacing:-0.5px">$1</h1>')
    text = text.replace(/^## (.+)$/gm, '<h2 style="font-size:19px;font-weight:700;color:#4f46e5;margin:32px 0 12px;padding-left:14px;border-left:4px solid #4f46e5">$1</h2>')
    text = text.replace(/^### (.+)$/gm, '<h3 style="font-size:16px;font-weight:700;color:#0f172a;margin:20px 0 8px">$1</h3>')
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong style="color:#4f46e5;font-weight:700">$1</strong>')
    text = text.replace(/^[-*] (.+)$/gm, '<li style="font-size:14px;line-height:2;color:#475569;margin:2px 0">$1</li>')
    text = text.replace(/(<li.*?<\/li>\n?)+/gs, m => `<ul style="padding-left:20px;margin:12px 0">${m}</ul>`)
    text = text.replace(/^---$/gm, '<hr style="border:none;border-top:1px solid #f0f0f0;margin:28px 0">')
    const lines = text.split('\n')
    const result = []
    let inTable = false
    let firstRow = true
    for (const line of lines) {
      if (line.includes('|') && line.trim().startsWith('|')) {
        if (!inTable) { result.push('<table style="width:100%;border-collapse:collapse;margin:20px 0;border:1px solid #f0f0f0;border-radius:10px;overflow:hidden">'); inTable = true; firstRow = true }
        if (/\|[\s\-|]+\|/.test(line)) continue
        const cols = line.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim())
        if (firstRow) {
          result.push('<thead><tr>' + cols.map(c => `<th style="padding:12px 16px;text-align:left;font-size:12px;font-weight:700;color:#4f46e5;background:#f0f4ff;text-transform:uppercase;letter-spacing:0.5px">${c}</th>`).join('') + '</tr></thead><tbody>')
          firstRow = false
        } else {
          result.push('<tr>' + cols.map(c => `<td style="padding:12px 16px;font-size:14px;color:#475569;border-top:1px solid #f8fafc">${c}</td>`).join('') + '</tr>')
        }
      } else {
        if (inTable) { result.push('</tbody></table>'); inTable = false }
        result.push(line)
      }
    }
    if (inTable) result.push('</tbody></table>')
    text = result.join('\n')
    text = text.replace(/\n\n+/g, '</p><p style="font-size:15px;line-height:1.8;color:#475569;margin-bottom:14px">')
    return `<p style="font-size:15px;line-height:1.8;color:#475569;margin-bottom:14px">${text}</p>`
  }

  if (loading) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fafafa' }}>
      <div style={{ color: '#4f46e5', fontWeight: '600', fontFamily: 'Inter, sans-serif' }}>Loading...</div>
    </div>
  )

  if (!scholarship) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fafafa' }}>
      <div style={{ textAlign: 'center' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '16px', fontFamily: 'Inter, sans-serif' }}>Scholarship not found</h2>
        <Link href="/" style={{ padding: '12px 24px', background: '#4f46e5', color: 'white', borderRadius: '12px', textDecoration: 'none', fontWeight: '600' }}>Go Back</Link>
      </div>
    </div>
  )

  const s = scholarship
  const isFullyFunded = s.funding_type?.toLowerCase().includes('full') || s.title?.toLowerCase().includes('fully funded')
  const noIelts = s.ielts_score === 'Not required' || s.ielts_score === 'Not mentioned'

  return (
    <div style={{ minHeight: '100vh', background: '#fafafa', fontFamily: "'Inter', -apple-system, sans-serif" }}>

      {/* NAV */}
      <nav style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(20px)', borderBottom: '1px solid #f0f0f0', height: '60px', display: 'flex', alignItems: 'center' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
            <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={18} color="white" />
            </div>
            <span style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.5px' }}>Admit<span style={{ color: '#4f46e5' }}>Goal</span></span>
          </Link>
          <a href={s.scholarship_link} target="_blank" rel="noopener noreferrer"
            style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '9px 20px', background: '#059669', color: 'white', borderRadius: '10px', fontSize: '13px', fontWeight: '600', textDecoration: 'none' }}>
            Apply Now <ExternalLink size={14} />
          </a>
        </div>
      </nav>

      {/* HERO */}
      <div style={{ paddingTop: '60px', background: 'linear-gradient(135deg, #0f172a, #1e1b4b, #312e81)' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '48px 24px' }}>
          <Link href="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'rgba(255,255,255,0.5)', fontSize: '13px', textDecoration: 'none', marginBottom: '24px' }}>
            <ArrowLeft size={14} /> Back to scholarships
          </Link>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
            {s.university_name && <span style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.15)', color: 'rgba(255,255,255,0.8)', padding: '4px 14px', borderRadius: '100px', fontSize: '12px', fontWeight: '600' }}>{s.university_name}</span>}
            {s.region && <span style={{ background: 'rgba(79,70,229,0.3)', border: '1px solid rgba(99,102,241,0.4)', color: '#a5b4fc', padding: '4px 14px', borderRadius: '100px', fontSize: '12px', fontWeight: '600' }}>{s.region}</span>}
          </div>
          <h1 style={{ fontSize: 'clamp(24px, 4vw, 40px)', fontWeight: '800', color: 'white', lineHeight: '1.2', marginBottom: '20px', letterSpacing: '-0.5px', maxWidth: '800px' }}>
            {s.seo_title || s.title}
          </h1>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {s.country && <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', color: 'rgba(255,255,255,0.8)', padding: '7px 16px', borderRadius: '100px', fontSize: '13px', fontWeight: '500' }}><MapPin size={13} />{s.country}</div>}
            {s.degree_level && <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', color: 'rgba(255,255,255,0.8)', padding: '7px 16px', borderRadius: '100px', fontSize: '13px', fontWeight: '500' }}><GraduationCap size={13} />{s.degree_level}</div>}
            {s.deadline && s.deadline !== 'See official website' && <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)', color: '#fca5a5', padding: '7px 16px', borderRadius: '100px', fontSize: '13px', fontWeight: '500' }}><Clock size={13} />{s.deadline}</div>}
            {isFullyFunded && <div style={{ background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)', color: '#6ee7b7', padding: '7px 16px', borderRadius: '100px', fontSize: '13px', fontWeight: '500' }}>Fully Funded</div>}
            {noIelts && <div style={{ background: 'rgba(20,184,166,0.15)', border: '1px solid rgba(20,184,166,0.3)', color: '#5eead4', padding: '7px 16px', borderRadius: '100px', fontSize: '13px', fontWeight: '500' }}>No IELTS Required</div>}
          </div>
        </div>
      </div>

      {/* CONTENT */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '32px' }}>

          {/* LEFT */}
          <div>
            {/* QUICK INFO */}
            <div style={{ background: 'white', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '24px', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: '700', color: '#0f172a', marginBottom: '20px' }}>Quick Overview</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                {[
                  ['University', s.university_name || 'Check website'],
                  ['Country', s.country || 'International'],
                  ['Degree Level', s.degree_level || 'All levels'],
                  ['Funding Type', s.funding_type || 'Check website'],
                  ['Deadline', s.deadline || 'See website'],
                  ['IELTS Required', s.ielts_score || 'Not required'],
                  ['Min GPA', s.gpa_required || 'Check website'],
                  ['Language', s.language_requirement || 'Check website'],
                ].map(([label, value]) => (
                  <div key={label} style={{ background: '#fafafa', borderRadius: '12px', padding: '14px' }}>
                    <div style={{ fontSize: '11px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>{label}</div>
                    <div style={{ fontSize: '14px', fontWeight: '600', color: '#0f172a' }}>{value}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* BLOG */}
            <div style={{ background: 'white', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '32px' }}>
              <div dangerouslySetInnerHTML={{ __html: convertToHtml(s.blog_post) }} />
            </div>
          </div>

          {/* SIDEBAR */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

            {/* APPLY */}
            <a href={s.scholarship_link} target="_blank" rel="noopener noreferrer"
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '16px', background: 'linear-gradient(135deg, #059669, #10b981)', color: 'white', borderRadius: '14px', textDecoration: 'none', fontSize: '16px', fontWeight: '700', boxShadow: '0 8px 24px rgba(16,185,129,0.25)' }}>
              Apply Now — Official Site <ExternalLink size={16} />
            </a>

            {/* KEY DETAILS */}
            <div style={{ background: 'white', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '20px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '16px' }}>Key Details</h3>
              {[
                ['Deadline', s.deadline || 'See website', '#dc2626'],
                ['Level', s.degree_level || 'All levels', '#0f172a'],
                ['Funding', s.funding_type || 'Check website', '#059669'],
                ['IELTS', s.ielts_score || 'Not required', '#d97706'],
                ['GPA', s.gpa_required || 'Check website', '#0f172a'],
              ].map(([label, value, color]) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid #fafafa' }}>
                  <span style={{ fontSize: '13px', color: '#94a3b8', fontWeight: '500' }}>{label}</span>
                  <span style={{ fontSize: '13px', fontWeight: '700', color }}>{value}</span>
                </div>
              ))}
            </div>

            {/* AI ASSISTANT */}
            <div style={{ background: 'linear-gradient(135deg, #0f172a, #1e1b4b)', borderRadius: '16px', padding: '20px', color: 'white' }}>
              <h3 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '6px' }}>AI Assistant</h3>
              <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginBottom: '16px', lineHeight: '1.6' }}>
                Ask about eligibility, IELTS, SOP, documents and more.
              </p>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                <input
                  type="text"
                  value={question}
                  onChange={e => setQuestion(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && askAI()}
                  placeholder="Can Pakistani students apply?"
                  style={{ flex: 1, background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '10px', padding: '10px 14px', color: 'white', fontSize: '13px', outline: 'none', fontFamily: 'inherit' }}
                />
                <button onClick={askAI} disabled={asking}
                  style={{ padding: '10px 14px', background: '#4f46e5', border: 'none', borderRadius: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                  <Send size={14} color="white" />
                </button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
                {['IELTS required?', 'Who can apply?', 'Documents needed?', 'How to write SOP?'].map(q => (
                  <button key={q} onClick={() => setQuestion(q)}
                    style={{ textAlign: 'left', fontSize: '12px', color: 'rgba(255,255,255,0.5)', background: 'rgba(255,255,255,0.05)', border: 'none', borderRadius: '8px', padding: '8px 12px', cursor: 'pointer', fontFamily: 'inherit' }}>
                    {q}
                  </button>
                ))}
              </div>
              {asking && <div style={{ background: 'rgba(255,255,255,0.08)', borderRadius: '10px', padding: '12px', fontSize: '13px', color: 'rgba(255,255,255,0.6)' }}>Thinking...</div>}
              {answer && <div style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '10px', padding: '14px', fontSize: '13px', color: 'rgba(255,255,255,0.85)', lineHeight: '1.7' }} dangerouslySetInnerHTML={{ __html: answer }} />}
            </div>

            {/* EXPLORE MORE */}
            <div style={{ background: 'white', borderRadius: '16px', border: '1px solid #f0f0f0', padding: '20px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '14px' }}>Explore More</h3>
              {[
                [`More from ${s.country || 'International'}`, `/search?q=${s.country || 'international'}`],
                ['Fully Funded Scholarships', '/search?q=fully+funded'],
                ['No IELTS Required', '/search?q=no+ielts'],
                ['PhD Scholarships', '/search?q=phd'],
              ].map(([label, href]) => (
                <Link key={label} href={href}
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 12px', borderRadius: '10px', background: '#fafafa', textDecoration: 'none', color: '#475569', fontSize: '13px', fontWeight: '500', marginBottom: '8px' }}
                  onMouseEnter={e => { e.currentTarget.style.background = '#f0f4ff'; e.currentTarget.style.color = '#4f46e5' }}
                  onMouseLeave={e => { e.currentTarget.style.background = '#fafafa'; e.currentTarget.style.color = '#475569' }}>
                  {label} <ChevronRight size={14} />
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* FOOTER */}
      <footer style={{ background: '#0f172a', color: 'white', marginTop: '60px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '48px 24px', textAlign: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <GraduationCap size={18} color="white" />
            </div>
            <span style={{ fontSize: '18px', fontWeight: '800' }}>Admit<span style={{ color: '#818cf8' }}>Goal</span></span>
          </div>
          <p style={{ color: '#475569', fontSize: '13px', marginBottom: '20px' }}>Free AI scholarship finder for students worldwide</p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '24px' }}>
            {[['About', '/about'], ['Privacy', '/privacy'], ['Contact', '/contact']].map(([l, h]) => (
              <Link key={l} href={h} style={{ color: '#475569', fontSize: '13px', textDecoration: 'none' }}>{l}</Link>
            ))}
          </div>
          <p style={{ color: '#1e293b', fontSize: '12px', marginTop: '32px' }}>© {new Date().getFullYear()} AdmitGoal</p>
        </div>
      </footer>
    </div>
  )
}