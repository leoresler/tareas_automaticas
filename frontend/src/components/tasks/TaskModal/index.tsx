import { useEffect } from 'react'
import { useTaskStore } from '../../../features/tasks/tasksStore'
import TaskForm from '../TaskForm'
import type { Task } from '../../../features/tasks/types'

interface TaskModalProps {
  isOpen: boolean
  onClose: () => void
  taskId?: number
}

const TaskModal = ({ isOpen, onClose, taskId }: TaskModalProps) => {
  const { currentTask, fetchTaskById, setCurrentTask } = useTaskStore()

  const handleSuccess = () => {
    onClose()
    setCurrentTask(null)
  }

  const handleCancel = () => {
    onClose()
    if (!taskId) {
      setCurrentTask(null)
    }
  }

  useEffect(() => {
    if (taskId && isOpen) {
      fetchTaskById(taskId)
    }
  }, [taskId, isOpen, fetchTaskById])

  useEffect(() => {
    if (!isOpen) {
      setCurrentTask(null)
    }
  }, [isOpen, setCurrentTask])

  if (!isOpen) return null

  const getContactIds = (task: Task | null): number[] => {
    if (!task?.contacts || !Array.isArray(task.contacts)) return []
    return task.contacts.map((contact: { id: number }) => contact.id)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div
        className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <TaskForm
          initialData={currentTask ? {
            title: currentTask.title,
            description: currentTask.description || '',
            scheduled_datetime: currentTask.scheduled_datetime,
            tags: currentTask.tags_list || [],
            contact_ids: getContactIds(currentTask),
          } : undefined}
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      </div>
    </div>
  )
}

export default TaskModal
