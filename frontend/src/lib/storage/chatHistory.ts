'use client'

import type { ChatSession } from '@/lib/types/api'

const CHATS_STORAGE_KEY = 'litrev-chats'
const ACTIVE_CHAT_STORAGE_KEY = 'litrev-active-chat'
const MAX_CHATS = 50

type UpdateChatPatch = Partial<Omit<ChatSession, 'id' | 'createdAt'>>

function canUseStorage() {
  return typeof window !== 'undefined'
}

function generateChatId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }

  return `chat-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

function readChats(): ChatSession[] {
  if (!canUseStorage()) return []

  try {
    const raw = localStorage.getItem(CHATS_STORAGE_KEY)
    if (!raw) return []

    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []

    return parsed as ChatSession[]
  } catch {
    return []
  }
}

function writeChats(chats: ChatSession[]) {
  if (!canUseStorage()) return

  const trimmed = chats
    .slice()
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, MAX_CHATS)

  localStorage.setItem(CHATS_STORAGE_KEY, JSON.stringify(trimmed))
}

export function getAllChats(): ChatSession[] {
  return readChats().sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  )
}

export function getChat(id: string): ChatSession | null {
  const chats = readChats()
  return chats.find((chat) => chat.id === id) ?? null
}

export function createChat(params?: { title?: string }): ChatSession {
  const now = new Date().toISOString()

  const newChat: ChatSession = {
    id: generateChatId(),
    title: params?.title?.trim() || 'New chat',
    createdAt: now,
    updatedAt: now,
    status: 'pending',
    messageCount: 0,
    messages: [],
  }

  const chats = readChats()
  writeChats([newChat, ...chats])

  return newChat
}

export function updateChat(id: string, patch: UpdateChatPatch): ChatSession | null {
  const chats = readChats()
  const index = chats.findIndex((chat) => chat.id === id)

  if (index === -1) return null

  const current = chats[index]
  const nextMessages = patch.messages ?? current.messages

  const updated: ChatSession = {
    ...current,
    ...patch,
    updatedAt: new Date().toISOString(),
    messageCount: nextMessages.length,
  }

  const nextChats = chats.slice()
  nextChats[index] = updated
  writeChats(nextChats)

  return updated
}

export function deleteChat(id: string): boolean {
  const chats = readChats()
  const nextChats = chats.filter((chat) => chat.id !== id)

  if (nextChats.length === chats.length) return false

  writeChats(nextChats)

  if (getActiveChatId() === id) {
    localStorage.removeItem(ACTIVE_CHAT_STORAGE_KEY)
  }

  return true
}

export function setActiveChatId(id: string | null) {
  if (!canUseStorage()) return

  if (!id) {
    localStorage.removeItem(ACTIVE_CHAT_STORAGE_KEY)
    return
  }

  localStorage.setItem(ACTIVE_CHAT_STORAGE_KEY, id)
}

export function getActiveChatId(): string | null {
  if (!canUseStorage()) return null
  return localStorage.getItem(ACTIVE_CHAT_STORAGE_KEY)
}
