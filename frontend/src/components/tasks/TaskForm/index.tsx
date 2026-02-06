import { useForm } from 'react-hook-form'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import DatePicker from '../../shared/DatePicker'
import ContactSelector from '../../shared/ContactSelector'
import type { TaskCreateInput } from '../../../features/tasks/tasksSchemas'
import { useTaskStore } from '../../../features/tasks/tasksStore'

interface TaskFormProps {
  initialData?: TaskCreateInput
  onSuccess?: () => void
  onCancel?: () => void
}

const TaskForm = ({ initialData, onSuccess, onCancel }: TaskFormProps) => {
  const { createTask, updateTask, loading, currentTask } = useTaskStore()
  const isEditing = !!initialData || !!currentTask

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    reset,
  } = useForm<TaskCreateInput>({
    defaultValues: initialData || {
      title: '',
      description: '',
      scheduled_datetime: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
      tags: [],
      contact_ids: [],
    },
  })

  const onSubmit = async (data: TaskCreateInput) => {
    try {
      if (!data.contact_ids || data.contact_ids.length === 0) {
        toast.error('Debe seleccionar al menos un contacto')
        return
      }

      const formattedData = {
        ...data,
        tags: typeof data.tags === 'string' ? data.tags.split(',').map(t => t.trim()).filter(t => t) : data.tags,
      }

      if (isEditing && currentTask) {
        await updateTask(currentTask.id, formattedData)
        toast.success('Tarea actualizada exitosamente')
      } else {
        await createTask(formattedData)
        toast.success('Tarea creada exitosamente')
      }
      reset()
      onSuccess?.()
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al guardar la tarea'
      toast.error(errorMessage)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {isEditing ? 'Editar Tarea' : 'Crear Nueva Tarea'}
          </h2>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          <div className="space-y-3">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Título *
              </label>
              <input
                id="title"
                type="text"
                {...register('title', { required: 'El título es requerido' })}
                className={`
                  w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                  focus:outline-none focus:ring-blue-500 focus:border-blue-500
                  ${errors.title ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : ''}
                `}
                placeholder="Ej: Reunión con cliente"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Descripción
              </label>
              <textarea
                id="description"
                rows={4}
                {...register('description')}
                className={`
                  w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                  focus:outline-none focus:ring-blue-500 focus:border-blue-500
                  ${errors.description ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : ''}
                `}
                placeholder="Describe los detalles de la tarea..."
              />
              {errors.description && (
                <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="scheduled_datetime" className="block text-sm font-medium text-gray-700 mb-2">
              Fecha y Hora *
            </label>
            <DatePicker
              value={watch('scheduled_datetime')}
              onChange={(value) => setValue('scheduled_datetime', value)}
              error={errors.scheduled_datetime?.message}
            />
            {errors.scheduled_datetime && (
              <p className="mt-1 text-sm text-red-600">{errors.scheduled_datetime.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-2">
              Etiquetas
            </label>
            <input
              id="tags"
              type="text"
              {...register('tags')}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                focus:outline-none focus:ring-blue-500 focus:border-blue-500
                ${errors.tags ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : ''}
              `}
              placeholder="Ej: importante, trabajo, familia (separado por comas)"
            />
            {errors.tags && (
              <p className="mt-1 text-sm text-red-600">{errors.tags.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="contact_ids" className="block text-sm font-medium text-gray-700 mb-2">
              Contactos Asociados *
            </label>
            <ContactSelector
              selectedContacts={watch('contact_ids') || []}
              onChange={(ids) => setValue('contact_ids', ids)}
            />
            {(watch('contact_ids')?.length ?? 0) === 0 && (
              <p className="mt-1 text-sm text-red-600">Debe seleccionar al menos un contacto</p>
            )}
          </div>

          <div>
            <label htmlFor="contact_ids" className="block text-sm font-medium text-gray-700 mb-2">
              Contactos Asociados
            </label>
            <ContactSelector
              selectedContacts={watch('contact_ids') || []}
              onChange={(ids) => setValue('contact_ids', ids)}
            />
          </div>

          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 border border-transparent rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default TaskForm