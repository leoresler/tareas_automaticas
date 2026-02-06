import type { TaskStatusData } from '../../../features/dashboard/dashboardApi'

interface StatusChartProps {
  data: TaskStatusData[]
  loading?: boolean
}

const StatusChart = ({ data, loading = false }: StatusChartProps) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Distribución de Tareas</h2>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-1/3" />
          <div className="h-32 bg-gray-200 rounded" />
        </div>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Distribución de Tareas</h2>
        <div className="text-center py-8">
          <p className="text-gray-500">No hay datos para mostrar</p>
        </div>
      </div>
    )
  }

  // Calcular total y porcentajes
  const total = data.reduce((sum, item) => sum + item.count, 0)
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Distribución de Tareas</h2>
      
      {/* Gráfico de barras horizontal */}
      <div className="space-y-4">
        {data.map((item) => {
          const percentage = total > 0 ? (item.count / total) * 100 : 0
          
          return (
            <div key={item.status} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">{item.status}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">{item.count} tareas</span>
                  <span className="text-sm font-medium text-gray-900">{percentage.toFixed(1)}%</span>
                </div>
              </div>
              
              {/* Barra de progreso */}
              <div className="w-full bg-gray-200 rounded-full h-8 overflow-hidden">
                <div
                  className="h-full rounded-full flex items-center justify-center text-white text-xs font-medium transition-all duration-300 ease-out"
                  style={{
                    width: `${Math.max(percentage, 2)}%`,
                    backgroundColor: item.color,
                    minWidth: '40px'
                  }}
                >
                  {percentage >= 5 && `${percentage.toFixed(0)}%`}
                </div>
              </div>
            </div>
          )
        })}
      </div>
      
      {/* Resumen */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Total de Tareas</span>
          <span className="text-lg font-bold text-gray-900">{total}</span>
        </div>
      </div>
    </div>
  )
}

export default StatusChart