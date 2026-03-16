/**
 * Auth API functions
 */

import { apiClient } from './client'
import type { LoginRequest, RegisterRequest, TokenResponse, UserResponse } from '../types/api'

const TOKEN_KEY = 'litrev-access-token'

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export async function register(data: RegisterRequest): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>('/api/v1/auth/register', data)
  setToken(res.data.access_token)
  return res.data
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>('/api/v1/auth/login', data)
  setToken(res.data.access_token)
  return res.data
}

export async function getMe(): Promise<UserResponse> {
  const res = await apiClient.get<UserResponse>('/api/v1/auth/me')
  return res.data
}

export function logout(): void {
  clearToken()
}
