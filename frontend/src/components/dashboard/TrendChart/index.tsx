import type { TaskMonthData } from '../../../features/dashboard/dashboardApi'

interface TrendChartProps {
  data: TaskMonthData[]
  loading?: boolean
}

const TrendChart = ({ data, loading = false }: TrendChartProps) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Tendencia Mensual</h2>
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
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Tendencia Mensual</h2>
        <div className="text-center py-8">
          <p className="text-gray-500">No hay datos para mostrar</p>
        </div>
      </div>
    )
  }

  // Encontrar el valor máximo para escalar el gráfico
  const maxCount = Math.max(...data.map(item => item.count))
  const chartHeight = 200
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Tendencia Mensual</h2>
      
      {/* Gráfico de barras verticales */}
      <div className="relative">
        {/* Línea base */}
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gray-300"></div>
        
        {/* Barras */}
        <div 
          className="flex items-end justify-between space-x-2"
          style={{ height: `${chartHeight}px` }}
        >
          {data.map((item, index) => {
            const height = maxCount > 0 ? (item.count / maxCount) * (chartHeight - 20) : 0
            const displayHeight = Math.max(height, 4) // Altura mínima para visibilidad
            
            return (
              <div 
                key={`${item.month}-${index}`}
                className="flex-1 flex flex-col items-center justify-end"
              >
                {/* Tooltip en hover */}
                <div className="relative group">
                  {/* Barra */}
                  <div
                    className="w-full bg-blue-500 rounded-t-sm transition-all duration-300 hover:bg-blue-600 cursor-pointer"
                    style={{
                      height: `${displayHeight}px`,
                      minHeight: '4px'
                    }}
                  />
                  
                  {/* Tooltip */}
                  <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap pointer-events-none">
                    <div>{item.month}</div>
                    <div className="font-bold">{item.count} tareas</div>
                    {/* Flecha del tooltip */}
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                      <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                    </div>
                  </div>
                </div>
                
                {/* Etiqueta del mes */}
                <div className="mt-2 text-xs text-gray-600 text-center">
                  {item.month.split(' ')[1]}
                </div>
              </div>
            )
          })}
        </div>
      </div>
      
      {/* Estadísticas */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {data.reduce((sum, item) => sum + item.count, 0)}
            </div>
            <div className="text-xs text-gray-500">Total Tareas</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(data.reduce((sum, item) => sum + item.count, 0) / data.length)}
            </div>
            <div className="text-xs text-gray-500">Promedio Mensual</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {Math.max(...data.map(item => item.count))}
            </div>
            <div className="text-xs text-gray-500">Máximo Mensual</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TrendChart