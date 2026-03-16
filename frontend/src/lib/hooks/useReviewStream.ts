/**
 * Custom hook for SSE streaming of review updates.
 * Streaming state is managed locally and can be persisted by parent callbacks.
 */

'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { API_URL } from '../api/client'
import type { Message, ReviewStatus, SSEEvent } from '../types/api'

interface StreamUpdatePayload {
  reviewId: string
  messages: Message[]
  status: ReviewStatus
}

interface UseReviewStreamOptions {
  onUpdate?: (payload: StreamUpdatePayload) => void
}

interface UseReviewStreamResult {
  messages: Message[]
  status: ReviewStatus
  isStreaming: boolean
  error: string | null
  startStream: () => void
  stopStream: () => void
}

export function useReviewStream(
  reviewId: string | null,
  options?: UseReviewStreamOptions
): UseReviewStreamResult {
  const [messages, setMessages] = useState<Message[]>([])
  const [status, setStatus] = useState<ReviewStatus>('pending')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!reviewId || !options?.onUpdate) return
    options.onUpdate({ reviewId, messages, status })
  }, [reviewId, messages, options, status])

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
      setIsStreaming(false)
    }
  }, [])

  const startStream = useCallback(() => {
    if (!reviewId) return

    stopStream()

    setMessages([])
    setIsStreaming(true)
    setStatus('in_progress')
    setError(null)

    const token = typeof window !== 'undefined' ? localStorage.getItem('litrev-access-token') : null
    const qs = token ? `?token=${encodeURIComponent(token)}` : ''
    const eventSource = new EventSource(`${API_URL}/api/v1/reviews/${reviewId}/stream${qs}`)
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
    if (!reviewId) {
      stopStream()
      setMessages([])
      setStatus('pending')
      setError(null)
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
