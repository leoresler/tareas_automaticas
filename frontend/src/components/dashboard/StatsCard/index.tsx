import type { LucideIcon } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: number | string
  icon: LucideIcon
  color: 'gray' | 'blue' | 'green' | 'red' | 'yellow' | 'purple'
  trend?: {
    value: number
    direction: 'up' | 'down' | 'neutral'
  }
  loading?: boolean
}

const StatsCard = ({ 
  title, 
  value, 
  icon: Icon, 
  color, 
  trend,
  loading = false 
}: StatsCardProps) => {
  // Colores de fondo e iconos
  const colorClasses = {
    gray: 'bg-gray-100 text-gray-600',
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    red: 'bg-red-100 text-red-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    purple: 'bg-purple-100 text-purple-600'
  }

  // Colores de tendencia
  const trendColors = {
    up: 'text-green-600',
    down: 'text-red-600', 
    neutral: 'text-gray-600'
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
            <div className="h-8 bg-gray-200 rounded w-16" />
          </div>
          <div className="w-12 h-12 bg-gray-200 rounded-lg" />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          
          {/* Tendencia */}
          {trend && (
            <div className="flex items-center mt-2 space-x-1">
              <svg 
                className={`w-4 h-4 ${trendColors[trend.direction]}`}
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                {trend.direction === 'up' && (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                )}
                {trend.direction === 'down' && (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                )}
                {trend.direction === 'neutral' && (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
                )}
              </svg>
              <span className={`text-sm font-medium ${trendColors[trend.direction]}`}>
                {trend.direction === 'up' && '+'}
                {trend.direction === 'down' && '-'}
                {Math.abs(trend.value)}%
              </span>
            </div>
          )}
        </div>
        
        <div className={`w-12 h-12 ${colorClasses[color]} rounded-lg flex items-center justify-center ml-4`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )
}

export default StatsCard