/**
 * API client configuration
 */

import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

export { API_URL }
