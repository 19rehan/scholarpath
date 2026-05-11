import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'AdmitGoal – Free AI Scholarship Finder | Pakistan India Bangladesh Africa',
  description: 'Find fresh scholarships from universities worldwide. Free AI guidance on eligibility, IELTS, SOP writing. No agent needed. Updated daily.',
  keywords: 'scholarships, study abroad, Pakistan scholarships, fully funded scholarships, no IELTS scholarships',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta name="google-site-verification" content="zKOcXjMcvxwhAnjJdQBtkxSOiyBWSJ2sU8fRXl7ZFUI" />
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-ZSKBYXZS8J"></script>
        <script dangerouslySetInnerHTML={{
          __html: `window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-ZSKBYXZS8J');`
        }} />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}