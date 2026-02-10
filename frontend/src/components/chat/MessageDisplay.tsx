'use client'

import { useEffect, useMemo, useState } from 'react'
import { Card, Space, Tag, Typography, Button, Empty } from 'antd'
import { Bot, AlertCircle } from 'lucide-react'
import type { Message, ReviewStatus } from '@/lib/types/api'

type ResearchStage = 'reviewing' | 'selecting' | 'summarizing'

interface MessageDisplayProps {
  messages: Message[]
  status: ReviewStatus
}

interface ResearchProgressCardProps {
  stage: ResearchStage
  processedPapers: number
  totalPapers: number
  percent: number
}

interface SummaryCardProps {
  summaries: Message[]
}

const STAGE_LABELS: Record<ResearchStage, string> = {
  reviewing: 'Literature review',
  selecting: 'Selecting papers',
  summarizing: 'Generating summaries',
}

function ResearchProgressCard({ stage, processedPapers, totalPapers, percent }: ResearchProgressCardProps) {
  return (
    <Card className="chat-card">
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Space align="center" size="middle">
          <div className="app-logo">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <Typography.Text strong>Conducting Deep Research</Typography.Text>
            <div className="text-xs text-muted-foreground">{STAGE_LABELS[stage]}</div>
          </div>
          <Tag color="blue">In progress</Tag>
        </Space>
      </Space>
    </Card>
  )
}

function SummaryCard({ summaries }: SummaryCardProps) {
  const renderInlineMarkdown = (text: string, allowBold = true) => {
    const nodes: React.ReactNode[] = []
    const regex = allowBold
      ? /(\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))/g
      : /(\[[^\]]+\]\([^)]+\))/g
    let lastIndex = 0
    let match: RegExpExecArray | null
    useEffect(() => {
    console.log('Summaries received:', summaries)
  }, [summaries])
    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        nodes.push(text.slice(lastIndex, match.index))
      }

      const token = match[0]
      if (token.startsWith('**')) {
        const inner = token.slice(2, -2)
        nodes.push(
          <strong key={`bold-${match.index}`}>
            {renderInlineMarkdown(inner, false)}
          </strong>
        )
      } else if (token.startsWith('[')) {
        const linkMatch = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/)
        if (linkMatch) {
          const [, label, href] = linkMatch
          nodes.push(
            <a key={`link-${match.index}`} href={href} target="_blank" rel="noreferrer" className="text-blue-500">
              {label}
            </a>
          )
        } else {
          nodes.push(token)
        }
      }

      lastIndex = match.index + token.length
    }

    if (lastIndex < text.length) {
      nodes.push(text.slice(lastIndex))
    }

    return nodes
  }

  const renderTextBlock = (content: string) => {
    const lines = content.split('\n')
    return lines.map((line, index) => (
      <span key={`line-${index}`}>
        {renderInlineMarkdown(line)}
        {index < lines.length - 1 && <br />}
      </span>
    ))
  }

  const cleanContent = (content: string) => {
    return content
      .replace(/^\s*(summarizer|summarizer_agent|search_agent|system)\s*:\s*/i, '')
      .replace(/```/g, '')
      .trim()
  }

  if (summaries.length === 0) {
    return (
      <Card className="chat-card">
        <Empty description="No summaries available yet" />
      </Card>
    )
  }

  return (
    <Card className="chat-card">
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Space align="center" size="middle">
          <div className="app-logo">
            <Bot className="h-5 w-5" />
          </div>
          <Typography.Text strong>Literature Review Summary</Typography.Text>
        </Space>
        {summaries.map((message, index) => (
          <Typography.Paragraph key={`${message.timestamp}-${index}`} className="message-text" ellipsis={false}>
            {renderTextBlock(cleanContent(message.content))}
          </Typography.Paragraph>
        ))}
      </Space>
    </Card>
  )
}

export function MessageDisplay({ messages, status }: MessageDisplayProps) {
  const [totalPapers, setTotalPapers] = useState<number>(0)
  const [processedPapers, setProcessedPapers] = useState<number>(0)
  const [stage, setStage] = useState<ResearchStage>('reviewing')

  const parseSearchResults = (content: string) => {
    const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/i)
    const fallbackMatch = content.match(/```\s*([\s\S]*?)\s*```/i)
    const jsonCandidate = jsonMatch?.[1] || fallbackMatch?.[1] || content

    const tryParse = (value: string) => {
      try {
        return JSON.parse(value)
      } catch {
        return null
      }
    }

    const direct = tryParse(jsonCandidate)
    if (Array.isArray(direct)) return direct
    if (direct && Array.isArray(direct.papers)) return direct.papers

    const arrayMatch = jsonCandidate.match(/\[[\s\S]*\]/)
    if (arrayMatch) {
      const arrayParsed = tryParse(arrayMatch[0])
      if (Array.isArray(arrayParsed)) return arrayParsed
    }

    return null
  }

  const isSearchMessage = (message: Message) => message.source === 'search_agent'
  const isSummaryMessage = (message: Message) => {
    if (message.message_type === 'summary') return true
    return /summarizer/i.test(message.source)
  }

  useEffect(() => {
    const searchMessages = messages.filter(isSearchMessage)
    const summaryMessages = messages.filter(isSummaryMessage)

    let nextTotal = 0
    for (const message of searchMessages) {
      const parsed = parseSearchResults(message.content)
      if (parsed && parsed.length > nextTotal) {
        nextTotal = parsed.length
      }
    }

    const linkRegex = /\[[^\]]+\]\([^)]+\)/g
    const summaryCount = summaryMessages.reduce((count, message) => {
      const matches = message.content.match(linkRegex)
      return count + (matches ? matches.length : 0)
    }, 0)

    let nextProcessed = summaryCount
    if (nextProcessed === 0 && summaryMessages.length > 0) {
      nextProcessed = summaryMessages.length
    }

    if (nextTotal > 0) {
      nextProcessed = Math.min(nextProcessed, nextTotal)
    }

    let nextStage: ResearchStage = 'reviewing'
    if (summaryMessages.length > 0) {
      nextStage = 'summarizing'
    } else if (nextTotal > 0) {
      nextStage = 'selecting'
    } else if (searchMessages.length > 0) {
      nextStage = 'reviewing'
    }

    setTotalPapers(nextTotal)
    setProcessedPapers(nextProcessed)
    setStage(nextStage)
  }, [messages])

  const summaryMessages = useMemo(() => {
    const summaries = messages.filter(isSummaryMessage)
    if (summaries.length > 0) return summaries

    return messages.filter((message) => !isSearchMessage(message) && message.message_type !== 'error')
  }, [messages])

  const percent =
    totalPapers > 0
      ? Math.round((processedPapers / totalPapers) * 100)
      : 0

  if (status === 'completed' && summaryMessages.length > 0) {
  return (
    <SummaryCard
      summaries={[summaryMessages[summaryMessages.length - 1]]}
    />
  )
}



  if (status === 'failed') {
    return (
      <Card className="chat-card">
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Space align="center" size="middle">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <div>
              <Typography.Text strong>Research failed</Typography.Text>
              <div className="text-xs text-muted-foreground">Please try again.</div>
            </div>
            <Tag color="red">Error</Tag>
          </Space>
          <Button type="primary" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Space>
      </Card>
    )
  }

  if (status === 'in_progress') {
    return (
      <ResearchProgressCard
        stage={stage}
        processedPapers={processedPapers}
        totalPapers={totalPapers}
        percent={percent}
      />
    )
  }

  return null
}
