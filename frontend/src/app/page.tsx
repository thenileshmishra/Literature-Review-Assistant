'use client'

import { useEffect, useMemo, useState, useCallback } from 'react'
import dynamic from 'next/dynamic'
import { Card, ConfigProvider, Layout, Alert, Button, Skeleton, Space, theme as antdTheme } from 'antd'
import { MessageSquarePlus, Moon, Sun } from 'lucide-react'
import { SearchForm } from '@/components/search/SearchForm'
import type { ChatHistoryItem, ChatSession, CreateReviewRequest, ReviewResponse } from '@/lib/types/api'
import { createReview, listReviews, deleteReview } from '@/lib/api/reviews'
import { useReviewStream } from '@/lib/hooks/useReviewStream'
import { HistorySidebar } from '@/components/chat/HistorySidebar'

const { Content, Sider } = Layout
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

/** Convert a backend ReviewResponse into the shape our components expect. */
function reviewToChat(r: ReviewResponse): ChatSession {
  return {
    id: r.id,
    title: r.request?.topic?.slice(0, 50) || 'Untitled',
    createdAt: r.created_at,
    updatedAt: r.completed_at || r.created_at,
    status: r.status,
    messageCount: r.messages.length,
    messages: r.messages,
    reviewId: r.id,
  }
}

