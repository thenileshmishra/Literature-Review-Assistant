'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PaperCard } from './PaperCard'
import { FileText, Loader2 } from 'lucide-react'
import { getReview } from '@/lib/api/reviews'
import type { Paper } from '@/lib/types/api'

interface PaperListProps {
  reviewId: string
}

export function PaperList({ reviewId }: PaperListProps) {
  const [papers, setPapers] = useState<Paper[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPapers = async () => {
      try {
        setIsLoading(true)
        const review = await getReview(reviewId)
        setPapers(review.papers || [])
      } catch (err: any) {
        setError(err.message || 'Failed to load papers')
      } finally {
        setIsLoading(false)
      }
    }

    if (reviewId) {
      fetchPapers()
    }
  }, [reviewId])

  if (isLoading) {
    return (
      <Card className="border-blue-500/20">
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-blue-400" />
          <span className="ml-2 text-sm text-muted-foreground">Loading papers...</span>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="border-destructive/20">
        <CardContent className="py-8">
          <p className="text-sm text-destructive text-center">{error}</p>
        </CardContent>
      </Card>
    )
  }

  if (papers.length === 0) {
    return (
      <Card className="border-blue-500/20">
        <CardContent className="py-8">
          <p className="text-sm text-muted-foreground text-center">No papers found</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <Card className="border-blue-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-400" />
            Found Papers ({papers.length})
          </CardTitle>
        </CardHeader>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        {papers.map((paper, index) => (
          <PaperCard key={index} paper={paper} />
        ))}
      </div>
    </div>
  )
}
