import { useEffect, useRef } from 'react'
import { useAuthStore } from '../../authStore'

const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const { checkAuth } = useAuthStore()
  const hasInitialized = useRef(false)

  useEffect(() => {
    const initializeAuth = async () => {
      if (hasInitialized.current) return
      hasInitialized.current = true
      
      const storedAuth = localStorage.getItem('auth-storage')
      if (storedAuth) {
        try {
          const parsedAuth = JSON.parse(storedAuth)
          if (parsedAuth.state?.user) {
            await checkAuth()
          }
        } catch {
          localStorage.removeItem('auth-storage')
        }
      }
    }

    initializeAuth()
  }, [checkAuth])

  return <>{children}</>
}

export default AuthProvider