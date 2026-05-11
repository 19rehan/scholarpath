import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

export default async function sitemap() {
  const base = 'https://admitgoal.com'

  // Static pages
  const staticPages = [
    { url: base, lastModified: new Date(), changeFrequency: 'daily', priority: 1.0 },
    { url: `${base}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${base}/contact`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.7 },
    { url: `${base}/privacy`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.5 },
    { url: `${base}/search?q=fully+funded`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/search?q=no+ielts`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/search?q=phd`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/search?q=germany`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/search?q=china`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/search?q=turkey`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/search?q=korea`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/search?q=australia`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/search?q=canada`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/search?q=uk`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/search?q=saudi+arabia`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/search?q=masters`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
  ]

  // Dynamic scholarship pages
  const { data } = await supabase
    .from('scholarship_details')
    .select('id, last_updated')
    .order('id', { ascending: false })

  const scholarshipPages = (data || []).map(s => ({
    url: `${base}/scholarship/${s.id}`,
    lastModified: s.last_updated ? new Date(s.last_updated) : new Date(),
    changeFrequency: 'weekly',
    priority: 0.9,
  }))

  return [...staticPages, ...scholarshipPages]
}