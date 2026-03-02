'use client'

import { useMemo, useState, useRef, useEffect } from 'react'
import { MessageSquarePlus, PanelLeft, PanelRight, Pencil, Check, X } from 'lucide-react'
import type { ChatHistoryItem } from '@/lib/types/api'

interface HistorySidebarProps {
  chats: ChatHistoryItem[]
  activeChatId: string | null
  onNewChat: () => void
  onSelectChat: (chatId: string) => void
  onRenameChat: (chatId: string, newTitle: string) => void
  collapsed?: boolean
  onToggleCollapse: () => void
}

export function HistorySidebar({
  chats,
  activeChatId,
  onNewChat,
  onSelectChat,
  onRenameChat,
  collapsed = false,
  onToggleCollapse,
}: HistorySidebarProps) {
  const sortedChats = useMemo(
    () => chats.slice().sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()),
    [chats]
  )

  const [renamingId, setRenamingId] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState('')
  const renameInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (renamingId && renameInputRef.current) {
      renameInputRef.current.focus()
      renameInputRef.current.select()
    }
  }, [renamingId])

  const startRename = (chat: ChatHistoryItem, e: React.MouseEvent) => {
    e.stopPropagation()
    setRenamingId(chat.id)
    setRenameValue(chat.title)
  }

  const confirmRename = () => {
    if (renamingId && renameValue.trim()) {
      onRenameChat(renamingId, renameValue.trim())
    }
    setRenamingId(null)
    setRenameValue('')
  }

  const cancelRename = () => {
    setRenamingId(null)
    setRenameValue('')
  }

  const handleRenameKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      confirmRename()
    } else if (e.key === 'Escape') {
      cancelRename()
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Top row: toggle + new chat */}
      <div className="flex items-center justify-between px-1 py-2">
        <button
          type="button"
          onClick={onToggleCollapse}
          className="sidebar-new-chat-btn"
          aria-label={collapsed ? 'Expand sidebar' : 'Shrink sidebar'}
          title={collapsed ? 'Expand sidebar' : 'Shrink sidebar'}
        >
          {collapsed ? <PanelRight className="h-4 w-4" /> : <PanelLeft className="h-4 w-4" />}
        </button>

        <button
          type="button"
          onClick={onNewChat}
          className="sidebar-new-chat-btn"
          aria-label="New chat"
          title="New chat"
        >
          <MessageSquarePlus className="h-4 w-4" />
        </button>
      </div>

      {/* Chat list */}
      {!collapsed && (
        <nav className="flex-1 overflow-y-auto mt-2 flex flex-col gap-0.5 px-1">
          {sortedChats.map((chat) => {
            const isActive = chat.id === activeChatId
            const isRenaming = chat.id === renamingId

            if (isRenaming) {
              return (
                <div
                  key={chat.id}
                  className={`history-chat-item ${isActive ? 'history-chat-item-active' : ''}`}
                >
                  <div className="flex items-center gap-1">
                    <input
                      ref={renameInputRef}
                      type="text"
                      className="rename-input"
                      value={renameValue}
                      onChange={(e) => setRenameValue(e.target.value)}
                      onKeyDown={handleRenameKeyDown}
                      onBlur={confirmRename}
                      aria-label="Rename chat"
                      placeholder="Chat name"
                    />
                    <button
                      type="button"
                      className="flex-shrink-0 p-0.5 rounded hover:bg-accent"
                      onClick={confirmRename}
                      aria-label="Confirm rename"
                    >
                      <Check className="h-3.5 w-3.5 text-muted-foreground" />
                    </button>
                    <button
                      type="button"
                      className="flex-shrink-0 p-0.5 rounded hover:bg-accent"
                      onClick={cancelRename}
                      aria-label="Cancel rename"
                    >
                      <X className="h-3.5 w-3.5 text-muted-foreground" />
                    </button>
                  </div>
                </div>
              )
            }

            return (
              <button
                key={chat.id}
                type="button"
                onClick={() => onSelectChat(chat.id)}
                className={`history-chat-item group ${isActive ? 'history-chat-item-active' : ''}`}
              >
                <div className="flex items-center justify-between gap-1">
                  <span className="block truncate text-sm flex-1">
                    {chat.title || 'Untitled chat'}
                  </span>
                  {isActive && (
                    <span
                      role="button"
                      tabIndex={0}
                      className="flex-shrink-0 p-0.5 rounded opacity-0 group-hover:opacity-100 hover:bg-accent transition-opacity"
                      onClick={(e) => startRename(chat, e)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') startRename(chat, e as unknown as React.MouseEvent)
                      }}
                      aria-label="Rename chat"
                      title="Rename"
                    >
                      <Pencil className="h-3.5 w-3.5 text-muted-foreground" />
                    </span>
                  )}
                </div>
              </button>
            )
          })}

          {sortedChats.length === 0 && (
            <div className="px-3 py-6 text-center text-sm text-muted-foreground">
              No conversations yet
            </div>
          )}
        </nav>
      )}
    </div>
  )
}
