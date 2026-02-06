/**
 * Custom hook for SSE streaming of review updates
 */

'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { API_URL } from '../api/client'
import type { Message, ReviewStatus, SSEEvent } from '../types/api'

interface UseReviewStreamResult {
  messages: Message[]
  status: ReviewStatus
  isStreaming: boolean
  error: string | null
  startStream: () => void
  stopStream: () => void
}

export function useReviewStream(reviewId: string | null): UseReviewStreamResult {
  const [messages, setMessages] = useState<Message[]>([])
  const [status, setStatus] = useState<ReviewStatus>('pending')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
      setIsStreaming(false)
    }
  }, [])

  const startStream = useCallback(() => {
    if (!reviewId) return

    // Close existing connection
    stopStream()

    setIsStreaming(true)
    setStatus('in_progress')
    setError(null)

    // Create EventSource for SSE
    const eventSource = new EventSource(`${API_URL}/api/v1/reviews/${reviewId}/stream`)
    eventSourceRef.current = eventSource

    // Handle message events
    eventSource.addEventListener('message', (e) => {
      try {
        const data: SSEEvent = JSON.parse(e.data)

        if ('source' in data && 'content' in data) {
          // Regular message
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

    // Handle complete event
    eventSource.addEventListener('complete', (e) => {
      console.log('Review completed:', e.data)
      setStatus('completed')
      setIsStreaming(false)
      stopStream()
    })

    // Handle error event
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

    // Handle connection error
    eventSource.onerror = () => {
      if (eventSource.readyState === EventSource.CLOSED) {
        setError('Connection closed')
        setIsStreaming(false)
        stopStream()
      }
    }
  }, [reviewId, stopStream])

  // Cleanup on unmount
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
