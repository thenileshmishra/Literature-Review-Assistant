'use client'

import { useState } from 'react'
import {
  Card,
  Form,
  Input,
  Button,
  Slider,
  Alert,
  Space,
  Typography,
} from 'antd'
import { SearchOutlined, LoadingOutlined } from '@ant-design/icons'
import type { CreateReviewRequest } from '@/lib/types/api'

const { Title, Text } = Typography
interface SearchFormProps {
  onSubmit: (request: CreateReviewRequest) => void
  isLoading?: boolean
  model: string
}


export function SearchForm({ onSubmit, isLoading = false, model }: SearchFormProps) {
  const [form] = Form.useForm()
  const [error, setError] = useState('')

  const handleFinish = (values: any) => {
    setError('')

    if (values.topic.trim().length < 3) {
      setError('Topic must be at least 3 characters long')
      return
    }

    onSubmit({
      topic: values.topic.trim(),
      num_papers: 5,
      model,
    })
  }

  return (
    <Card className="search-card" bordered={false}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={4} style={{ marginBottom: 4 }}>Start your review</Title>
          <Text type="secondary">
            Ask a focused research question and receive an agent-produced literature map.
          </Text>
        </div>

        <Form
          form={form}
          layout="vertical"
          initialValues={{
            numPapers: 5,
          }}
          onFinish={handleFinish}
        >
          {/* Topic Input */}
          <Form.Item
            name="topic"
            rules={[
              { required: true, message: 'Please enter a topic' },
              { min: 3, message: 'Topic must be at least 3 characters' },
            ]}
          >
            <Input
              placeholder="e.g., Graph-Based Memory for AI Agents"
              disabled={isLoading}
              size="large"
              prefix={<SearchOutlined />}
            />
          </Form.Item>

          {error && <Alert type="error" message={error} showIcon />}

          {/* Submit Button */}
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              block
              disabled={isLoading}
              icon={
                isLoading ? <LoadingOutlined /> : <SearchOutlined />
              }
              loading={isLoading}
            >
              {isLoading
                ? 'Starting Review...'
                : 'Start Literature Review'}
            </Button>
          </Form.Item>
        </Form>
      </Space>
    </Card>
  )
}
