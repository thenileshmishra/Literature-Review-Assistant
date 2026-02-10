'use client'

import { useEffect, useRef } from 'react'
import { Card, List, Typography, Avatar, Tag, Empty } from 'antd'
import { Bot, AlertCircle } from 'lucide-react'
import type { Message, ReviewStatus } from '@/lib/types/api'

interface MessageDisplayProps {
  messages: Message[]
  status: ReviewStatus
}

export function MessageDisplay({ messages, status }: MessageDisplayProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const statusTag =
    status === 'in_progress'
      ? <Tag color="blue">Processing</Tag>
      : status === 'completed'
      ? <Tag color="green">Completed</Tag>
      : status === 'failed'
      ? <Tag color="red">Failed</Tag>
      : null

  return (
    <Card
      title={
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4" />
          <span>Agent messages</span>
        </div>
      }
      extra={statusTag}
      className="chat-card"
    >
      <div className="chat-scroll">
        {messages.length === 0 ? (
          <Empty description="Waiting for agents to start" />
        ) : (
          <List
            dataSource={messages}
            renderItem={(message, index) => (
              <List.Item
                key={`${message.timestamp}-${index}`}
                className={message.message_type === 'error' ? 'message-row message-row-error' : 'message-row'}
              >
                <List.Item.Meta
                  avatar={
                    <Avatar
                      className={message.message_type === 'error' ? 'avatar-error' : 'avatar-default'}
                      icon={message.message_type === 'error' ? <AlertCircle className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                    />
                  }
                  title={
                    <div className="flex items-center gap-2">
                      <Typography.Text strong>
                        {message.source === 'search_agent'
                          ? 'Search agent'
                          : message.source === 'summarizer'
                          ? 'Summarizer agent'
                          : 'System'}
                      </Typography.Text>
                      <Typography.Text type="secondary" className="text-xs">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </Typography.Text>
                    </div>
                  }
                  description={
                    <Typography.Paragraph className="message-text" ellipsis={false}>
                      {message.content}
                    </Typography.Paragraph>
                  }
                />
              </List.Item>
            )}
          />
        )}
        <div ref={messagesEndRef} />
      </div>
    </Card>
  )
}
