import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import toast from 'react-hot-toast'
import type { Contact } from '../../../features/contacts/types'
import { useContactStore } from '../../../features/contacts/contactsStore'
import { z } from 'zod'

const contactFormSchema = z.object({
  name: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  channel_type: z.enum(['whatsapp', 'email', 'telegram']),
  channel_value: z.string().min(1, 'El valor del canal es requerido'),
  is_active: z.boolean().default(true),
})

type ContactFormData = z.infer<typeof contactFormSchema>

interface ContactFormProps {
  initialData?: Contact
  onSuccess?: () => void
  onCancel?: () => void
}

const ContactForm = ({ initialData, onSuccess, onCancel }: ContactFormProps) => {
  const { createContact, updateContact, loading } = useContactStore()
  const isEditing = !!initialData

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactFormSchema),
    defaultValues: {
      name: initialData?.name || '',
      channel_type: initialData?.channel_type || 'whatsapp',
      channel_value: initialData?.channel_value || '',
      is_active: initialData?.is_active ?? true,
    },
  })

  const onSubmit = async (data: ContactFormData) => {
    try {
      if (isEditing && initialData) {
        await updateContact(initialData.id, data)
        toast.success('Contacto actualizado exitosamente')
      } else {
        await createContact(data)
        toast.success('Contacto creado exitosamente')
      }
      
      reset()
      onSuccess?.()
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al guardar contacto'
      toast.error(errorMessage)
    }
  }

  const channelOptions = [
    { value: 'whatsapp', label: 'WhatsApp' },
    { value: 'email', label: 'Email' },
    { value: 'telegram', label: 'Telegram' },
  ]

  const getChannelPlaceholder = (channelType: string) => {
    switch (channelType) {
      case 'whatsapp':
        return 'Ej: +34 6000 1234'
      case 'email':
        return 'Ej: usuario@ejemplo.com'
      case 'telegram':
        return 'Ej: @usuario_telegram'
      default:
        return 'Ingrese el valor del canal'
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {isEditing ? 'Editar Contacto' : 'Crear Nuevo Contacto'}
          </h2>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Nombre del Contacto *
            </label>
            <input
              id="name"
              type="text"
              {...register('name', { required: 'El nombre es requerido' })}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                focus:outline-none focus:ring-blue-500 focus:border-blue-500
                ${errors.name ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : ''}
              `}
              placeholder="Ej: Juan Pérez"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="channel_type" className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Canal *
            </label>
          <select
            id="channel_type"
            {...register('channel_type')}
            className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${errors.channel_type ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : ''}`}
          >
            {channelOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
            {errors.channel_type && (
              <p className="mt-1 text-sm text-red-600">{errors.channel_type.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="channel_value" className="block text-sm font-medium text-gray-700 mb-2">
              Valor del Canal *
            </label>
            <input
              id="channel_value"
              type="text"
              {...register('channel_value', { required: 'El valor del canal es requerido' })}
              className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${errors.channel_value ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : ''}`}
              placeholder={getChannelPlaceholder(initialData?.channel_type || 'whatsapp')}
            />
            {errors.channel_value && (
              <p className="mt-1 text-sm text-red-600">{errors.channel_value.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="is_active" className="flex items-center space-x-2">
              <input
                id="is_active"
                type="checkbox"
                {...register('is_active')}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">Activo</span>
            </label>
              {errors.is_active && (
                <p className="mt-1 text-sm text-red-600">{errors.is_active.message}</p>
              )}
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

export default ContactForm