import type { TaskStatus } from '../../../features/tasks/types'

interface StatusBadgeProps {
  status: TaskStatus
  size?: 'sm' | 'md' | 'lg'
}

const statusConfig: Record<TaskStatus, {
  label: string
  bgColor: string
  textColor: string
  dotColor: string
}> = {
  pendiente: {
    label: 'Pendiente',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-700',
    dotColor: 'bg-gray-400',
  },
  en_progreso: {
    label: 'En Progreso',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-700',
    dotColor: 'bg-blue-400',
  },
  finalizado: {
    label: 'Finalizado',
    bgColor: 'bg-green-100',
    textColor: 'text-green-700',
    dotColor: 'bg-green-400',
  },
  enviada: {
    label: 'Enviada',
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-700',
    dotColor: 'bg-purple-400',
  },
  cancelada: {
    label: 'Cancelada',
    bgColor: 'bg-red-100',
    textColor: 'text-red-700',
    dotColor: 'bg-red-400',
  },
}

const StatusBadge = ({ status, size = 'md' }: StatusBadgeProps) => {
  const config = statusConfig[status]

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  }

  const dotSize = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-2.5 h-2.5',
  }

  return (
    <span
      className={`
        ${config.bgColor} ${config.textColor}
        ${sizeClasses[size]}
        inline-flex items-center gap-1.5 rounded-full font-medium
        transition-colors duration-200
      `}
    >
      <span className={`rounded-full ${config.dotColor} ${dotSize[size]}`} />
      {config.label}
    </span>
  )
}

export default StatusBadge
