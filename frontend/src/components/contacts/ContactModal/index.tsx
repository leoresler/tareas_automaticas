import ContactForm from '../ContactForm'
import type { Contact } from '../../../features/contacts/types'
import { useContacts } from '../../../features/contacts/contactsStore'

interface ContactModalProps {
  isOpen: boolean
  onClose: () => void
  contactId?: number
}

const ContactModal = ({ isOpen, onClose, contactId }: ContactModalProps) => {
  const contacts = useContacts()
  
  if (!isOpen) {
    return null
  }

  const handleSuccess = () => {
    onClose()
  }

  const handleCancel = () => {
    onClose()
  }

  const getInitialContact = (): Contact | undefined => {
    if (!contactId) return undefined
    return contacts.find(c => c.id === contactId)
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 py-8">
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
        
        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              {contactId ? 'Editar Contacto' : 'Crear Nuevo Contacto'}
            </h3>
            
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 transition-colors"
              title="Cerrar"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="px-6 py-4">
            <ContactForm
              initialData={getInitialContact()}
              onSuccess={handleSuccess}
              onCancel={handleCancel}
            />
          </div>

          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-4 h-4 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-xs font-bold">ℹ️</span>
                </div>
                <p className="font-medium">Información de Canales</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="font-medium text-gray-900 mb-1">📱 WhatsApp</div>
                  <p className="text-xs text-gray-600">Formato: +34 6000 1234</p>
                </div>
                
                <div className="text-center">
                  <div className="font-medium text-gray-900 mb-1">📧 Email</div>
                  <p className="text-xs text-gray-600">Formato: usuario@dominio.com</p>
                </div>
                
                <div className="text-center">
                  <div className="font-medium text-gray-900 mb-1">✈️ Telegram</div>
                  <p className="text-xs text-gray-600">Formato: @username</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ContactModal