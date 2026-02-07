'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ExternalLink, ChevronDown, ChevronUp, Calendar, Users } from 'lucide-react'
import type { Paper } from '@/lib/types/api'
import { formatDate, formatAuthors, truncateText } from '@/lib/utils'

interface PaperCardProps {
  paper: Paper
}

export function PaperCard({ paper }: PaperCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <Card className="border-blue-500/20 hover:border-blue-500/40 transition-colors">
      <CardHeader>
        <CardTitle className="text-lg leading-tight">{paper.title}</CardTitle>
        <CardDescription className="flex flex-wrap items-center gap-3 text-xs">
          <span className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            {formatAuthors(paper.authors)}
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {formatDate(paper.published)}
          </span>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <h4 className="text-sm font-semibold mb-2">Abstract</h4>
          <p className="text-sm text-muted-foreground">
            {isExpanded ? paper.summary : truncateText(paper.summary, 200)}
          </p>
          {paper.summary.length > 200 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="mt-2 h-auto p-0 text-blue-400 hover:text-blue-300"
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="h-4 w-4 mr-1" />
                  Show less
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4 mr-1" />
                  Show more
                </>
              )}
            </Button>
          )}
        </div>
      </CardContent>
      <CardFooter>
        <Button
          variant="default"
          size="sm"
          asChild
          className="w-full"
        >
          <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="h-4 w-4 mr-2" />
            View PDF
          </a>
        </Button>
      </CardFooter>
    </Card>
  )
}
