import { useState } from 'react'
import { DayPicker } from 'react-day-picker'
import { format, parse } from 'date-fns'
import { es } from 'date-fns/locale'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import 'react-day-picker/style.css'

interface DatePickerProps {
  value?: string
  onChange: (value: string) => void
  error?: string
  label?: string
  required?: boolean
}

const DatePicker = ({ value, onChange, error, label, required }: DatePickerProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedDate, setSelectedDate] = useState<Date | null>(
    value ? parse(value, "yyyy-MM-dd'T'HH:mm", new Date()) : new Date()
  )

  const handleDateSelect = (date: Date | undefined) => {
    if (date) {
      const [hours, minutes] = value ? 
        [parseInt(value.split('T')[1].split(':')[0]), parseInt(value.split('T')[1].split(':')[1])] : 
        [12, 0]
      
      date.setHours(hours)
      date.setMinutes(minutes)
      
      const formatted = format(date, "yyyy-MM-dd'T'HH:mm")
      onChange(formatted)
    }
    setIsOpen(false)
  }

  const handleTimeChange = (type: 'hour' | 'minute', value: string) => {
    const numValue = parseInt(value) || 0
    const newDate = selectedDate ? new Date(selectedDate) : new Date()
    
    if (type === 'hour') {
      newDate.setHours(Math.min(23, Math.max(0, numValue)))
    } else {
      newDate.setMinutes(Math.min(59, Math.max(0, numValue)))
    }
    
    setSelectedDate(newDate)
    const formatted = format(newDate, "yyyy-MM-dd'T'HH:mm")
    onChange(formatted)
  }

  const hours = selectedDate ? selectedDate.getHours() : 0
  const minutes = selectedDate ? selectedDate.getMinutes() : 0

  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        <div className="flex space-x-2">
          {/* Date Picker */}
          <button
            type="button"
            onClick={() => setIsOpen(true)}
            className={`
              flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm
              focus:outline-none focus:ring-blue-500 focus:border-blue-500
              text-left
              ${error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : ''}
            `}
          >
            {selectedDate ? format(selectedDate, 'd MMMM yyyy', { locale: es }) : 'Seleccionar fecha'}
          </button>

          {/* Time Inputs */}
          <input
            type="number"
            min="0"
            max="23"
            value={hours}
            onChange={(e) => handleTimeChange('hour', e.target.value)}
            className="w-20 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-center"
            placeholder="HH"
          />
          <span className="flex items-center text-gray-500">:</span>
          <input
            type="number"
            min="0"
            max="59"
            value={minutes.toString().padStart(2, '0')}
            onChange={(e) => handleTimeChange('minute', e.target.value)}
            className="w-20 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-center"
            placeholder="MM"
          />
        </div>

        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}

        {/* Calendar Modal */}
        {isOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-4">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Seleccionar fecha</h3>
              </div>
              
              <div className="flex justify-between items-center mb-4">
                <button
                  onClick={() => {
                    const newDate = new Date(selectedDate || new Date())
                    newDate.setMonth(newDate.getMonth() - 1)
                    setSelectedDate(newDate)
                  }}
                  className="p-2 hover:bg-gray-100 rounded"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                
                <span className="font-medium">
                  {selectedDate ? format(selectedDate, 'MMMM yyyy', { locale: es }) : ''}
                </span>
                
                <button
                  onClick={() => {
                    const newDate = new Date(selectedDate || new Date())
                    newDate.setMonth(newDate.getMonth() + 1)
                    setSelectedDate(newDate)
                  }}
                  className="p-2 hover:bg-gray-100 rounded"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              <DayPicker
                mode="single"
                selected={selectedDate || undefined}
                onSelect={handleDateSelect}
                locale={es}
                fromDate={new Date()}
                className="mx-auto"
              />

              <div className="mt-4 flex justify-end space-x-2">
                <button
                  onClick={() => setIsOpen(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={() => handleDateSelect(selectedDate || new Date())}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Seleccionar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DatePicker