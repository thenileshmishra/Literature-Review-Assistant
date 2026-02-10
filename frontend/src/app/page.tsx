'use client'

import { useEffect, useState } from 'react'
import { ConfigProvider, Layout, Alert, Button, Space, Typography, Spin, theme as antdTheme } from 'antd'
import { Header } from '@/components/layout/Header'
import { SearchForm } from '@/components/search/SearchForm'
import { MessageDisplay } from '@/components/chat/MessageDisplay'
import { PaperList } from '@/components/papers/PaperList'
import type { CreateReviewRequest } from '@/lib/types/api'
import { createReview } from '@/lib/api/reviews'
import { useReviewStream } from '@/lib/hooks/useReviewStream'

const { Content } = Layout
const { Text } = Typography
const { defaultAlgorithm, darkAlgorithm } = antdTheme
const THEME_KEY = 'app-theme'

export default function Home() {
  const [reviewId, setReviewId] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>('dark')
  const [themeInitialized, setThemeInitialized] = useState(false)
  const [model, setModel] = useState('gpt-4o-mini')

  const { messages, status, isStreaming, error: streamError, startStream } = useReviewStream(reviewId)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const saved = localStorage.getItem(THEME_KEY)
    if (saved === 'light' || saved === 'dark') {
      setThemeMode(saved)
      setThemeInitialized(true)
      return
    }

    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    setThemeMode(prefersDark ? 'dark' : 'light')
    setThemeInitialized(true)
  }, [])

  useEffect(() => {
    if (!themeInitialized) return
    const root = document.documentElement
    root.classList.toggle('dark', themeMode === 'dark')
    root.classList.toggle('light', themeMode === 'light')

    if (typeof window !== 'undefined') {
      localStorage.setItem(THEME_KEY, themeMode)
    }
  }, [themeMode, themeInitialized])

  const handleSubmit = async (request: CreateReviewRequest) => {
    try {
      setIsCreating(true)
      setError(null)

      // Create review
      const review = await createReview(request)
      setReviewId(review.id)

      // Start streaming
      setTimeout(() => {
        startStream()
      }, 500)

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create review')
      console.error('Error creating review:', err)
    } finally {
      setIsCreating(false)
    }
  }

  const handleNewSearch = () => {
    setReviewId(null)
    setError(null)
  }

  return (
    <ConfigProvider
      theme={{
        algorithm: themeMode === 'dark' ? darkAlgorithm : defaultAlgorithm,
        token: {
          borderRadius: 12,
          colorPrimary: '#1f6feb',
          fontFamily: 'inherit',
        },
      }}
    >
      <Layout className="app-shell">
        <Header
          model={model}
          onModelChange={setModel}
          themeMode={themeMode}
          onThemeChange={setThemeMode}
        />

        <Content className="app-content">
          <div className="content-wrap">
            {!reviewId ? (
              <SearchForm onSubmit={handleSubmit} isLoading={isCreating} model={model} />
            ) : (
              <div className="space-y-6">
                <Button type="link" onClick={handleNewSearch} className="px-0">
                  ← New search
                </Button>

                {isStreaming && (
                  <Space align="center">
                    <Spin size="small" />
                    <Text type="secondary">Processing review...</Text>
                  </Space>
                )}

                {messages.length > 0 && (
                  <MessageDisplay messages={messages} status={status} />
                )}

                {status === 'completed' && messages.length > 0 && (
                  <PaperList reviewId={reviewId} />
                )}
              </div>
            )}

            {(error || streamError) && (
              <Alert
                type="error"
                message={error || streamError}
                showIcon
                className="mt-6"
              />
            )}
          </div>
        </Content>
      </Layout>
    </ConfigProvider>
  )
}
