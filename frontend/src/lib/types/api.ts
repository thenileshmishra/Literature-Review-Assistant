/**
 * API types matching backend models
 */

export type ReviewStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

export type MessageType = 'search' | 'summary' | 'critique' | 'planning' | 'system' | 'error'

export interface Message {
  source: string
  content: string
  timestamp: string
  message_type: MessageType
}

export interface Paper {
  title: string
  authors: string[]
  published: string
  summary: string
  pdf_url: string
}

export interface CreateReviewRequest {
  topic: string
}

export interface ReviewResponse {
  id: string
  status: ReviewStatus
  request: {
    topic: string
    papers_limit: number
    model?: string
  }
  messages: Message[]
  papers: Paper[]
  created_at: string
  completed_at: string | null
}

export interface SSEMessageEvent {
  source: string
  content: string
  timestamp: string
  message_type: MessageType
}

export interface SSECompleteEvent {
  type: 'complete'
  session_id: string
  timestamp: string
}

export interface SSEErrorEvent {
  type: 'error'
  error: string
  timestamp: string
}

export type SSEEvent = SSEMessageEvent | SSECompleteEvent | SSEErrorEvent
