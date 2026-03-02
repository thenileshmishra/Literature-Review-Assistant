'use client'

import { useEffect, useMemo, useState } from 'react'
import { Card, Space, Tag, Typography, Button, Empty } from 'antd'
import { Bot, AlertCircle, ClipboardCheck, Search, BrainCircuit, FileText, ChevronDown, ChevronRight, Loader2 } from 'lucide-react'
import type { Message, ReviewStatus } from '@/lib/types/api'

type ResearchStage = 'planning' | 'searching' | 'summarizing' | 'critiquing' | 'revising'

interface MessageDisplayProps {
  messages: Message[]
  status: ReviewStatus
}

const STAGE_CONFIG: Record<ResearchStage, { label: string; description: string }> = {
  planning: { label: 'Planning', description: 'Decomposing topic into sub-queries' },
  searching: { label: 'Searching', description: 'Querying arXiv & Semantic Scholar' },
  summarizing: { label: 'Summarizing', description: 'Writing literature review' },
  critiquing: { label: 'Critiquing', description: 'Evaluating review quality' },
  revising: { label: 'Revising', description: 'Improving based on feedback' },
}

const STAGE_ORDER: ResearchStage[] = ['planning', 'searching', 'summarizing', 'critiquing', 'revising']

// ── Helper: classify messages ──
function isPlannerMessage(m: Message) { return m.source === 'planner' || m.message_type === 'planning' }
function isSearchMessage(m: Message) { return m.source === 'search_agent' || m.message_type === 'search' }
function isSummaryMessage(m: Message) { return m.message_type === 'summary' || /summarizer/i.test(m.source) }
function isCritiqueMessage(m: Message) { return m.message_type === 'critique' || m.source === 'critic' }

// ── Thinking step card (collapsible) ──
function ThinkingStep({ icon, title, tag, children, defaultOpen = false }: {
  icon: React.ReactNode
  title: string
  tag?: React.ReactNode
  children: React.ReactNode
  defaultOpen?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="thinking-step">
      <button
        type="button"
        className="thinking-step-header"
        onClick={() => setOpen(!open)}
      >
        <span className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium">{title}</span>
          {tag}
        </span>
        {open ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
      </button>
      {open && <div className="thinking-step-body">{children}</div>}
    </div>
  )
}

// ── Parse planner sub-queries from content ──
function parseSubQueries(content: string): string[] {
  // Try JSON array
  const jsonMatch = content.match(/\[[\s\S]*?\]/)
  if (jsonMatch) {
    try {
      const arr = JSON.parse(jsonMatch[0])
      if (Array.isArray(arr) && arr.every((s) => typeof s === 'string')) return arr
    } catch { /* ignore */ }
  }
  // Fallback: numbered/bulleted lines
  const lines = content.split('\n').filter((l) => /^\s*[\d\-\*•]+[\.\)]\s/.test(l))
  if (lines.length > 0) return lines.map((l) => l.replace(/^\s*[\d\-\*•]+[\.\)]\s*/, '').trim())
  return []
}

// ── Parse paper count from search messages ──
function parseSearchPaperCount(content: string): { arxiv: number; scholar: number } {
  const counts = { arxiv: 0, scholar: 0 }
  const arxivMatch = content.match(/arxiv/i)
  const scholarMatch = content.match(/semantic.?scholar/i)

  // Try to extract JSON papers array
  const jsonMatch = content.match(/\[[\s\S]*?\]/)
  if (jsonMatch) {
    try {
      const arr = JSON.parse(jsonMatch[0])
      if (Array.isArray(arr)) {
        const total = arr.length
        // Split roughly if both sources mentioned
        if (arxivMatch && scholarMatch) {
          counts.arxiv = Math.ceil(total / 2)
          counts.scholar = total - counts.arxiv
        } else if (arxivMatch) {
          counts.arxiv = total
        } else if (scholarMatch) {
          counts.scholar = total
        } else {
          counts.arxiv = Math.ceil(total / 2)
          counts.scholar = total - counts.arxiv
        }
      }
    } catch { /* ignore */ }
  }
  return counts
}

