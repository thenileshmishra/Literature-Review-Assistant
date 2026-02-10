import type { Metadata } from "next"
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
    <html lang="en" className="dark" suppressHydrationWarning>
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
