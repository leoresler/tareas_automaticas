import { useEffect } from 'react'
import { 
  useDashboardStore, 
  useDashboardStats, 
  useDashboardLoading, 
  useDashboardError,
  useTasksByStatus,
  useTasksByMonth,
  useRecentTasks,
  useTodayTasks
} from '../../features/dashboard/dashboardStore'
import EmptyState from '../../components/shared/EmptyState'
import StatsCard from '../../components/dashboard/StatsCard'
import StatusChart from '../../components/dashboard/StatusChart'
import TrendChart from '../../components/dashboard/TrendChart'
import { 
  Clock, 
  TrendingUp, 
  CheckCircle, 
  Calendar,
  AlertTriangle,
  BarChart3
} from 'lucide-react'

const DashboardPage = () => {
  const { fetchAllDashboardData, resetDashboard } = useDashboardStore()
  const stats = useDashboardStats()
  const loading = useDashboardLoading()
  const error = useDashboardError()
  const tasksByStatus = useTasksByStatus()
  const tasksByMonth = useTasksByMonth()
  const recentTasks = useRecentTasks()
  const todayTasks = useTodayTasks()

  useEffect(() => {
    fetchAllDashboardData()
  }, [fetchAllDashboardData])

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-4" />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="h-32 bg-gray-200 rounded-lg" />
              <div className="h-32 bg-gray-200 rounded-lg" />
              <div className="h-32 bg-gray-200 rounded-lg" />
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-red-800 font-medium">Error al cargar el dashboard</h3>
                <p className="text-red-600 text-sm mt-1">{error}</p>
              </div>
              <button
                onClick={() => {
                  resetDashboard()
                  fetchAllDashboardData()
                }}
                className="bg-red-100 text-red-800 px-4 py-2 rounded-md hover:bg-red-200 transition-colors"
              >
                Reintentar
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Bienvenido a tu panel de gestión de tareas</p>
      </div>

      {/* Tarjetas de Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Tareas"
          value={stats?.total_tasks || 0}
          icon={BarChart3}
          color="gray"
        />
        
        <StatsCard
          title="Pendientes"
          value={stats?.pending_count || 0}
          icon={Clock}
          color="blue"
          trend={stats?.overdue_count && stats?.overdue_count > 0 ? {
            value: 15,
            direction: 'up'
          } : undefined}
        />
        
        <StatsCard
          title="En Progreso"
          value={stats?.in_progress_count || 0}
          icon={TrendingUp}
          color="yellow"
        />
        
        <StatsCard
          title="Completadas"
          value={stats?.completed_count || 0}
          icon={CheckCircle}
          color="green"
          trend={stats?.completion_rate ? {
            value: stats.completion_rate,
            direction: stats.completion_rate > 50 ? 'up' : 'neutral'
          } : undefined}
        />
      </div>

      {/* Estadísticas Adicionales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatsCard
          title="Tareas de Hoy"
          value={stats?.today_tasks || 0}
          icon={Calendar}
          color="blue"
        />
        
        <StatsCard
          title="Vencidas"
          value={stats?.overdue_count || 0}
          icon={AlertTriangle}
          color="red"
        />
        
        <StatsCard
          title="Completadas esta Semana"
          value={stats?.week_completed || 0}
          icon={CheckCircle}
          color="green"
        />
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <StatusChart data={tasksByStatus} loading={loading} />
        <TrendChart data={tasksByMonth} loading={loading} />
      </div>

      {/* Listas de Tareas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tareas de Hoy */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Tareas de Hoy</h2>
            {todayTasks.length > 0 && (
              <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                {todayTasks.length}
              </span>
            )}
          </div>
          
          {todayTasks.length === 0 ? (
            <EmptyState
              title="No hay tareas para hoy"
              description="¡Genial! Tienes el día libre o puedes crear nuevas tareas."
              illustration="calendar"
            />
          ) : (
            <div className="space-y-3">
              {todayTasks.slice(0, 5).map((task) => (
                <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{task.title}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <p className="text-sm text-gray-500">
                        {task.scheduled_datetime && new Date(task.scheduled_datetime).toLocaleTimeString('es-ES', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                      {task.is_overdue && (
                        <span className="bg-red-100 text-red-800 text-xs font-medium px-2 py-0.5 rounded">
                          Vencida
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => window.location.href = `/tasks/${task.id}`}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors"
                  >
                    Ver
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Tareas Recientes */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Tareas Recientes</h2>
            {recentTasks.length > 0 && (
              <span className="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded">
                {recentTasks.length}
              </span>
            )}
          </div>
          
          {recentTasks.length === 0 ? (
            <EmptyState
              title="No hay tareas aún"
              description="Crea tu primera tarea para comenzar a organizarte."
              actionLabel="Crear Tarea"
              onAction={() => (window.location.href = '/tasks/new')}
              illustration="tasks"
            />
          ) : (
            <div className="space-y-3">
              {recentTasks.slice(0, 5).map((task) => (
                <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{task.title}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <p className="text-sm text-gray-500">
                        {task.created_at && new Date(task.created_at).toLocaleDateString('es-ES', {
                          day: 'numeric',
                          month: 'short',
                        })}
                      </p>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded ${
                        task.status === 'finalizado' 
                          ? 'bg-green-100 text-green-800'
                          : task.status === 'en_progreso'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {task.status === 'finalizado' ? 'Finalizada' : 
                         task.status === 'en_progreso' ? 'En Progreso' : 'Pendiente'}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => window.location.href = `/tasks/${task.id}`}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors"
                  >
                    Ver
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
