import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}

export function formatAuthors(authors: string[]): string {
  if (authors.length === 0) return 'Unknown'
  if (authors.length === 1) return authors[0]
  if (authors.length === 2) return authors.join(' and ')
  if (authors.length <= 3) return authors.slice(0, -1).join(', ') + ', and ' + authors[authors.length - 1]
  return authors.slice(0, 3).join(', ') + ' et al.'
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}
