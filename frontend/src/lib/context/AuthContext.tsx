'use client'

import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { clearToken, getMe, getToken, login, logout as doLogout, register } from '@/lib/api/auth'
import type { LoginRequest, RegisterRequest, UserResponse } from '@/lib/types/api'

interface AuthContextValue {
  user: UserResponse | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // On mount, rehydrate user from stored token
  useEffect(() => {
    async function rehydrate() {
      const token = getToken()
      if (!token) { setIsLoading(false); return }
      try {
        const me = await getMe()
        setUser(me)
      } catch {
        clearToken()
      } finally {
        setIsLoading(false)
      }
    }
    rehydrate()
  }, [])

  const handleLogin = useCallback(async (data: LoginRequest) => {
    await login(data)          // sets token in localStorage
    const me = await getMe()
    setUser(me)
  }, [])

  const handleRegister = useCallback(async (data: RegisterRequest) => {
    await register(data)       // sets token in localStorage
    const me = await getMe()
    setUser(me)
  }, [])

  const handleLogout = useCallback(() => {
    doLogout()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
