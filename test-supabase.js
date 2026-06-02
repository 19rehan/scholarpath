const { createClient } = require('@supabase/supabase-js')

const supabase = createClient(
  'https://deqyxksflvlxjelppgxz.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRlcXl4a3NmbHZseGplbHBwZ3h6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzczMzYyNjEsImV4cCI6MjA1MjkxMjI2MX0.kLHyx8qMmVHYZqr1H0u7hpPw4mYCJSxXgQKIiFw6uOw'
)

async function test() {
  const { data, error, count } = await supabase
    .from('scholarship_details')
    .select('*', { count: 'exact' })
    .limit(5)
  
  console.log('Count:', count)
  console.log('Error:', error)
  console.log('Data:', data?.length, 'scholarships')
}

test()