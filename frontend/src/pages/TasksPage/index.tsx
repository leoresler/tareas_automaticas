import { useState } from 'react'
import CalendarView from '../../components/calendar/CalendarView'
import KanbanView from '../../components/kanban/KanbanView'
import TaskModal from '../../components/tasks/TaskModal'

type ViewType = 'calendar' | 'kanban'

const TasksPage = () => {
  const [currentView, setCurrentView] = useState<ViewType>('calendar')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingTaskId, setEditingTaskId] = useState<number | undefined>()

  const handleCreateTask = () => {
    setEditingTaskId(undefined)
    setIsModalOpen(true)
  }

  const handleEditTask = (taskId: number) => {
    setEditingTaskId(taskId)
    setIsModalOpen(true)
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingTaskId(undefined)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tareas</h1>
          <p className="text-gray-600 mt-1">Gestiona todas tus tareas</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setCurrentView('calendar')}
              className={`
                px-4 py-2 text-sm font-medium rounded-md transition-all duration-200
                ${currentView === 'calendar'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
                }
              `}
            >
              📅 Calendario
            </button>
            <button
              onClick={() => setCurrentView('kanban')}
              className={`
                px-4 py-2 text-sm font-medium rounded-md transition-all duration-200
                ${currentView === 'kanban'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
                }
              `}
            >
              📋 Tablero
            </button>
          </div>

          <button
            onClick={handleCreateTask}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
          >
            + Nueva Tarea
          </button>
        </div>
      </div>

      {currentView === 'calendar' && <CalendarView onTaskClick={handleEditTask} />}
      {currentView === 'kanban' && <KanbanView onTaskClick={handleEditTask} />}

      <TaskModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        taskId={editingTaskId}
      />
    </div>
  )
}

export default TasksPage