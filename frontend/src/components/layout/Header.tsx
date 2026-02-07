import { BookOpen } from 'lucide-react'

export function Header() {
  return (
    <div className="text-center space-y-4">
      <div className="flex items-center justify-center gap-3">
        <BookOpen className="h-12 w-12 text-blue-400" />
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          Literature Review Assistant
        </h1>
      </div>
      <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
        AI-powered multi-agent system for conducting comprehensive literature reviews
      </p>
    </div>
  )
}
