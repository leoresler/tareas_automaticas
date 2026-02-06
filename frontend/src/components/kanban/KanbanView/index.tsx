import { DndContext, DragOverlay, closestCorners, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useState } from 'react'
import type { Task, TaskStatus } from '../../../features/tasks/types'
import { useTaskStore } from '../../../features/tasks/tasksStore'
import TaskCard from '../../tasks/TaskCard'
import EmptyState from '../../shared/EmptyState'

interface SortableTaskProps {
  task: Task
  onTaskClick?: (taskId: number) => void
}

const SortableTask = ({ task, onTaskClick }: SortableTaskProps) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: task.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <TaskCard task={task} onClick={() => onTaskClick?.(task.id)} />
    </div>
  )
}

interface KanbanColumnProps {
  status: TaskStatus
  title: string
  tasks: Task[]
  onTaskClick?: (taskId: number) => void
}

const KanbanColumn = ({ status, title, tasks, onTaskClick }: KanbanColumnProps) => {
  const [activeTask, setActiveTask] = useState<Task | null>(null)
  const { updateTaskStatus } = useTaskStore()

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  )

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event
    const task = tasks.find((t) => t.id === active.id)
    setActiveTask(task || null)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    setActiveTask(null)

    if (!over) return

    const activeTaskId = active.id as number

    const activeTask = tasks.find((t) => t.id === activeTaskId)
    if (!activeTask) return

    if (activeTask.status !== status) {
      updateTaskStatus(activeTaskId, status)
    }
  }

  return (
    <div className="bg-gray-50 rounded-lg p-4 min-h-100">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <span className="text-sm text-gray-500 bg-white px-2 py-0.5 rounded-full">
          {tasks.length}
        </span>
      </div>

      {tasks.length === 0 ? (
        <div className="flex items-center justify-center h-64">
          <EmptyState
            title="Sin tareas"
            description={`No hay tareas ${title.toLowerCase()}`}
          />
        </div>
      ) : (
        <DndContext
          sensors={sensors}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
          collisionDetection={closestCorners}
        >
          <SortableContext items={tasks} strategy={verticalListSortingStrategy}>
            <div className="space-y-3">
              {tasks.map((task) => (
                <SortableTask key={task.id} task={task} onTaskClick={onTaskClick} />
              ))}
            </div>
          </SortableContext>
          <DragOverlay>
            {activeTask && (
              <div className="transform rotate-3">
                <TaskCard task={activeTask} onClick={() => onTaskClick?.(activeTask.id)} />
              </div>
            )}
          </DragOverlay>
        </DndContext>
      )}
    </div>
  )
}

interface KanbanViewProps {
  onTaskClick?: (taskId: number) => void
}

const KanbanView = ({ onTaskClick }: KanbanViewProps) => {
  const { tasks } = useTaskStore()

  const tasksByStatus = {
    pendiente: tasks.filter((t) => t.status === 'pendiente'),
    en_progreso: tasks.filter((t) => t.status === 'en_progreso'),
    finalizado: tasks.filter((t) => t.status === 'finalizado'),
    enviada: tasks.filter((t) => t.status === 'enviada'),
    cancelada: tasks.filter((t) => t.status === 'cancelada'),
  }

  const columns = [
    { status: 'pendiente' as TaskStatus, title: 'Pendiente', tasks: tasksByStatus.pendiente },
    { status: 'en_progreso' as TaskStatus, title: 'En Progreso', tasks: tasksByStatus.en_progreso },
    { status: 'finalizado' as TaskStatus, title: 'Finalizado', tasks: tasksByStatus.finalizado },
    { status: 'enviada' as TaskStatus, title: 'Enviada', tasks: tasksByStatus.enviada },
    { status: 'cancelada' as TaskStatus, title: 'Cancelada', tasks: tasksByStatus.cancelada },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Tablero Kanban</h1>
        <p className="text-gray-600 mt-1">Gestiona tus tareas por estado. Arrastra y suelta para cambiar el estado.</p>
      </div>

      {tasks.length === 0 ? (
        <EmptyState
          title="No hay tareas"
          description="Crea tu primera tarea para comenzar a usar el tablero Kanban."
          actionLabel="Crear Tarea"
          onAction={() => console.log('crear tarea')}
          illustration="tasks"
        />
      ) : (
        <DndContext collisionDetection={closestCorners}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 overflow-x-auto pb-4">
            {columns.map((column) => (
              <KanbanColumn
                key={column.status}
                status={column.status}
                title={column.title}
                tasks={column.tasks}
                onTaskClick={onTaskClick}
              />
            ))}
          </div>
        </DndContext>
      )}
    </div>
  )
}

export default KanbanView
