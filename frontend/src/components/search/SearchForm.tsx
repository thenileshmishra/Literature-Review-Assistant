'use client'

import { useState, useRef, useEffect } from 'react'
import { ArrowUp, Loader2 } from 'lucide-react'
import type { CreateReviewRequest } from '@/lib/types/api'

interface SearchFormProps {
  onSubmit: (request: CreateReviewRequest) => void
  isLoading?: boolean
}

const COOLDOWN_MS = 10_000 // 10s cooldown between submissions

export function SearchForm({ onSubmit, isLoading = false }: SearchFormProps) {
  const [value, setValue] = useState('')
  const [error, setError] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const lastSubmitRef = useRef<number>(0)

  useEffect(() => {
    textareaRef.current?.focus()
  }, [])

  const autoResize = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }

  const handleSubmit = () => {
    const trimmed = value.trim()
    setError('')

    if (trimmed.length < 3) {
      setError('Topic must be at least 3 characters long')
      return
    }

    // Frontend cooldown
    const now = Date.now()
    const elapsed = now - lastSubmitRef.current
    if (elapsed < COOLDOWN_MS) {
      const wait = Math.ceil((COOLDOWN_MS - elapsed) / 1000)
      setError(`Please wait ${wait}s before submitting again.`)
      return
    }
    lastSubmitRef.current = now

    onSubmit({ topic: trimmed })
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (!isLoading && value.trim()) {
        handleSubmit()
      }
    }
  }

  return (
    <div className="composer-container">
      <h1 className="composer-heading">What would you like to review?</h1>

      <div className="composer-box">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => {
            setValue(e.target.value)
            autoResize()
          }}
          onKeyDown={handleKeyDown}
          placeholder="Enter an AI/ML research topic..."
          disabled={isLoading}
          rows={1}
        />
        <button
          type="button"
          className="composer-submit-btn"
          onClick={handleSubmit}
          disabled={isLoading || !value.trim()}
          aria-label="Submit"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <ArrowUp className="h-4 w-4" />
          )}
        </button>
      </div>

      {error && (
        <p className="text-sm mt-3 text-destructive">{error}</p>
      )}
    </div>
  )
}
