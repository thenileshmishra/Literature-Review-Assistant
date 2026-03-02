'use client'

import { createCache, extractStyle, StyleProvider } from '@ant-design/cssinjs'
import { useServerInsertedHTML } from 'next/navigation'
import { type ReactNode, useState } from 'react'

type AntdStyleRegistryProps = {
  children: ReactNode
}

export function AntdStyleRegistry({ children }: AntdStyleRegistryProps) {
  const [cache] = useState(() => createCache())

  useServerInsertedHTML(() => {
    const styleText = extractStyle(cache, true)

    if (!styleText) {
      return null
    }

    return (
      <style
        id="antd"
        dangerouslySetInnerHTML={{ __html: styleText }}
      />
    )
  })

  return <StyleProvider cache={cache}>{children}</StyleProvider>
}
