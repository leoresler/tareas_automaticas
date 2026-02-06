import { useState, useEffect } from 'react'
import { Search } from 'lucide-react'
import type { Contact } from '../../../features/contacts/types'

interface ContactSelectorProps {
  selectedContacts: number[]
  onChange: (contactIds: number[]) => void
  className?: string
}

const ContactSelector = ({ selectedContacts, onChange, className }: ContactSelectorProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [availableContacts, setAvailableContacts] = useState<Contact[]>([])
  const [loading, setLoading] = useState(false)

  const toggleContact = (contactId: number) => {
    const isSelected = selectedContacts.includes(contactId)
    const newSelection = isSelected
      ? selectedContacts.filter(id => id !== contactId)
      : [...selectedContacts, contactId]
    onChange(newSelection)
  }

  const removeContact = (contactId: number) => {
    const newSelection = selectedContacts.filter(id => id !== contactId)
    onChange(newSelection)
  }

  useEffect(() => {
    if (isOpen) {
      setLoading(true)
        setTimeout(() => {
          setAvailableContacts([
            {
              id: 1,
              user_id: 1,
              name: 'Juan Pérez',
              channel_type: 'whatsapp',
              channel_value: '+549111234567',
              is_active: true,
              created_at: '2024-01-01T00:00:00',
              updated_at: '2024-01-01T00:00:00',
            },
            {
              id: 2,
              user_id: 1,
              name: 'María García',
              channel_type: 'email',
              channel_value: 'maria@example.com',
              is_active: true,
              created_at: '2024-01-02T00:00:00',
              updated_at: '2024-01-02T00:00:00',
            },
            {
              id: 3,
              user_id: 1,
              name: 'Pedro López',
              channel_type: 'telegram',
              channel_value: '@pedro_lopez',
              is_active: true,
              created_at: '2024-01-03T00:00:00',
              updated_at: '2024-01-03T00:00:00',
            },
          ])
          setLoading(false)
        }, 500)
    }
  }, [isOpen])

  const filteredContacts = availableContacts.filter(contact =>
    contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.channel_value.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const selectedContactsData = availableContacts.filter(contact =>
    selectedContacts.includes(contact.id)
  )

  return (
    <div className={className}>
      {/* Selected Contacts */}
      <div className="mb-3">
        {selectedContactsData.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {selectedContactsData.map(contact => (
              <div
                key={contact.id}
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
              >
                <span>{contact.name}</span>
                <button
                  type="button"
                  onClick={() => removeContact(contact.id)}
                  className="hover:text-blue-900 ml-2"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No hay contactos seleccionados</p>
        )}
      </div>

      {/* Selector Button */}
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-left focus:outline-none focus:ring-blue-500 focus:border-blue-500 hover:bg-gray-50"
      >
        <div className="flex items-center justify-between">
          <span className="text-gray-700">
            {selectedContacts.length > 0 
              ? `${selectedContacts.length} contacto${selectedContacts.length !== 1 ? 's' : ''} seleccionado${selectedContacts.length !== 1 ? 's' : ''}`
              : 'Seleccionar contactos'
            }
          </span>
          <Search className="w-4 h-4 text-gray-400" />
        </div>
      </button>

      {/* Contact Selection Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[80vh] overflow-hidden flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">Seleccionar Contactos</h3>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Search */}
            <div className="p-4 border-b border-gray-200">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar contactos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Contacts List */}
            <div className="flex-1 overflow-y-auto p-4">
              {loading ? (
                <div className="text-center py-8">
                  <p className="text-gray-500">Cargando contactos...</p>
                </div>
              ) : filteredContacts.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-500">No se encontraron contactos</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredContacts.map(contact => {
                    const isSelected = selectedContacts.includes(contact.id)
                    return (
                      <div
                        key={contact.id}
                        onClick={() => toggleContact(contact.id)}
                        className={`
                          p-3 border rounded-lg cursor-pointer transition-colors
                          ${isSelected 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'border-gray-200 hover:bg-gray-50'
                          }
                        `}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium text-gray-900">{contact.name}</p>
                            <p className="text-sm text-gray-500">{contact.channel_value}</p>
                          </div>
                          <div className={`
                            w-5 h-5 rounded-full border-2 flex items-center justify-center text-xs
                            ${isSelected 
                              ? 'border-blue-500 bg-blue-500 text-white' 
                              : 'border-gray-300'
                            }
                          `}>
                            {isSelected && '✓'}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="p-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Guardar ({selectedContacts.length})
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ContactSelector