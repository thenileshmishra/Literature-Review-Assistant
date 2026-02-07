'use client'

import { useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Bot, User, AlertCircle } from 'lucide-react'
import type { Message, ReviewStatus } from '@/lib/types/api'
import { cn } from '@/lib/utils'

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

  return (
    <Card className="border-blue-500/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-blue-400" />
          Agent Messages
          <span className="ml-auto text-sm font-normal text-muted-foreground">
            {status === 'in_progress' && '🔄 Processing...'}
            {status === 'completed' && '✓ Completed'}
            {status === 'failed' && '✗ Failed'}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 max-h-[500px] overflow-y-auto">
        {messages.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">
            Waiting for agents to start...
          </p>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={cn(
                "message-slide-in p-4 rounded-lg",
                message.message_type === 'error'
                  ? 'bg-destructive/10 border border-destructive/20'
                  : 'bg-card border border-blue-500/20'
              )}
            >
              <div className="flex items-start gap-3">
                <div className={cn(
                  "flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center",
                  message.source === 'search_agent'
                    ? 'bg-blue-500/20'
                    : message.source === 'summarizer'
                    ? 'bg-purple-500/20'
                    : 'bg-gray-500/20'
                )}>
                  {message.message_type === 'error' ? (
                    <AlertCircle className="h-4 w-4 text-destructive" />
                  ) : (
                    <Bot className="h-4 w-4 text-blue-400" />
                  )}
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold">
                      {message.source === 'search_agent'
                        ? 'Search Agent'
                        : message.source === 'summarizer'
                        ? 'Summarizer Agent'
                        : 'System'}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-foreground/90 whitespace-pre-wrap">
                    {message.content}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </CardContent>
    </Card>
  )
}
