import { useEffect, useRef } from 'react'
import Header from '../dashboard/Header'
import Sidebar from '../dashboard/Sidebar'
import { useTaskStore } from '../../features/tasks/tasksStore'
import { useAuthStore } from '../../features/auth/authStore'

interface DashboardLayoutProps {
  children: React.ReactNode
}

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const { fetchTasks } = useTaskStore()
  const { isAuthenticated, user } = useAuthStore()
  const isInitialized = useRef(false)

  useEffect(() => {
    if (isAuthenticated && user && !isInitialized.current) {
      isInitialized.current = true
      fetchTasks().catch(() => {
        localStorage.removeItem('auth-storage')
        window.location.href = '/login'
      })
    }
  }, [isAuthenticated, user, fetchTasks])

  if (!isAuthenticated || !user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 lg:ml-16 max-w-7xl min-h-[calc(100vh-64px)]">
          <div className="p-4 sm:p-6 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout
