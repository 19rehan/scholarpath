'use client';
import { useState } from 'react';
import { supabase } from '@/lib/supabase';
import { useRouter } from 'next/navigation';

export default function CreateProfile() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [countrySearch, setCountrySearch] = useState('');
  const [fieldSearch, setFieldSearch] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    gender: '',
    current_country: '',
    current_education_level: '',
    target_degree: '',
    field_of_study: '',
    specific_major: '',
    gpa: '',
    gpa_scale: '4.0',
    has_ielts: false,
    ielts_overall: '',
    has_toefl: false,
    toefl_score: '',
    has_pte: false,
    pte_score: '',
    preferred_countries: [],
    funding_preference: 'Fully Funded',
    budget_per_year: ''
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCountryToggle = (country) => {
    setFormData(prev => ({
      ...prev,
      preferred_countries: prev.preferred_countries.includes(country)
        ? prev.preferred_countries.filter(c => c !== country)
        : [...prev.preferred_countries, country]
    }));
  };

  const validateStep = () => {
    if (step === 1) {
      if (!formData.name || !formData.email || !formData.current_country) {
        setError('Please fill all required fields');
        return false;
      }
    }
    if (step === 2) {
      if (!formData.target_degree || !formData.field_of_study) {
        setError('Please fill all required fields');
        return false;
      }
    }
    setError('');
    return true;
  };

  const handleNext = () => {
    if (validateStep()) {
      setStep(step + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleBack = () => {
    setStep(step - 1);
    setError('');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSocialLogin = async (provider) => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: provider,
        options: {
          redirectTo: window.location.origin + '/profile/create?step=2'
        }
      });
      if (error) throw error;
    } catch (err) {
      setError('Social login failed. Please try again.');
    }
  };

  const handleSubmit = async () => {
    if (!validateStep()) return;
    setLoading(true);
    setError('');

    try {
      const { data, error: dbError } = await supabase
        .from('user_profiles')
        .insert([{ ...formData, profile_completed: true }])
        .select();

      if (dbError) throw dbError;

      localStorage.setItem('admitgoal_profile_id', data[0].id);
      localStorage.setItem('admitgoal_profile_created', 'true');
      localStorage.setItem('admitgoal_user_email', formData.email);

      router.push('/profile/matches');
    } catch (err) {
      setError(err.message || 'Failed to create profile');
      setLoading(false);
    }
  };

  const countries = [
    'Pakistan', 'India', 'Bangladesh', 'Nigeria', 'Kenya', 'Ghana', 
    'Ethiopia', 'South Africa', 'Nepal', 'Sri Lanka', 'Afghanistan',
    'Egypt', 'Tanzania', 'Uganda', 'Zimbabwe', 'Morocco', 'Algeria'
  ];

  const fields = [
    'Engineering', 'Computer Science', 'Business', 'Medical', 
    'Natural Sciences', 'Social Sciences', 'Arts & Humanities',
    'Education', 'Law', 'Agriculture', 'Architecture', 'Pharmacy'
  ];

  const filteredCountries = countries.filter(c => 
    c.toLowerCase().includes(countrySearch.toLowerCase())
  );

  const filteredFields = fields.filter(f => 
    f.toLowerCase().includes(fieldSearch.toLowerCase())
  );

  const dreamCountries = [
    'USA', 'UK', 'Canada', 'Germany', 'Australia', 'Netherlands', 
    'Sweden', 'Norway', 'France', 'Italy', 'Spain', 'China', 
    'Japan', 'South Korea', 'Singapore', 'Switzerland', 'Denmark'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-8 px-4">
      <div className="max-w-5xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-4">
          {[1, 2, 3, 4].map(s => (
            <div key={s} className="flex items-center flex-1">
              <div 
                className="w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all"
                style={{
                  background: step >= s ? 'linear-gradient(135deg, #6366f1, #a855f7)' : '#374151',
                  color: 'white',
                  boxShadow: step >= s ? '0 10px 25px rgba(99, 102, 241, 0.5)' : 'none'
                }}
              >
                {step > s ? '✓' : s}
              </div>
              {s < 4 && (
                <div 
                  className="flex-1 h-2 mx-3 rounded-full transition-all duration-500"
                  style={{ background: step > s ? 'linear-gradient(90deg, #6366f1, #a855f7)' : '#374151' }}
                />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between text-white text-sm font-semibold">
          <span style={{ opacity: step === 1 ? 1 : 0.6 }}>Personal</span>
          <span style={{ opacity: step === 2 ? 1 : 0.6 }}>Academic</span>
          <span style={{ opacity: step === 3 ? 1 : 0.6 }}>Tests</span>
          <span style={{ opacity: step === 4 ? 1 : 0.6 }}>Preferences</span>
        </div>
      </div>

      <div className="max-w-5xl mx-auto bg-white rounded-3xl shadow-2xl p-8 md:p-12">
        <div className="mb-8">
          <h1 
            className="text-5xl font-black mb-3"
            style={{
              background: 'linear-gradient(135deg, #6366f1, #a855f7, #ec4899)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            Create Your Profile
          </h1>
          <p className="text-gray-600 text-lg">
            Get personalized scholarship matches in just 2 minutes
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border-2 border-red-200 rounded-xl text-red-600 font-semibold">
            {error}
          </div>
        )}

        <div style={{ minHeight: '500px' }}>
          {step === 1 && (
            <div className="space-y-6">
              <div className="mb-8 pb-8 border-b-2 border-gray-200">
                <p className="text-sm font-semibold text-gray-600 mb-4">Quick Sign In</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <button
                    onClick={() => handleSocialLogin('google')}
                    className="flex items-center justify-center gap-3 px-6 py-3 bg-white border-2 border-gray-200 rounded-xl font-semibold hover:border-gray-300 transition"
                  >
                    <svg className="w-5 h-5" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    Google
                  </button>

                  <button
                    onClick={() => handleSocialLogin('facebook')}
                    className="flex items-center justify-center gap-3 px-6 py-3 bg-white border-2 border-gray-200 rounded-xl font-semibold hover:border-gray-300 transition"
                  >
                    <svg className="w-5 h-5" fill="#1877F2" viewBox="0 0 24 24">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                    Facebook
                  </button>

                  <button
                    onClick={() => handleSocialLogin('apple')}
                    className="flex items-center justify-center gap-3 px-6 py-3 bg-black text-white border-2 border-black rounded-xl font-semibold hover:bg-gray-900 transition"
                  >
                    <svg className="w-5 h-5" fill="white" viewBox="0 0 24 24">
                      <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                    </svg>
                    Apple
                  </button>
                </div>
                <p className="text-center text-sm text-gray-500 mt-4">Or fill the form below</p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Full Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                  placeholder="Enter your full name"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Email Address *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                  placeholder="your.email@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Gender</label>
                <select
                  value={formData.gender}
                  onChange={(e) => handleChange('gender', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                >
                  <option value="">Select gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                  <option value="Prefer not to say">Prefer not to say</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Current Country *</label>
                <input
                  type="text"
                  value={countrySearch}
                  onChange={(e) => setCountrySearch(e.target.value)}
                  onFocus={(e) => e.target.value = ''}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition mb-2"
                  placeholder="Search country (e.g., PK, Pakistan)..."
                />
                <select
                  value={formData.current_country}
                  onChange={(e) => handleChange('current_country', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                  size="5"
                >
                  <option value="">Select your country</option>
                  {filteredCountries.map(country => (
                    <option key={country} value={country}>{country}</option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Current Education Level</label>
                <select
                  value={formData.current_education_level}
                  onChange={(e) => handleChange('current_education_level', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                >
                  <option value="">Select level</option>
                  <option value="High School">High School</option>
                  <option value="Bachelor">Bachelor Degree</option>
                  <option value="Master">Master Degree</option>
                  <option value="PhD">PhD</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Target Degree *</label>
                <select
                  value={formData.target_degree}
                  onChange={(e) => handleChange('target_degree', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                >
                  <option value="">What degree do you want?</option>
                  <option value="Bachelor">Bachelor Degree</option>
                  <option value="Master">Master Degree</option>
                  <option value="PhD">PhD</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Field of Study *</label>
                <input
                  type="text"
                  value={fieldSearch}
                  onChange={(e) => setFieldSearch(e.target.value)}
                  onFocus={(e) => e.target.value = ''}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition mb-2"
                  placeholder="Search field..."
                />
                <select
                  value={formData.field_of_study}
                  onChange={(e) => handleChange('field_of_study', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                  size="5"
                >
                  <option value="">Select field</option>
                  {filteredFields.map(field => (
                    <option key={field} value={field}>{field}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Specific Major</label>
                <input
                  type="text"
                  value={formData.specific_major}
                  onChange={(e) => handleChange('specific_major', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                  placeholder="e.g., Computer Science, Mechanical Engineering"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">GPA/Percentage</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.gpa}
                    onChange={(e) => handleChange('gpa', e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                    placeholder="3.5"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">GPA Scale</label>
                  <select
                    value={formData.gpa_scale}
                    onChange={(e) => handleChange('gpa_scale', e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                  >
                    <option value="4.0">4.0</option>
                    <option value="5.0">5.0</option>
                    <option value="10.0">10.0</option>
                    <option value="100">100 (Percentage)</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <p className="text-gray-600 mb-4">Add your test scores if you have them (optional)</p>

              <div className="border-2 border-gray-200 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <label className="text-lg font-semibold text-gray-800">IELTS</label>
                  <button
                    type="button"
                    onClick={() => handleChange('has_ielts', !formData.has_ielts)}
                    className="relative w-14 h-8 rounded-full transition"
                    style={{ background: formData.has_ielts ? 'linear-gradient(135deg, #6366f1, #a855f7)' : '#d1d5db' }}
                  >
                    <div 
                      className="absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform"
                      style={{ transform: formData.has_ielts ? 'translateX(24px)' : 'translateX(0)' }}
                    />
                  </button>
                </div>
                {formData.has_ielts && (
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    max="9"
                    value={formData.ielts_overall}
                    onChange={(e) => handleChange('ielts_overall', e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                    placeholder="Overall Band Score (e.g., 7.5)"
                  />
                )}
              </div>

              <div className="border-2 border-gray-200 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <label className="text-lg font-semibold text-gray-800">TOEFL</label>
                  <button
                    type="button"
                    onClick={() => handleChange('has_toefl', !formData.has_toefl)}
                    className="relative w-14 h-8 rounded-full transition"
                    style={{ background: formData.has_toefl ? 'linear-gradient(135deg, #6366f1, #a855f7)' : '#d1d5db' }}
                  >
                    <div 
                      className="absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform"
                      style={{ transform: formData.has_toefl ? 'translateX(24px)' : 'translateX(0)' }}
                    />
                  </button>
                </div>
                {formData.has_toefl && (
                  <input
                    type="number"
                    min="0"
                    max="120"
                    value={formData.toefl_score}
                    onChange={(e) => handleChange('toefl_score', e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                    placeholder="Total Score (e.g., 100)"
                  />
                )}
              </div>

              <div className="border-2 border-gray-200 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <label className="text-lg font-semibold text-gray-800">PTE Academic</label>
                  <button
                    type="button"
                    onClick={() => handleChange('has_pte', !formData.has_pte)}
                    className="relative w-14 h-8 rounded-full transition"
                    style={{ background: formData.has_pte ? 'linear-gradient(135deg, #6366f1, #a855f7)' : '#d1d5db' }}
                  >
                    <div 
                      className="absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform"
                      style={{ transform: formData.has_pte ? 'translateX(24px)' : 'translateX(0)' }}
                    />
                  </button>
                </div>
                {formData.has_pte && (
                  <input
                    type="number"
                    min="10"
                    max="90"
                    value={formData.pte_score}
                    onChange={(e) => handleChange('pte_score', e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                    placeholder="Overall Score (e.g., 65)"
                  />
                )}
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">Dream Countries (Select multiple)</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {dreamCountries.map(country => (
                    <button
                      key={country}
                      type="button"
                      onClick={() => handleCountryToggle(country)}
                      className="px-4 py-3 rounded-xl font-semibold transition"
                      style={{
                        background: formData.preferred_countries.includes(country) 
                          ? 'linear-gradient(135deg, #6366f1, #a855f7)' 
                          : '#f3f4f6',
                        color: formData.preferred_countries.includes(country) ? 'white' : '#374151'
                      }}
                    >
                      {country}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Funding Preference</label>
                <select
                  value={formData.funding_preference}
                  onChange={(e) => handleChange('funding_preference', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                >
                  <option value="Fully Funded">Only Fully Funded</option>
                  <option value="Partial">Partial Funding OK</option>
                  <option value="Any">Any Funding Type</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Budget per Year (USD) - Optional</label>
                <input
                  type="number"
                  value={formData.budget_per_year}
                  onChange={(e) => handleChange('budget_per_year', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none transition"
                  placeholder="10000"
                />
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-between items-center mt-8 pt-6 border-t-2 border-gray-200">
          {step > 1 ? (
            <button
              onClick={handleBack}
              disabled={loading}
              className="px-8 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition disabled:opacity-50"
            >
              Back
            </button>
          ) : <div></div>}
          
          {step < 4 ? (
            <button
              onClick={handleNext}
              className="px-8 py-3 text-white rounded-xl font-semibold transition"
              style={{ 
                background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                marginLeft: step === 1 ? 'auto' : '0'
              }}
            >
              Next Step
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-8 py-3 text-white rounded-xl font-semibold transition disabled:opacity-50"
              style={{ 
                background: loading ? '#9ca3af' : 'linear-gradient(135deg, #10b981, #059669)',
                marginLeft: 'auto'
              }}
            >
              {loading ? 'Creating Profile...' : 'Find My Matches'}
            </button>
          )}
        </div>
      </div>

      <div className="max-w-5xl mx-auto mt-6 text-center text-white text-sm opacity-80">
        <p>Your data is secure and never shared with third parties</p>
      </div>
    </div>
  );
}