import { useEffect, useState } from 'react'
import { useContactStore } from '../../features/contacts/contactsStore'
import ContactList from '../../components/contacts/ContactList'
import ContactModal from '../../components/contacts/ContactModal'
import EmptyState from '../../components/shared/EmptyState'

const ContactsPage = () => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingContact, setEditingContact] = useState<number | undefined>()
  const { 
    contacts, 
    loading, 
    error, 
    fetchContacts, 
    deleteContact 
  } = useContactStore()

  useEffect(() => {
    fetchContacts()
  }, [fetchContacts])

  const handleCreateContact = () => {
    setEditingContact(undefined)
    setIsModalOpen(true)
  }

  const handleEditContact = (contactId: number) => {
    setEditingContact(contactId)
    setIsModalOpen(true)
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingContact(undefined)
  }

  const handleDeleteContact = async (contactId: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este contacto?')) {
      await deleteContact(contactId)
    }
  }

  if (loading && contacts.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-4" />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="h-32 bg-gray-200 rounded-lg" />
              <div className="h-32 bg-gray-200 rounded-lg" />
              <div className="h-32 bg-gray-200 rounded-lg" />
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="text-lg font-medium text-red-800">Error al cargar contactos</h3>
            <p className="mt-2 text-red-600">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 bg-red-100 text-red-800 px-4 py-2 rounded-md hover:bg-red-200 transition-colors"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Contactos</h1>
              <p className="mt-1 text-gray-600">
                Gestiona tu lista de contactos para enviar mensajes automáticos
              </p>
            </div>
            
            <button
              onClick={handleCreateContact}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 6v6m0 6h6m-6 0h6" />
              </svg>
              Nuevo Contacto
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {contacts.length === 0 ? (
          <EmptyState
            title="No hay contactos"
            description="Crea tu primer contacto para comenzar a enviar mensajes automáticos."
            actionLabel="Crear Contacto"
            onAction={handleCreateContact}
            illustration="contacts"
          />
        ) : (
          <ContactList
            contacts={contacts}
            onEdit={handleEditContact}
            onDelete={handleDeleteContact}
          />
        )}
      </div>

      {/* Contact Modal */}
      <ContactModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        contactId={editingContact}
      />
    </div>
  )
}

export default ContactsPage