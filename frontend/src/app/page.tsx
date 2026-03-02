'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import { Card, ConfigProvider, Layout, Alert, Button, Skeleton, Space, theme as antdTheme } from 'antd'
import { Header } from '@/components/layout/Header'
import { SearchForm } from '@/components/search/SearchForm'
import type { CreateReviewRequest } from '@/lib/types/api'
import { createReview } from '@/lib/api/reviews'
import { useReviewStream, clearSession, getStoredReviewId } from '@/lib/hooks/useReviewStream'

const { Content } = Layout
const { defaultAlgorithm, darkAlgorithm } = antdTheme
const THEME_KEY = 'app-theme'

const MessageDisplay = dynamic(
  () => import('@/components/chat/MessageDisplay').then((module) => module.MessageDisplay),
  { loading: () => <Skeleton active paragraph={{ rows: 3 }} /> }
)

const PaperList = dynamic(
  () => import('@/components/papers/PaperList').then((module) => module.PaperList),
  { loading: () => <Skeleton active paragraph={{ rows: 4 }} /> }
)

export default function Home() {
  const [reviewId, setReviewId] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>(() => {
    if (typeof document === 'undefined') {
      return 'dark'
    }

    return document.documentElement.classList.contains('light') ? 'light' : 'dark'
  })

  const { messages, status, isStreaming, error: streamError, startStream } = useReviewStream(reviewId)

  // Restore previous session on mount
  useEffect(() => {
    const storedId = getStoredReviewId()
    if (storedId) setReviewId(storedId)
  }, [])

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('dark', themeMode === 'dark')
    root.classList.toggle('light', themeMode === 'light')

    localStorage.setItem(THEME_KEY, themeMode)
  }, [themeMode])

  const handleSubmit = async (request: CreateReviewRequest) => {
    try {
      setIsCreating(true)
      setError(null)
      clearSession()

      const review = await createReview(request)
      setReviewId(review.id)

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create review')
      console.error('Error creating review:', err)
    } finally {
      setIsCreating(false)
    }
  }

  useEffect(() => {
    if (!reviewId) return
    startStream()
  }, [reviewId, startStream])

  const handleNewSearch = () => {
    clearSession()
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
          themeMode={themeMode}
          onThemeChange={setThemeMode}
        />

        <Content className="app-content">
          <div className="content-wrap">
            {!reviewId ? (
              <SearchForm onSubmit={handleSubmit} isLoading={isCreating} />
            ) : (
              <div className="space-y-6">
                <Button type="link" onClick={handleNewSearch} className="px-0">
                  ← New search
                </Button>

                {isStreaming && messages.length === 0 && (
                  <Card className="chat-card">
                    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                      <Skeleton.Input active size="small" style={{ width: 200 }} />
                      <Skeleton active paragraph={{ rows: 3 }} />
                    </Space>
                  </Card>
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
