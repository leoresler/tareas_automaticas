import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../features/auth/authStore'

interface PublicRouteProps {
  children: React.ReactNode
}

const PublicRoute = ({ children }: PublicRouteProps) => {
  const { user, isAuthenticated } = useAuthStore()
  const location = useLocation()

  if (isAuthenticated && user) {
    return <Navigate to="/dashboard" state={{ from: location }} replace />
  }

  return <>{children}</>
}

export default PublicRoute
