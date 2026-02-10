'use client'

import { BookOpen } from 'lucide-react'
import { Switch, Typography, Tooltip, Space } from 'antd'
import { MoonOutlined, SunOutlined } from '@ant-design/icons'

const { Text } = Typography

interface HeaderProps {
  themeMode: 'light' | 'dark'
  onThemeChange: (value: 'light' | 'dark') => void
}

export function Header({ themeMode, onThemeChange }: HeaderProps) {
  return (
    <header className="app-header">
      <div className="app-header-inner">
        <div className="flex items-center gap-3">
          <div className="app-logo">
            <BookOpen className="h-5 w-5" />
          </div>
          <div>
            <div className="text-lg font-semibold">Literature Review Assistant</div>
            <Text type="secondary" className="text-sm">
              Multi-agent summaries, minimal workflow
            </Text>
          </div>
        </div>

        <div className="app-header-controls">
          <Space size="middle" wrap>
            <div className="control-group">
              <Text type="secondary" className="text-xs uppercase tracking-wider">
                Theme
              </Text>
              <Tooltip title={themeMode === 'dark' ? 'Switch to light' : 'Switch to dark'}>
                <Switch
                  checked={themeMode === 'dark'}
                  onChange={(checked) => onThemeChange(checked ? 'dark' : 'light')}
                  checkedChildren={<MoonOutlined />}
                  unCheckedChildren={<SunOutlined />}
                />
              </Tooltip>
            </div>
          </Space>
        </div>
      </div>
    </header>
  )
}
