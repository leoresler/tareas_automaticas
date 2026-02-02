# Frontend - Sistema de Autenticación

## Tecnologías

- React 19 + TypeScript
- Vite
- Tailwind CSS v4
- React Router DOM v7
- Axios (HTTP client)
- Zustand (state management)
- React Hook Form + Zod (formularios y validaciones)
- React Hot Toast (notificaciones)
- Cookies HTTP-Only (autenticación)

## Estructura del Proyecto

```
frontend/src/
├── features/
│   └── auth/
│       ├── types.ts          # Interfaces TypeScript
│       ├── api.ts            # Axios + endpoints
│       └── authStore.ts      # Zustand store
├── components/
│   └── auth/
│       ├── LoginForm/        # Componente de login
│       └── RegisterForm/     # Componente de registro
├── pages/
│   ├── LoginPage/            # Página de login
│   ├── RegisterPage/         # Página de registro
│   └── DashboardPage/        # Página protegida (dashboard)
├── router/
│   ├── ProtectedRoute/       # Componente de ruta protegida
│   └── AppRouter.tsx         # Configuración de rutas
├── App.tsx                   # Componente principal
└── main.tsx                  # Punto de entrada
```

## Configuración

1. Crear archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

2. Editar `.env` con la URL del backend:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Instalación

```bash
npm install
```

## Scripts

```bash
npm run dev      # Servidor de desarrollo (http://localhost:5173)
npm run build    # Build para producción
npm run lint     # Ejecutar ESLint
npm run preview  # Previsualizar build de producción
```

## Rutas

- `/` → Redirige a `/dashboard` o `/login`
- `/login` → Página de inicio de sesión
- `/register` → Página de registro
- `/dashboard` → Página protegida (requiere autenticación)

## Autenticación

El sistema utiliza **cookies HTTP-Only** para almacenar el JWT token, lo cual es más seguro que localStorage:

1. **Login**: Backend envía cookie http-only con el token
2. **Peticiones**: Axios envía automáticamente la cookie con cada petición
3. **Logout**: Backend elimina la cookie

## API Endpoints

### Auth

- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/logout` - Cerrar sesión
- `GET /api/v1/auth/me` - Obtener usuario actual (requiere auth)

## Notas

- El interceptor de Axios maneja automáticamente los errores 401 redirigiendo al login
- El estado de autenticación se persiste en localStorage usando Zustand persist
- Los formularios usan React Hook Form con validación Zod
- Las notificaciones se muestran con React Hot Toast
