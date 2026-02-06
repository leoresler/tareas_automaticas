import { useTaskStore } from '../../../features/tasks/tasksStore'

const Sidebar = () => {
  const { tasks } = useTaskStore()

  const pendingCount = tasks.filter((t) => t.status === 'pendiente').length
  const inProgressCount = tasks.filter((t) => t.status === 'en_progreso').length
  const completedCount = tasks.filter((t) => t.status === 'finalizado').length

  const navItems = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'Tareas', href: '/tasks', icon: '📋', count: pendingCount },
    { name: 'Calendario', href: '/calendar', icon: '📅' },
    { name: 'Contactos', href: '/contacts', icon: '👥' },
  ]

  return (
    <aside className="hidden lg:block w-64 bg-white border-r border-gray-200 h-[calc(100vh-64px)] sticky top-16 overflow-y-auto">
      <div className="p-4">
        <div className="space-y-6">
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Resumen
            </h3>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="text-2xl font-bold text-blue-600">{pendingCount}</p>
                <p className="text-xs text-blue-700">Pendientes</p>
              </div>
              <div className="bg-green-50 rounded-lg p-3">
                <p className="text-2xl font-bold text-green-600">{completedCount}</p>
                <p className="text-xs text-green-700">Completadas</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Navegación
            </h3>
            <nav className="space-y-1">
              {navItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className={`
                    group flex items-center px-3 py-2 text-sm font-medium rounded-lg
                    transition-colors duration-200
                    ${window.location.pathname === item.href
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <span className="mr-3 text-lg">{item.icon}</span>
                  <span className="flex-1">{item.name}</span>
                  {item.count !== undefined && item.count > 0 && (
                    <span className="inline-flex items-center justify-center px-2 py-0.5 text-xs font-semibold rounded-full bg-blue-100 text-blue-700">
                      {item.count}
                    </span>
                  )}
                </a>
              ))}
            </nav>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Estados
            </h3>
            <nav className="space-y-1">
              <a
                href="/tasks?status=pendiente"
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                <span className="w-2 h-2 rounded-full bg-gray-400 mr-3" />
                Pendientes
              </a>
              <a
                href="/tasks?status=en_progreso"
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                <span className="w-2 h-2 rounded-full bg-blue-400 mr-3" />
                En Progreso
                {inProgressCount > 0 && (
                  <span className="ml-auto text-xs text-gray-500">{inProgressCount}</span>
                )}
              </a>
              <a
                href="/tasks?status=finalizado"
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                <span className="w-2 h-2 rounded-full bg-green-400 mr-3" />
                Finalizados
              </a>
            </nav>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
