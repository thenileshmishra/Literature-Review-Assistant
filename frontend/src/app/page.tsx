'use client'

import { useState } from 'react'
import { Header } from '@/components/layout/Header'
import { SearchForm } from '@/components/search/SearchForm'
import { MessageDisplay } from '@/components/chat/MessageDisplay'
import { PaperList } from '@/components/papers/PaperList'
import type { CreateReviewRequest } from '@/lib/types/api'
import { createReview } from '@/lib/api/reviews'
import { useReviewStream } from '@/lib/hooks/useReviewStream'
import { Loader2 } from 'lucide-react'

export default function Home() {
  const [reviewId, setReviewId] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { messages, status, isStreaming, error: streamError, startStream } = useReviewStream(reviewId)

  const handleSubmit = async (request: CreateReviewRequest) => {
    try {
      setIsCreating(true)
      setError(null)

      // Create review
      const review = await createReview(request)
      setReviewId(review.id)

      // Start streaming
      setTimeout(() => {
        startStream()
      }, 500)

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create review')
      console.error('Error creating review:', err)
    } finally {
      setIsCreating(false)
    }
  }

  const handleNewSearch = () => {
    setReviewId(null)
    setError(null)
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <Header />

      <div className="mt-8 space-y-6">
        {!reviewId ? (
          <SearchForm onSubmit={handleSubmit} isLoading={isCreating} />
        ) : (
          <div className="space-y-6">
            <button
              onClick={handleNewSearch}
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              ← New Search
            </button>

            {isStreaming && (
              <div className="flex items-center gap-2 text-blue-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Processing review...</span>
              </div>
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
          <div className="p-4 bg-destructive/10 border border-destructive rounded-lg">
            <p className="text-sm text-destructive">{error || streamError}</p>
          </div>
        )}
      </div>
    </div>
  )
}
