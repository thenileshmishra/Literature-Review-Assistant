import type { Metadata } from "next"
import Script from "next/script"
import { Space_Grotesk } from "next/font/google"
import "antd/dist/reset.css"
import "./globals.css"
import { QueryProvider } from "@/providers/QueryProvider"

const spaceGrotesk = Space_Grotesk({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Literature Review Assistant",
  description: "AI-powered multi-agent literature review system",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <Script id="theme-init" strategy="beforeInteractive">{`
          (function () {
            try {
              var saved = localStorage.getItem('app-theme');
              var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
              var mode = (saved === 'light' || saved === 'dark') ? saved : (prefersDark ? 'dark' : 'light');
              var root = document.documentElement;
              root.classList.remove('light', 'dark');
              root.classList.add(mode);
            } catch (e) {}
          })();
        `}</Script>
      </head>
      <body className={spaceGrotesk.className}>
        <QueryProvider>
          <main className="min-h-screen">
            {children}
          </main>
        </QueryProvider>
      </body>
    </html>
  )
}
