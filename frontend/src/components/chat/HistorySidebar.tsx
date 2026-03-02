'use client'

import { useMemo } from 'react'
import { Button, List, Space, Typography, Tooltip } from 'antd'
import { MessageSquarePlus, MoreHorizontal, PanelLeft, PanelRight } from 'lucide-react'
import type { ChatHistoryItem } from '@/lib/types/api'

const { Text } = Typography

interface HistorySidebarProps {
  chats: ChatHistoryItem[]
  activeChatId: string | null
  onNewChat: () => void
  onSelectChat: (chatId: string) => void
  collapsed?: boolean
  onToggleCollapse: () => void
}

function formatRelativeTime(isoDate: string) {
  const now = Date.now()
  const target = new Date(isoDate).getTime()
  const diffMs = target - now

  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour

  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })

  if (Math.abs(diffMs) < hour) {
    return rtf.format(Math.round(diffMs / minute), 'minute')
  }

  if (Math.abs(diffMs) < day) {
    return rtf.format(Math.round(diffMs / hour), 'hour')
  }

  return rtf.format(Math.round(diffMs / day), 'day')
}

export function HistorySidebar({
  chats,
  activeChatId,
  onNewChat,
  onSelectChat,
  collapsed = false,
  onToggleCollapse,
}: HistorySidebarProps) {
  const sortedChats = useMemo(
    () => chats.slice().sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()),
    [chats]
  )

  return (
    <div className="h-full flex flex-col gap-3">
      <div className="flex items-center justify-end">
        <Tooltip title={collapsed ? 'Expand sidebar' : 'Shrink sidebar'} placement="right">
          <Button
            type="text"
            icon={collapsed ? <PanelRight className="h-4 w-4" /> : <PanelLeft className="h-4 w-4" />}
            onClick={onToggleCollapse}
            aria-label={collapsed ? 'Expand sidebar' : 'Shrink sidebar'}
          />
        </Tooltip>
      </div>

      {collapsed && (
        <Tooltip title="New chat" placement="right">
          <Button type="primary" icon={<MessageSquarePlus className="h-4 w-4" />} onClick={onNewChat} block />
        </Tooltip>
      )}

      {!collapsed && sortedChats.length > 0 && (
        <List
          header={
            <button
              type="button"
              onClick={onNewChat}
              className="history-chat-item"
            >
              <Space align="center" size="small">
                <MessageSquarePlus className="h-4 w-4" />
                <Text className="history-chat-title">New chat</Text>
              </Space>
            </button>
          }
          dataSource={sortedChats}
          className="overflow-y-auto"
          renderItem={(chat) => {
            const isActive = chat.id === activeChatId

            return (
              <List.Item className="!border-none !px-0 !py-1">
                <button
                  type="button"
                  onClick={() => onSelectChat(chat.id)}
                  className={`history-chat-item ${isActive ? 'history-chat-item-active' : ''}`}
                >
                  <Space direction="vertical" size={2} className="w-full">
                    <div className="flex items-start justify-between gap-2">
                      <Text strong={isActive} className="line-clamp-2 history-chat-title">
                        {chat.title || 'Untitled chat'}
                      </Text>

                      <Tooltip title="More actions (coming soon)">
                        <Button
                          type="text"
                          size="small"
                          icon={<MoreHorizontal className="h-4 w-4" />}
                          onClick={(event) => event.stopPropagation()}
                        />
                      </Tooltip>
                    </div>

                    <div className="flex items-center justify-between gap-2">
                      <Text type="secondary" className="text-xs history-chat-meta">
                        {formatRelativeTime(chat.updatedAt)}
                      </Text>
                    </div>
                  </Space>
                </button>
              </List.Item>
            )
          }}
        />
      )}

      {!collapsed && sortedChats.length === 0 && (
        <button
          type="button"
          onClick={onNewChat}
          className="history-chat-item"
        >
          <Space align="center" size="small">
            <MessageSquarePlus className="h-4 w-4" />
            <Text className="history-chat-title">New chat</Text>
          </Space>
        </button>
      )}
    </div>
  )
}
