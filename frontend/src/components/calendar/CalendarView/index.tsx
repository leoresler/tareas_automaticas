import { useState } from 'react'
import { format, addMonths, subMonths, isSameDay } from 'date-fns'
import { es } from 'date-fns/locale'
import { DayPicker } from 'react-day-picker'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useTaskStore } from '../../../features/tasks/tasksStore'
import TaskCard from '../../tasks/TaskCard'
import EmptyState from '../../shared/EmptyState'

interface CalendarViewProps {
  onTaskClick?: (taskId: number) => void
}

const CalendarView = ({ onTaskClick }: CalendarViewProps) => {
  const { tasks } = useTaskStore()
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [selectedDay, setSelectedDay] = useState<Date | null>(null)

  const getTasksForDay = (day: Date) => {
    return tasks.filter((task) => {
      const taskDate = new Date(task.scheduled_datetime)
      return isSameDay(taskDate, day)
    })
  }

  const handleDayClick = (day: Date) => {
    setSelectedDay(day)
  }

  const hasTaskOnDay = (day: Date) => {
    return tasks.some((task) => {
      const taskDate = new Date(task.scheduled_datetime)
      return isSameDay(taskDate, day)
    })
  }

  const selectedDayTasks = selectedDay ? getTasksForDay(selectedDay) : []
  const todayTasks = getTasksForDay(new Date())

  const modifiers = {
    hasTask: (day: Date) => hasTaskOnDay(day),
  }

  const modifiersStyles = {
    hasTask: {
      backgroundColor: '#dbeafe',
      fontWeight: 'bold' as const,
    },
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Calendario</h1>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Mes anterior"
          >
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </button>
          <span className="text-lg font-semibold text-gray-900 min-w-50 text-center">
            {format(currentMonth, 'MMMM yyyy', { locale: es })}
          </span>
          <button
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Siguiente mes"
          >
            <ChevronRight className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="relative">
              <DayPicker
                mode="single"
                required
                selected={selectedDay ?? undefined}
                onSelect={handleDayClick}
                month={currentMonth}
                onMonthChange={setCurrentMonth}
                locale={es}
                modifiers={modifiers}
                modifiersStyles={modifiersStyles}
                className="w-full"
                classNames={{
                  caption: 'flex justify-center pt-1 relative items-center',
                  caption_label: 'text-sm font-medium',
                  nav: 'flex items-center',
                  nav_button: 'inline-flex items-center justify-center rounded-md text-gray-500 hover:text-gray-900 h-7 w-7',
                  table: 'w-full border-collapse space-y-1',
                  head_row: 'flex',
                  head_cell: 'text-gray-900 rounded-md w-9 font-normal text-[0.8rem]',
                  row: 'flex w-full mt-2',
                  cell: 'relative p-0 text-center text-sm focus-within:relative focus-within:z-20',
                  day: 'h-9 w-9 p-0 font-normal text-gray-700 hover:bg-gray-100 rounded-full transition-colors',
                  day_today: 'bg-blue-100 text-blue-700 font-bold',
                  day_selected: 'bg-blue-600 text-white hover:bg-blue-600 focus:bg-blue-600',
                  day_outside: 'text-gray-400',
                }}
              />
            </div>
          </div>

          {selectedDay && (
            <div className="mt-4 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                {format(selectedDay, "d 'de' MMMM", { locale: es })}
              </h3>
              {selectedDayTasks.length === 0 ? (
                <EmptyState
                  title="No hay tareas este día"
                  description="Este día está libre de tareas."
                  illustration="calendar"
                />
              ) : (
                <div className="space-y-2">
                  {selectedDayTasks.map((task) => (
                    <TaskCard key={task.id} task={task} compact onClick={() => onTaskClick?.(task.id)} />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Tareas de {format(new Date(), "d 'de' MMMM", { locale: es })}
            </h3>
            {todayTasks.length === 0 ? (
              <EmptyState
                title="No hay tareas hoy"
                description="¡Genial! Tienes el día libre o puedes crear nuevas tareas."
                illustration="tasks"
              />
            ) : (
              <div className="space-y-3">
                {todayTasks.map((task) => (
                  <TaskCard key={task.id} task={task} onClick={() => onTaskClick?.(task.id)} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CalendarView
