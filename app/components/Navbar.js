'use client';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { getUser, signOut } from '@/lib/supabase-auth';
import { GraduationCap } from 'lucide-react';

export default function Navbar() {
  const [user, setUser] = useState(null);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkUser() {
      const currentUser = await getUser();
      setUser(currentUser);
      setLoading(false);
    }
    checkUser();
  }, []);

  async function handleLogout() {
    await signOut();
    setUser(null);
    setShowProfileMenu(false);
    window.location.href = '/';
  }

  return (
    <div style={{ padding: '12px 0', background: '#ffffff', position: 'sticky', top: 0, zIndex: 100 }}>
      <nav style={{
        width: '96%',
        maxWidth: '1400px',
        margin: '0 auto',
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(79, 70, 229, 0.1)',
        borderRadius: '24px',
        padding: '16px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 20px 60px rgba(79, 70, 229, 0.08)',
      }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '14px', textDecoration: 'none' }}>
          <div style={{
            width: '48px', height: '48px',
            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%)',
            borderRadius: '14px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 8px 24px rgba(139, 92, 246, 0.35)',
            animation: 'float 6s ease-in-out infinite'
          }}>
            <GraduationCap size={26} color="white" strokeWidth={2.5} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '28px', fontWeight: '900', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '-1.5px' }}>AdmitGoal</span>
            <span style={{ fontSize: '10px', fontWeight: '800', backgroundColor: '#4f46e5', color: 'white', padding: '3px 8px', borderRadius: '6px', letterSpacing: '1px', lineHeight: '18px' }}>BETA</span>
          </div>
        </Link>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {['About', 'Contact'].map(item => (
            <Link key={item} href={`/${item.toLowerCase()}`} style={{ padding: '12px 24px', borderRadius: '14px', fontSize: '16px', fontWeight: '600', color: '#64748b', textDecoration: 'none', transition: 'all 0.3s ease' }}
              onMouseEnter={e => { e.target.style.background = '#f8fafc'; e.target.style.color = '#4f46e5' }}
              onMouseLeave={e => { e.target.style.background = 'transparent'; e.target.style.color = '#64748b' }}>
              {item}
            </Link>
          ))}
          
          {!loading && (
            <>
              {!user ? (
                <Link href="/signup" style={{ padding: '14px 32px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', borderRadius: '16px', fontSize: '16px', fontWeight: '700', textDecoration: 'none', boxShadow: '0 8px 24px rgba(139, 92, 246, 0.35)', transition: 'all 0.3s ease' }}
                  onMouseEnter={e => { e.target.style.transform = 'translateY(-3px)'; e.target.style.boxShadow = '0 12px 32px rgba(139, 92, 246, 0.5)' }}
                  onMouseLeave={e => { e.target.style.transform = 'translateY(0)'; e.target.style.boxShadow = '0 8px 24px rgba(139, 92, 246, 0.35)' }}>
                  Get Started →
                </Link>
              ) : (
                <div style={{ position: 'relative' }}>
                  <button
                    onClick={() => setShowProfileMenu(!showProfileMenu)}
                    style={{ padding: '14px 32px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', borderRadius: '16px', fontSize: '16px', fontWeight: '700', border: 'none', cursor: 'pointer', boxShadow: '0 8px 24px rgba(139, 92, 246, 0.35)', transition: 'all 0.3s ease', display: 'flex', alignItems: 'center', gap: '8px' }}
                    onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 12px 32px rgba(139, 92, 246, 0.5)' }}
                    onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(139, 92, 246, 0.35)' }}>
                    {user.user_metadata?.full_name || user.email?.split('@')[0] || 'Profile'} ▾
                  </button>

                  {showProfileMenu && (
                    <div style={{ position: 'absolute', right: 0, top: '60px', width: '220px', background: 'white', borderRadius: '16px', boxShadow: '0 12px 40px rgba(0,0,0,0.15)', border: '1px solid #f0f0f0', overflow: 'hidden', animation: 'fadeIn 0.2s ease' }}>
                      <Link href="/dashboard" style={{ display: 'block', padding: '14px 20px', color: '#0f172a', textDecoration: 'none', fontSize: '15px', fontWeight: '600', borderBottom: '1px solid #f8fafc', transition: 'all 0.2s' }}
                        onMouseEnter={e => { e.target.style.background = '#f8fafc'; e.target.style.color = '#4f46e5' }}
                        onMouseLeave={e => { e.target.style.background = 'transparent'; e.target.style.color = '#0f172a' }}>
                        Dashboard
                      </Link>
                      <Link href="/profile/edit" style={{ display: 'block', padding: '14px 20px', color: '#0f172a', textDecoration: 'none', fontSize: '15px', fontWeight: '600', borderBottom: '1px solid #f8fafc', transition: 'all 0.2s' }}
                        onMouseEnter={e => { e.target.style.background = '#f8fafc'; e.target.style.color = '#4f46e5' }}
                        onMouseLeave={e => { e.target.style.background = 'transparent'; e.target.style.color = '#0f172a' }}>
                        Edit Profile
                      </Link>
                      <Link href="/saved" style={{ display: 'block', padding: '14px 20px', color: '#0f172a', textDecoration: 'none', fontSize: '15px', fontWeight: '600', borderBottom: '1px solid #f8fafc', transition: 'all 0.2s' }}
                        onMouseEnter={e => { e.target.style.background = '#f8fafc'; e.target.style.color = '#4f46e5' }}
                        onMouseLeave={e => { e.target.style.background = 'transparent'; e.target.style.color = '#0f172a' }}>
                        Saved Scholarships
                      </Link>
                      <button onClick={handleLogout} style={{ display: 'block', width: '100%', textAlign: 'left', padding: '14px 20px', color: '#ef4444', background: 'transparent', border: 'none', fontSize: '15px', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s' }}
                        onMouseEnter={e => { e.target.style.background = '#fef2f2' }}
                        onMouseLeave={e => { e.target.style.background = 'transparent' }}>
                        Logout
                      </button>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </nav>

      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-5px); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}