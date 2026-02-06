import type { Task } from '../../../features/tasks/types'

interface TaskCardProps {
  task: Task
  onClick?: () => void
  compact?: boolean
}

const TaskCard = ({ task, onClick, compact = false }: TaskCardProps) => {
  const taskDate = new Date(task.scheduled_datetime)
  const isOverdue = taskDate < new Date() && task.status === 'pendiente'

  const statusColors = {
    pendiente: 'border-l-gray-400',
    en_progreso: 'border-l-blue-400',
    finalizado: 'border-l-green-400',
    enviada: 'border-l-purple-400',
    cancelada: 'border-l-red-400',
  }

  if (compact) {
    return (
      <div
        onClick={onClick}
        className={`
          p-2 bg-white rounded border border-gray-200 border-l-4 shadow-sm
          hover:shadow-md transition-all duration-200 cursor-pointer
          ${statusColors[task.status]}
          ${isOverdue ? 'bg-red-50' : ''}
        `}
      >
        <div className="flex items-center justify-between gap-2">
          <h4 className="text-sm font-medium text-gray-900 truncate flex-1">
            {task.title}
          </h4>
          <span className="text-xs text-gray-500 whitespace-nowrap">
            {taskDate.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>
    )
  }

  return (
    <div
      onClick={onClick}
      className={`
        p-4 bg-white rounded-lg border border-gray-200 border-l-4 shadow-sm
        hover:shadow-md transition-all duration-200 cursor-pointer
        ${statusColors[task.status]}
        ${isOverdue ? 'bg-red-50' : ''}
      `}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <h4 className="text-base font-semibold text-gray-900 line-clamp-2 flex-1">
          {task.title}
        </h4>
        <span className="text-xs text-gray-500 whitespace-nowrap">
          {taskDate.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>

      {task.description && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {task.description}
        </p>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {task.tags_list?.slice(0, 2).map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-700"
            >
              {tag}
            </span>
          ))}
          {task.tags_list && task.tags_list.length > 2 && (
            <span className="text-xs text-gray-500">
              +{task.tags_list.length - 2}
            </span>
          )}
        </div>

        {task.contacts && task.contacts.length > 0 && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span>{task.contacts.length}</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default TaskCard
