'use client'

import { useState } from 'react'
import { Alert, Button, Card, Form, Input, Tabs } from 'antd'
import { useAuth } from '@/lib/context/AuthContext'

export default function LoginPage() {
  const { login, register } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleLogin(values: { email: string; password: string }) {
    setError(null)
    setLoading(true)
    try {
      await login({ email: values.email, password: values.password })
      // AuthContext sets user → page.tsx will unmount this and render the app
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  async function handleRegister(values: { email: string; password: string; full_name?: string }) {
    setError(null)
    setLoading(true)
    try {
      await register({ email: values.email, password: values.password, full_name: values.full_name })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md shadow-lg" style={{ borderRadius: 16 }}>
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold">Literature Review Assistant</h1>
          <p className="text-sm text-muted-foreground mt-1">Sign in to access your reviews</p>
        </div>

        {error && <Alert type="error" message={error} showIcon className="mb-4" />}

        <Tabs
          defaultActiveKey="login"
          onChange={() => setError(null)}
          items={[
            {
              key: 'login',
              label: 'Sign In',
              children: (
                <Form layout="vertical" onFinish={handleLogin} requiredMark={false}>
                  <Form.Item
                    name="email"
                    label="Email"
                    rules={[{ required: true, type: 'email', message: 'Enter a valid email' }]}
                  >
                    <Input placeholder="you@example.com" size="large" />
                  </Form.Item>
                  <Form.Item
                    name="password"
                    label="Password"
                    rules={[{ required: true, message: 'Enter your password' }]}
                  >
                    <Input.Password placeholder="••••••••" size="large" />
                  </Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    block
                    size="large"
                    className="mt-2"
                  >
                    Sign In
                  </Button>
                </Form>
              ),
            },
            {
              key: 'register',
              label: 'Create Account',
              children: (
                <Form layout="vertical" onFinish={handleRegister} requiredMark={false}>
                  <Form.Item name="full_name" label="Full Name (optional)">
                    <Input placeholder="Jane Smith" size="large" />
                  </Form.Item>
                  <Form.Item
                    name="email"
                    label="Email"
                    rules={[{ required: true, type: 'email', message: 'Enter a valid email' }]}
                  >
                    <Input placeholder="you@example.com" size="large" />
                  </Form.Item>
                  <Form.Item
                    name="password"
                    label="Password"
                    rules={[
                      { required: true, message: 'Enter a password' },
                      { min: 8, message: 'At least 8 characters' },
                    ]}
                  >
                    <Input.Password placeholder="Min. 8 characters" size="large" />
                  </Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    block
                    size="large"
                    className="mt-2"
                  >
                    Create Account
                  </Button>
                </Form>
              ),
            },
          ]}
        />
      </Card>
    </div>
  )
}
