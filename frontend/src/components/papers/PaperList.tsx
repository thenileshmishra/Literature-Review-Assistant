'use client'

import { useEffect, useState } from 'react'
import { Card, Spin, Empty, Typography } from 'antd'
import { PaperCard } from './PaperCard'
import { FileText } from 'lucide-react'
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
      <Card className="panel-card">
        <div className="flex items-center justify-center py-10">
          <Spin size="large" />
          <Typography.Text type="secondary" className="ml-3">
            Loading papers...
          </Typography.Text>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="panel-card">
        <Typography.Text type="danger" className="block py-6 text-center">
          {error}
        </Typography.Text>
      </Card>
    )
  }

  if (papers.length === 0) {
    return (
      <Card className="panel-card">
        <Empty description="No papers found" />
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <Card
        className="panel-card"
        title={
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            <span>Found papers</span>
          </div>
        }
        extra={<Typography.Text type="secondary">{papers.length}</Typography.Text>}
      />

      <div className="grid gap-4 md:grid-cols-2">
        {papers.map((paper, index) => (
          <PaperCard key={index} paper={paper} />
        ))}
      </div>
    </div>
  )
}
