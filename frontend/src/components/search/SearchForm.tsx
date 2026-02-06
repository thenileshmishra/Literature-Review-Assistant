'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Search, Loader2 } from 'lucide-react'
import type { CreateReviewRequest } from '@/lib/types/api'

interface SearchFormProps {
  onSubmit: (request: CreateReviewRequest) => void
  isLoading?: boolean
}

const EXAMPLE_TOPICS = [
  'machine learning in healthcare',
  'quantum computing algorithms',
  'climate change mitigation strategies',
  'neural networks for NLP',
]

export function SearchForm({ onSubmit, isLoading = false }: SearchFormProps) {
  const [topic, setTopic] = useState('')
  const [numPapers, setNumPapers] = useState(5)
  const [model, setModel] = useState('gpt-4o-mini')
  const [error, setError] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (topic.trim().length < 3) {
      setError('Topic must be at least 3 characters long')
      return
    }

    if (numPapers < 1 || numPapers > 10) {
      setError('Number of papers must be between 1 and 10')
      return
    }

    onSubmit({
      topic: topic.trim(),
      num_papers: numPapers,
      model,
    })
  }

  const handleExampleClick = (exampleTopic: string) => {
    setTopic(exampleTopic)
  }

  return (
    <Card className="border-blue-500/20">
      <CardHeader>
        <CardTitle>Start Your Literature Review</CardTitle>
        <CardDescription>
          Enter a research topic and let our AI agents find and summarize relevant papers
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Topic Input */}
          <div className="space-y-2">
            <Label htmlFor="topic">Research Topic</Label>
            <Input
              id="topic"
              placeholder="e.g., machine learning in healthcare"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              disabled={isLoading}
              className="text-base"
            />
            <div className="flex flex-wrap gap-2 mt-2">
              {EXAMPLE_TOPICS.map((example) => (
                <button
                  key={example}
                  type="button"
                  onClick={() => handleExampleClick(example)}
                  disabled={isLoading}
                  className="text-xs px-2 py-1 rounded-full bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 transition-colors disabled:opacity-50"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Number of Papers */}
          <div className="space-y-2">
            <Label htmlFor="numPapers">Number of Papers: {numPapers}</Label>
            <input
              id="numPapers"
              type="range"
              min="1"
              max="10"
              value={numPapers}
              onChange={(e) => setNumPapers(parseInt(e.target.value))}
              disabled={isLoading}
              className="w-full h-2 bg-blue-500/20 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>1</span>
              <span>10</span>
            </div>
          </div>

          {/* Model Selection */}
          <div className="space-y-2">
            <Label htmlFor="model">LLM Model</Label>
            <select
              id="model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              disabled={isLoading}
              className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="gpt-4o-mini">GPT-4o Mini (Fast & Efficient)</option>
              <option value="gpt-4o">GPT-4o (Balanced)</option>
              <option value="gpt-4-turbo">GPT-4 Turbo (Most Capable)</option>
            </select>
          </div>

          {/* Error Message */}
          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={isLoading}
            className="w-full"
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Starting Review...
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4" />
                Start Literature Review
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
