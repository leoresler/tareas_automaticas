import type { Contact } from '../../../features/contacts/types'
import { Edit, Trash2 } from 'lucide-react'

interface ContactListProps {
  contacts: Contact[]
  onEdit: (contactId: number) => void
  onDelete: (contactId: number) => void
}

const ContactList = ({ contacts, onEdit, onDelete }: ContactListProps) => {
  const getStatusColor = (isActive: boolean) => {
    if (isActive) {
      return 'text-green-600 bg-green-100'
    }
    return 'text-gray-600 bg-gray-100'
  }

  const getChannelIcon = (channelType: string) => {
    switch (channelType) {
      case 'whatsapp':
        return '📱'
      case 'email':
        return '📧'
      case 'telegram':
        return '✈️'
      default:
        return '📞'
    }
  }

  if (contacts.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500">
          <div className="text-4xl mb-4">📱</div>
          <p>No hay contactos registrados</p>
          <p className="text-sm">Crea tu primer contacto para comenzar a enviar mensajes automáticos</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {contacts.map((contact) => (
        <div
          key={contact.id}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow duration-200"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${getStatusColor(contact.is_active)}`}>
                  {getChannelIcon(contact.channel_type)}
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{contact.name}</h3>
                  <p className={`text-sm font-medium ${getStatusColor(contact.is_active)}`}>
                    {contact.is_active ? 'Activo' : 'Inactivo'}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onEdit(contact.id)}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex items-center gap-2"
                title="Editar contacto"
              >
                <Edit className="w-4 h-4" />
                Editar
              </button>
              
              <button
                onClick={() => onDelete(contact.id)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-2"
                title="Eliminar contacto"
              >
                <Trash2 className="w-4 h-4" />
                Eliminar
              </button>
            </div>
          </div>
          
          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Canal</label>
              <p className="text-sm text-gray-900 capitalize">{contact.channel_type}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Valor</label>
              <p className="text-sm text-gray-900">{contact.channel_value}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default ContactList