/**
 * Custom hook for SSE streaming of review updates.
 * Persists results to sessionStorage so they survive page refreshes.
 */

'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { API_URL } from '../api/client'
import type { Message, ReviewStatus, SSEEvent } from '../types/api'

const STORAGE_KEY = 'litrev-session'

interface StoredSession {
  reviewId: string
  messages: Message[]
  status: ReviewStatus
}

interface UseReviewStreamResult {
  messages: Message[]
  status: ReviewStatus
  isStreaming: boolean
  error: string | null
  startStream: () => void
  stopStream: () => void
}

function loadSession(): StoredSession | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function saveSession(session: StoredSession) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session))
  } catch { /* quota exceeded — ignore */ }
}

export function clearSession() {
  sessionStorage.removeItem(STORAGE_KEY)
}

export function getStoredReviewId(): string | null {
  return loadSession()?.reviewId ?? null
}

export function useReviewStream(reviewId: string | null): UseReviewStreamResult {
  const cached = reviewId ? loadSession() : null
  const isRestoredSession = cached?.reviewId === reviewId && cached?.status === 'completed'

  const [messages, setMessages] = useState<Message[]>(isRestoredSession ? cached!.messages : [])
  const [status, setStatus] = useState<ReviewStatus>(isRestoredSession ? 'completed' : 'pending')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)

  // Persist to sessionStorage whenever messages or status change
  useEffect(() => {
    if (!reviewId || messages.length === 0) return
    saveSession({ reviewId, messages, status })
  }, [reviewId, messages, status])

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
      setIsStreaming(false)
    }
  }, [])

  const startStream = useCallback(() => {
    if (!reviewId) return

    // Don't re-stream a completed session restored from storage
    const stored = loadSession()
    if (stored?.reviewId === reviewId && stored.status === 'completed') return

    stopStream()

    setMessages([])
    setIsStreaming(true)
    setStatus('in_progress')
    setError(null)

    const eventSource = new EventSource(`${API_URL}/api/v1/reviews/${reviewId}/stream`)
    eventSourceRef.current = eventSource

    eventSource.addEventListener('message', (e) => {
      try {
        const data: SSEEvent = JSON.parse(e.data)

        if ('source' in data && 'content' in data) {
          const message: Message = {
            source: data.source,
            content: data.content,
            timestamp: data.timestamp,
            message_type: data.message_type,
          }
          setMessages((prev) => [...prev, message])
        }
      } catch (err) {
        console.error('Error parsing message:', err)
      }
    })

    eventSource.addEventListener('complete', () => {
      setStatus('completed')
      setIsStreaming(false)
      stopStream()
    })

    eventSource.addEventListener('error', (e: any) => {
      try {
        if (e.data) {
          const errorData = JSON.parse(e.data)
          setError(errorData.error || 'An error occurred')
        }
      } catch {
        setError('Connection error occurred')
      }
      setStatus('failed')
      setIsStreaming(false)
      stopStream()
    })

    eventSource.onerror = () => {
      if (eventSource.readyState === EventSource.CLOSED) {
        setError('Connection closed')
        setIsStreaming(false)
        stopStream()
      }
    }
  }, [reviewId, stopStream])

  useEffect(() => {
    return () => {
      stopStream()
    }
  }, [stopStream])

  return {
    messages,
    status,
    isStreaming,
    error,
    startStream,
    stopStream,
  }
}