export default function Home() {
  const [chats, setChats] = useState<ChatSession[]>([])
  const [activeChatId, setActiveChatId] = useState<string | null>(null)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [streamReviewId, setStreamReviewId] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [, setIsLoadingChats] = useState(true)
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>(() => {
    if (typeof document === 'undefined') return 'dark'
    return document.documentElement.classList.contains('light') ? 'light' : 'dark'
  })

  // ── Stream hook: update the active chat in-place as SSE events arrive ──
  const { status: streamStatus, isStreaming, error: streamError, startStream } = useReviewStream(streamReviewId, {
    onUpdate: ({ messages, status }) => {
      if (!streamReviewId) return
      setChats((prev) =>
        prev.map((c) =>
          c.id === streamReviewId ? { ...c, messages, status, messageCount: messages.length } : c
        )
      )
    },
  })

  const activeChat = useMemo(
    () => (activeChatId ? chats.find((c) => c.id === activeChatId) ?? null : null),
    [activeChatId, chats]
  )

  const sidebarItems: ChatHistoryItem[] = useMemo(
    () => chats.map(({ id, title, createdAt, updatedAt, status, messageCount }) => ({
      id, title, createdAt, updatedAt, status, messageCount,
    })),
    [chats]
  )

  const displayMessages = activeChat?.messages ?? []
  const displayStatus = activeChat?.status ?? 'pending'
  const displayReviewId = activeChat?.reviewId ?? null
  const isActiveStreaming = isStreaming && streamReviewId === activeChatId

  // ── Load reviews from backend on mount ──
  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const reviews = await listReviews(50)
        if (cancelled) return
        const mapped = reviews.map(reviewToChat)
        setChats(mapped)
        if (mapped.length > 0) {
          setActiveChatId(mapped[0].id)
        }
      } catch (err) {
        console.error('Failed to load reviews from backend:', err)
        // Not fatal — user can still create new reviews
      } finally {
        if (!cancelled) setIsLoadingChats(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  // ── Theme persistence ──
  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('dark', themeMode === 'dark')
    root.classList.toggle('light', themeMode === 'light')
    localStorage.setItem(THEME_KEY, themeMode)
  }, [themeMode])

  // ── Submit a new review ──
  const handleSubmit = async (request: CreateReviewRequest) => {
    try {
      setIsCreating(true)
      setError(null)

      const review = await createReview(request)
      const newChat = reviewToChat(review)
      setChats((prev) => [newChat, ...prev])
      setActiveChatId(newChat.id)
      setStreamReviewId(review.id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create review')
      console.error('Error creating review:', err)
    } finally {
      setIsCreating(false)
    }
  }

  // ── Start stream when reviewId changes ──
  useEffect(() => {
    if (!streamReviewId) return
    startStream()
  }, [streamReviewId, startStream])

  // ── Clear stream state on completion ──
  useEffect(() => {
    if (!streamReviewId) return
    if (streamStatus !== 'completed' && streamStatus !== 'failed') return
    setStreamReviewId(null)
  }, [streamReviewId, streamStatus])

  // ── New chat = just show composer ──
  const handleNewChat = useCallback(() => {
    setActiveChatId(null)
    setError(null)
  }, [])

  const handleSelectChat = useCallback((chatId: string) => {
    setActiveChatId(chatId)
    setError(null)
  }, [])

  // ── Delete a review (backend + local state) ──
  const handleDeleteChat = useCallback(async (chatId: string) => {
    try {
      await deleteReview(chatId)
    } catch {
      // Session might already be expired on backend, still remove locally
    }
    setChats((prev) => prev.filter((c) => c.id !== chatId))
    if (activeChatId === chatId) {
      setActiveChatId(null)
    }
  }, [activeChatId])

  // ── Rename (local only — backend has no rename endpoint) ──
  const handleRenameChat = useCallback((chatId: string, newTitle: string) => {
    const trimmed = newTitle.trim()
    if (!trimmed) return
    setChats((prev) => prev.map((c) => c.id === chatId ? { ...c, title: trimmed } : c))
  }, [])

  const shouldShowSearchForm =
    !activeChat || (displayMessages.length === 0 && displayStatus === 'pending' && !isActiveStreaming)

  return (
    <ConfigProvider
      theme={{
        algorithm: themeMode === 'dark' ? darkAlgorithm : defaultAlgorithm,
        token: {
          borderRadius: 12,
          fontFamily: 'inherit',
          colorText: themeMode === 'dark' ? 'rgba(255,255,255,0.88)' : 'rgba(15,23,42,0.88)',
          colorTextSecondary: themeMode === 'dark' ? 'rgba(226,232,240,0.72)' : 'rgba(15,23,42,0.62)',
          colorBgBase: themeMode === 'dark' ? '#1e1e24' : '#ffffff',
          colorBgContainer: themeMode === 'dark' ? '#26262e' : '#ffffff',
        },
      }}
    >
      <Layout className="app-shell">
        <Sider
          width={260}
          collapsed={isSidebarCollapsed}
          collapsible
          trigger={null}
          collapsedWidth={60}
          className="history-sider"
        >
          <div className="history-sider-inner">
            <HistorySidebar
              chats={sidebarItems}
              activeChatId={activeChatId}
              onNewChat={handleNewChat}
              onSelectChat={handleSelectChat}
              onRenameChat={handleRenameChat}
              onDeleteChat={handleDeleteChat}
              collapsed={isSidebarCollapsed}
              onToggleCollapse={() => setIsSidebarCollapsed((v) => !v)}
            />
          </div>
        </Sider>

        <Layout>
          <div className="top-bar">
            <div className="text-lg font-semibold text-foreground">
              Literature Review
            </div>
            <button
              type="button"
              onClick={() => setThemeMode(themeMode === 'dark' ? 'light' : 'dark')}
              className="sidebar-new-chat-btn"
              aria-label="Toggle theme"
              title={themeMode === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {themeMode === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
          </div>

          <Content className="app-content">
            <div className="content-wrap">
              {shouldShowSearchForm ? (
                <SearchForm onSubmit={handleSubmit} isLoading={isCreating} />
              ) : (
                <div className="space-y-6 px-4 pt-8 pb-16">
                  <Button
                    type="text"
                    icon={<MessageSquarePlus className="h-4 w-4" />}
                    onClick={handleNewChat}
                    className="new-search-action"
                  >
                    New chat
                  </Button>

                  {isActiveStreaming && displayMessages.length === 0 && (
                    <Card className="chat-card">
                      <Space direction="vertical" size="middle" className="w-full">
                        <Skeleton.Input active size="small" className="w-52" />
                        <Skeleton active paragraph={{ rows: 3 }} />
                      </Space>
                    </Card>
                  )}

                  {displayMessages.length > 0 && (
                    <MessageDisplay messages={displayMessages} status={displayStatus} />
                  )}

                  {displayStatus === 'completed' && displayMessages.length > 0 && displayReviewId && (
                    <PaperList reviewId={displayReviewId} />
                  )}
                </div>
              )}

              {(error || streamError) && (
                <Alert
                  type="error"
                  message={error || streamError}
                  showIcon
                  className="mt-6 mx-4"
                />
              )}
            </div>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  )
}
