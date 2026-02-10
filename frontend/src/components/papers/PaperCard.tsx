'use client'

import { Card, Button, Typography, Divider, Space } from 'antd'
import { ExternalLink, Calendar, Users } from 'lucide-react'
import type { Paper } from '@/lib/types/api'
import { formatDate, formatAuthors } from '@/lib/utils'

interface PaperCardProps {
  paper: Paper
}

export function PaperCard({ paper }: PaperCardProps) {
  return (
    <Card className="panel-card" bordered={false}>
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        <Typography.Title level={5} style={{ marginBottom: 0 }}>
          {paper.title}
        </Typography.Title>

        <Space size="middle" wrap className="text-xs">
          <span className="meta-chip">
            <Users className="h-3 w-3" />
            {formatAuthors(paper.authors)}
          </span>
          <span className="meta-chip">
            <Calendar className="h-3 w-3" />
            {formatDate(paper.published)}
          </span>
        </Space>

        <Divider style={{ margin: '8px 0' }} />

        <Typography.Paragraph
          type="secondary"
          ellipsis={{ rows: 4, expandable: true, symbol: 'Show more' }}
        >
          {paper.summary}
        </Typography.Paragraph>

        <Button
          type="primary"
          block
          icon={<ExternalLink className="h-4 w-4" />}
          href={paper.pdf_url}
          target="_blank"
        >
          View PDF
        </Button>
      </Space>
    </Card>
  )
}
