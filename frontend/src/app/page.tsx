'use client'

import { useEffect, useMemo, useState } from 'react'
import dynamic from 'next/dynamic'
import { Card, ConfigProvider, Layout, Alert, Button, Skeleton, Space, theme as antdTheme } from 'antd'
import { MessageSquarePlus } from 'lucide-react'
import { Header } from '@/components/layout/Header'
import { SearchForm } from '@/components/search/SearchForm'
import type { ChatHistoryItem, ChatSession, CreateReviewRequest } from '@/lib/types/api'
import { createReview } from '@/lib/api/reviews'
import { useReviewStream } from '@/lib/hooks/useReviewStream'
import { HistorySidebar } from '@/components/chat/HistorySidebar'
import {
  createChat,
  getActiveChatId,
  getAllChats,
  getChat,
  setActiveChatId,
  updateChat,
} from '@/lib/storage/chatHistory'

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

export default function Home() {
  const [chats, setChats] = useState<ChatSession[]>([])
  const [activeChatId, setActiveChatIdState] = useState<string | null>(null)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [streamReviewId, setStreamReviewId] = useState<string | null>(null)
  const [streamChatId, setStreamChatId] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>(() => {
    if (typeof document === 'undefined') {
      return 'dark'
    }

    return document.documentElement.classList.contains('light') ? 'light' : 'dark'
  })

  const { status: streamStatus, isStreaming, error: streamError, startStream } = useReviewStream(streamReviewId, {
    onUpdate: ({ messages, status }) => {
      if (!streamChatId) return
      const updated = updateChat(streamChatId, { messages, status })
      if (!updated) return
      setChats(getAllChats())
    },
  })

  const activeChat = useMemo(
    () => (activeChatId ? chats.find((chat) => chat.id === activeChatId) ?? null : null),
    [activeChatId, chats]
  )

  const sidebarItems: ChatHistoryItem[] = useMemo(
    () => chats.map(({ id, title, createdAt, updatedAt, status, messageCount }) => ({
      id,
      title,
      createdAt,
      updatedAt,
      status,
      messageCount,
    })),
    [chats]
  )

  const displayMessages = activeChat?.messages ?? []
  const displayStatus = activeChat?.status ?? 'pending'
  const displayReviewId = activeChat?.reviewId ?? null
  const isActiveStreaming = isStreaming && streamChatId === activeChatId

  useEffect(() => {
    const allChats = getAllChats()
    if (allChats.length === 0) {
      setChats([])
      setActiveChatIdState(null)
      setActiveChatId(null)
      return
    }

    setChats(allChats)

    const storedActive = getActiveChatId()
    const resolvedActive =
      (storedActive && allChats.some((chat) => chat.id === storedActive) ? storedActive : allChats[0].id)

    setActiveChatIdState(resolvedActive)
    setActiveChatId(resolvedActive)
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

      let targetChatId = activeChatId
      if (!targetChatId) {
        const nextChat = createChat({ title: request.topic })
        targetChatId = nextChat.id
        setActiveChatIdState(nextChat.id)
        setActiveChatId(nextChat.id)
      }

      const trimmedTitle = request.topic.trim().slice(0, 50)
      updateChat(targetChatId, {
        title: trimmedTitle || 'New chat',
        messages: [],
        status: 'pending',
        reviewId: undefined,
      })
      setChats(getAllChats())

      const review = await createReview(request)
      setStreamReviewId(review.id)
      setStreamChatId(targetChatId)

      updateChat(targetChatId, {
        reviewId: review.id,
        status: 'in_progress',
      })
      setChats(getAllChats())

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create review')
      console.error('Error creating review:', err)
    } finally {
      setIsCreating(false)
    }
  }

  useEffect(() => {
    if (!streamReviewId) return
    startStream()
  }, [streamReviewId, startStream])

  useEffect(() => {
    if (!streamChatId) return
    if (streamStatus !== 'completed' && streamStatus !== 'failed') return

    setStreamReviewId(null)
    setStreamChatId(null)
  }, [streamChatId, streamStatus])

  const handleNewChat = () => {
    if (activeChat && activeChat.messages.length === 0 && activeChat.status === 'pending' && !activeChat.reviewId) {
      setError(null)
      return
    }

    const existingDraft = chats.find(
      (chat) => chat.messages.length === 0 && chat.status === 'pending' && !chat.reviewId
    )

    if (existingDraft) {
      setActiveChatIdState(existingDraft.id)
      setActiveChatId(existingDraft.id)
      setError(null)
      return
    }

    const nextChat = createChat()
    setChats(getAllChats())
    setActiveChatIdState(nextChat.id)
    setActiveChatId(nextChat.id)
    setError(null)
  }

  const handleSelectChat = (chatId: string) => {
    const chat = getChat(chatId)
    if (!chat) return

    setActiveChatIdState(chat.id)
    setActiveChatId(chat.id)
    setError(null)
  }

  const shouldShowSearchForm =
    !activeChat || (displayMessages.length === 0 && displayStatus === 'pending' && !isActiveStreaming)

  return (
    <ConfigProvider
      theme={{
        algorithm: themeMode === 'dark' ? darkAlgorithm : defaultAlgorithm,
        token: {
          borderRadius: 12,
          colorPrimary: '#1f6feb',
          fontFamily: 'inherit',
          colorText: themeMode === 'dark' ? 'rgba(255, 255, 255, 0.88)' : 'rgba(15, 23, 42, 0.88)',
          colorTextSecondary: themeMode === 'dark' ? 'rgba(226, 232, 240, 0.72)' : 'rgba(15, 23, 42, 0.62)',
          colorBgBase: themeMode === 'dark' ? '#0f172a' : '#ffffff',
          colorBgContainer: themeMode === 'dark' ? '#111827' : '#ffffff',
        },
      }}
    >
      <Layout className="app-shell">
        <Header
          themeMode={themeMode}
          onThemeChange={setThemeMode}
        />

        <Layout className="app-main-layout">
          <Sider
            width={300}
            collapsed={isSidebarCollapsed}
            collapsible
            trigger={null}
            collapsedWidth={84}
            className="history-sider"
          >
            <div className="history-sider-inner">
              <HistorySidebar
                chats={sidebarItems}
                activeChatId={activeChatId}
                onNewChat={handleNewChat}
                onSelectChat={handleSelectChat}
                collapsed={isSidebarCollapsed}
                onToggleCollapse={() => setIsSidebarCollapsed((value) => !value)}
              />
            </div>
          </Sider>

          <Content className="app-content">
            <div className="content-wrap">
              {shouldShowSearchForm ? (
                <SearchForm onSubmit={handleSubmit} isLoading={isCreating} />
              ) : (
                <div className="space-y-6">
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
                  className="mt-6"
                />
              )}
            </div>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  )
}