// ── Summary card (markdown renderer) ──
function SummaryCard({ summaries }: { summaries: Message[] }) {
  const renderInlineMarkdown = (text: string, allowBold = true) => {
    const nodes: React.ReactNode[] = []
    const regex = allowBold
      ? /(\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))/g
      : /(\[[^\]]+\]\([^)]+\))/g
    let lastIndex = 0
    let match: RegExpExecArray | null

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) nodes.push(text.slice(lastIndex, match.index))
      const token = match[0]
      if (token.startsWith('**')) {
        nodes.push(<strong key={`b-${match.index}`}>{renderInlineMarkdown(token.slice(2, -2), false)}</strong>)
      } else if (token.startsWith('[')) {
        const lm = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/)
        if (lm) {
          nodes.push(<a key={`l-${match.index}`} href={lm[2]} target="_blank" rel="noreferrer" className="text-blue-500">{lm[1]}</a>)
        } else { nodes.push(token) }
      }
      lastIndex = match.index + token.length
    }
    if (lastIndex < text.length) nodes.push(text.slice(lastIndex))
    return nodes
  }

  const renderTextBlock = (content: string) => {
    return content.split('\n').map((line, i) => {
      const h3 = line.match(/^###\s+(.+)/); if (h3) return <h5 key={i} className="mt-3 mb-1 font-semibold">{renderInlineMarkdown(h3[1])}</h5>
      const h2 = line.match(/^##\s+(.+)/); if (h2) return <h4 key={i} className="mt-3.5 mb-1 font-semibold">{renderInlineMarkdown(h2[1])}</h4>
      const h1 = line.match(/^#\s+(.+)/); if (h1) return <h3 key={i} className="mt-4 mb-1.5 font-bold">{renderInlineMarkdown(h1[1])}</h3>
      return <span key={i}>{renderInlineMarkdown(line)}<br /></span>
    })
  }

  const clean = (c: string) => c.replace(/^\s*(summarizer|summarizer_agent|search_agent|system)\s*:\s*/i, '').replace(/```/g, '').trim()

  if (summaries.length === 0) return <Card className="chat-card"><Empty description="No summaries available yet" /></Card>

  return (
    <Card className="chat-card">
      <Space direction="vertical" size="middle" className="w-full">
        <Space align="center" size="middle">
          <div className="app-logo"><Bot className="h-5 w-5" /></div>
          <Typography.Text strong>Literature Review Summary</Typography.Text>
        </Space>
        {summaries.map((msg, i) => (
          <Typography.Paragraph key={`${msg.timestamp}-${i}`} className="message-text" ellipsis={false}>
            {renderTextBlock(clean(msg.content))}
          </Typography.Paragraph>
        ))}
      </Space>
    </Card>
  )
}

// ── Critique card ──
function CritiqueCard({ critique }: { critique: Message }) {
  const content = critique.content.replace(/^\s*critic\s*:\s*/i, '').trim()
  return (
    <ThinkingStep
      icon={<ClipboardCheck className="h-4 w-4" style={{ color: '#faad14' }} />}
      title="Critic Feedback"
      tag={<Tag color="gold" className="text-xs">Review</Tag>}
      defaultOpen={false}
    >
      <div className="text-sm leading-relaxed whitespace-pre-wrap">{content}</div>
    </ThinkingStep>
  )
}

// ── Main component ──
export function MessageDisplay({ messages, status }: MessageDisplayProps) {
  const [stage, setStage] = useState<ResearchStage>('planning')

  const plannerMessages = useMemo(() => messages.filter(isPlannerMessage), [messages])
  const searchMessages = useMemo(() => messages.filter(isSearchMessage), [messages])
  const summaryMessages = useMemo(() => {
    const s = messages.filter(isSummaryMessage)
    return s.length > 0 ? s : messages.filter((m) => !isSearchMessage(m) && !isCritiqueMessage(m) && m.message_type !== 'error')
  }, [messages])
  const critiqueMessages = useMemo(() => messages.filter(isCritiqueMessage), [messages])

  // Sub-queries extracted from planner
  const subQueries = useMemo(() => {
    for (const m of plannerMessages) {
      const q = parseSubQueries(m.content)
      if (q.length > 0) return q
    }
    return []
  }, [plannerMessages])

  // Paper counts from search
  const searchInfo = useMemo(() => {
    let totalPapers = 0
    let arxivCount = 0
    let scholarCount = 0
    for (const m of searchMessages) {
      const counts = parseSearchPaperCount(m.content)
      arxivCount += counts.arxiv
      scholarCount += counts.scholar
      totalPapers += counts.arxiv + counts.scholar
    }
    return { totalPapers, arxivCount, scholarCount }
  }, [searchMessages])

  // Determine current stage
  useEffect(() => {
    const last = messages.length > 0 ? messages[messages.length - 1] : null
    if (!last) { setStage('planning'); return }

    if (critiqueMessages.length > 0 && last.source === 'critic') setStage('critiquing')
    else if (critiqueMessages.length > 0 && /summarizer/i.test(last.source)) setStage('revising')
    else if (summaryMessages.length > 0 && isSummaryMessage(last)) setStage('summarizing')
    else if (searchMessages.length > 0) setStage('searching')
    else setStage('planning')
  }, [messages, critiqueMessages.length, searchMessages.length, summaryMessages.length])

  const lastCritique = critiqueMessages.length > 0 ? critiqueMessages[critiqueMessages.length - 1] : null

  // ── COMPLETED ──
  if (status === 'completed') {
    const lastSummary = summaryMessages.length > 0 ? [summaryMessages[summaryMessages.length - 1]] : []
    return (
      <Space direction="vertical" size="middle" className="w-full">
        {/* Collapsible thinking steps */}
        {subQueries.length > 0 && (
          <ThinkingStep
            icon={<BrainCircuit className="h-4 w-4 text-purple-500" />}
            title="Planned Sub-queries"
            tag={<Tag color="purple" className="text-xs">{subQueries.length} queries</Tag>}
          >
            <ul className="list-disc pl-4 text-sm space-y-1">
              {subQueries.map((q, i) => <li key={i}>{q}</li>)}
            </ul>
          </ThinkingStep>
        )}

        {searchInfo.totalPapers > 0 && (
          <ThinkingStep
            icon={<Search className="h-4 w-4 text-blue-500" />}
            title="Papers Found"
            tag={<Tag color="blue" className="text-xs">{searchInfo.totalPapers} papers</Tag>}
          >
            <div className="flex gap-4 text-sm">
              {searchInfo.arxivCount > 0 && (
                <span className="meta-chip"><FileText className="h-3.5 w-3.5" /> arXiv: {searchInfo.arxivCount}</span>
              )}
              {searchInfo.scholarCount > 0 && (
                <span className="meta-chip"><FileText className="h-3.5 w-3.5" /> Semantic Scholar: {searchInfo.scholarCount}</span>
              )}
            </div>
          </ThinkingStep>
        )}

        {lastCritique && <CritiqueCard critique={lastCritique} />}
        <SummaryCard summaries={lastSummary} />
      </Space>
    )
  }

  // ── FAILED ──
  if (status === 'failed') {
    return (
      <Card className="chat-card">
        <Space direction="vertical" size="middle" className="w-full">
          <Space align="center" size="middle">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <div>
              <Typography.Text strong>Research failed</Typography.Text>
              <div className="text-xs text-muted-foreground">Please try again.</div>
            </div>
            <Tag color="red">Error</Tag>
          </Space>
          <Button type="primary" onClick={() => window.location.reload()}>Retry</Button>
        </Space>
      </Card>
    )
  }

  // ── IN PROGRESS ──
  if (status === 'in_progress') {
    const currentStageIdx = STAGE_ORDER.indexOf(stage)

    return (
      <Space direction="vertical" size="middle" className="w-full">
        {/* Stage stepper */}
        <Card className="chat-card">
          <Space direction="vertical" size="small" className="w-full">
            <Space align="center" size="middle">
              <div className="app-logo"><Bot className="h-5 w-5" /></div>
              <div>
                <Typography.Text strong>Conducting Deep Research</Typography.Text>
                <div className="text-xs text-muted-foreground">{STAGE_CONFIG[stage].description}</div>
              </div>
              <Tag color="blue">In progress</Tag>
            </Space>

            {/* Stepper */}
            <div className="stage-stepper">
              {STAGE_ORDER.map((s, i) => {
                const isDone = i < currentStageIdx
                const isCurrent = i === currentStageIdx
                return (
                  <div key={s} className={`stage-step ${isDone ? 'stage-done' : ''} ${isCurrent ? 'stage-active' : ''}`}>
                    <div className="stage-dot">
                      {isDone && <Check className="h-3 w-3" />}
                      {isCurrent && <Loader2 className="h-3 w-3 animate-spin" />}
                    </div>
                    <span className="stage-label">{STAGE_CONFIG[s].label}</span>
                  </div>
                )
              })}
            </div>
          </Space>
        </Card>

        {/* Live thinking steps */}
        {subQueries.length > 0 && (
          <ThinkingStep
            icon={<BrainCircuit className="h-4 w-4 text-purple-500" />}
            title="Planned Sub-queries"
            tag={<Tag color="purple" className="text-xs">{subQueries.length} queries</Tag>}
            defaultOpen
          >
            <ul className="list-disc pl-4 text-sm space-y-1">
              {subQueries.map((q, i) => <li key={i}>{q}</li>)}
            </ul>
          </ThinkingStep>
        )}

        {searchInfo.totalPapers > 0 && (
          <ThinkingStep
            icon={<Search className="h-4 w-4 text-blue-500" />}
            title="Papers Found"
            tag={<Tag color="blue" className="text-xs">{searchInfo.totalPapers} papers</Tag>}
            defaultOpen
          >
            <div className="flex gap-4 text-sm">
              {searchInfo.arxivCount > 0 && (
                <span className="meta-chip"><FileText className="h-3.5 w-3.5" /> arXiv: {searchInfo.arxivCount}</span>
              )}
              {searchInfo.scholarCount > 0 && (
                <span className="meta-chip"><FileText className="h-3.5 w-3.5" /> Semantic Scholar: {searchInfo.scholarCount}</span>
              )}
            </div>
          </ThinkingStep>
        )}

        {lastCritique && <CritiqueCard critique={lastCritique} />}
      </Space>
    )
  }

  return null
}

// Small check icon for stepper (avoids another lucide import collision)
function Check({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" className={className}>
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}
