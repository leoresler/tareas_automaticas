import { useAuthStore } from '../../features/auth/authStore'
import toast from 'react-hot-toast'

const DashboardPage = () => {
  const { user, logout } = useAuthStore()

  const handleLogout = async () => {
    try {
      await logout()
      toast.success('Sesión cerrada correctamente')
    } catch {
      toast.error('Error al cerrar sesión')
    }
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              Mi dashboard - {user.username}
            </h1>
            <button
              onClick={handleLogout}
              className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Cerrar Sesión
            </button>
          </div>
          <div className="mt-4 text-gray-600">
            <p>Bienvenido, {user.full_name || user.username}!</p>
            <p className="mt-2">Email: {user.email}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
