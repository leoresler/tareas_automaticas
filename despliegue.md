# Guía de Despliegue en Vercel

## 📋 Resumen del Proyecto

Este es un proyecto Full-Stack con:
- **Backend**: FastAPI (Python) con MySQL
- **Frontend**: React + TypeScript + Vite
- **Base de Datos**: MySQL (requiere servicio externo gratuito)
- **Autenticación**: JWT tokens
- **Rate Limiting**: Configurado con slowapi
- **Deployment**: Vercel (frontend) + servicio MySQL externo

## 🚀 Requisitos Previos

### Cuentas Necesarias
- [Vercel](https://vercel.com/) - Cuenta gratuita
- [GitHub](https://github.com/) - Cuenta gratuita
- Servicio MySQL gratuito (ver opciones abajo)

### Herramientas Locales
- Git
- Node.js 18+ (para frontend)
- Python 3.11+ (para backend)
- Vercel CLI (`npm install -g vercel`)

## 🌐 Opciones de Base de Datos MySQL Gratuita

### Opción 1: Supabase (Recomendado)
- **Plan Gratis**: 2GB de almacenamiento, 500K filas, 500K API calls/mes
- **URL**: https://supabase.com/
- **Ventajas**: MySQL-compatible, fácil integración, serverless
- **Limitaciones**: No es MySQL puro (PostgreSQL), pero compatible

### Opción 2: PlanetScale
- **Plan Gratis**: 5GB de almacenamiento, conexiones ilimitadas
- **URL**: https://planetscale.com/
- **Ventajas**: MySQL serverless, branching, backups automáticos
- **Limitaciones**: 1 proyecto, 5GB storage

### Opción 3: Heroku (Postgres como alternativa)
- **Plan Gratis**: 10k rows, 20 conexiones simultáneas
- **URL**: https://www.heroku.com/
- **Ventajas**: PostgreSQL (compatible con SQLAlchemy)
- **Limitaciones**: Podcasting después de 30 mins de inactividad

### Opción 4: Railway
- **Plan Gratis**: $5/mes (créditos gratuitos)
- **URL**: https://railway.app/
- **Ventajas**: MySQL real, fácil deploy
- **Limitaciones**: Pago requerido para uso continuado

**Recomendación**: Supabase o PlanetScale para mejor experiencia gratuita.

## 🔧 Configuración del Backend

### 1. Variables de Entorno Necesarias
```bash
# Base de Datos
DATABASE_URL=servicio_mysql_connection_string

# Autenticación
SECRET_KEY=tu_secret_key_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Tareas Automaticas API
VERSION=1.0.0

# CORS
BACKEND_CORS_ORIGINS=["https://tu-dominio.vercel.app"]

# Admin inicial
FIRST_SUPERUSER_EMAIL=admin@ejemplo.com
FIRST_SUPERUSER_PASSWORD=tu_contraseña_segura
```

### 2. Configuración para Vercel

#### Archivo `vercel.json` (en backend)
```json
{
  "version": 2,
  "buildCommand": "pip install -r requirements.txt",
  "outputDirectory": ".",
  "framework": null,
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/app/api/routers/$1"
    }
  ]
}
```

#### Dockerfile (opcional pero recomendado)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🎨 Configuración del Frontend

### 1. Variables de Entorno
```bash
# Variables Públicas (accesibles desde el navegador)
VITE_API_URL=https://tu-backend.vercel.app/api/v1
VITE_APP_NAME=Tareas Automaticas

# Variables Privadas (solo servidor)
# No se usan en este proyecto frontend
```

### 2. Configuración Vercel

#### Archivo `vercel.json` (en frontend)
```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "VITE_API_URL": "@backend-url"
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "no-cache"
        }
      ]
    }
  ]
}
```

## 🚀 Pasos de Despliegue

### Paso 1: Preparar el Backend

#### 1.1 Crear repositorio GitHub para backend
```bash
cd backend
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/tu-usuario/backend-repo.git
git push -u origin main
```

#### 1.2 Configurar variables en Vercel
1. Ir a [Vercel Dashboard](https://vercel.com/dashboard)
2. Crear nuevo proyecto > Importar repositorio GitHub
3. Seleccionar el repositorio backend
4. Ir a Settings > Environment Variables
5. Agregar todas las variables necesarias

#### 1.3 Desplegar backend
```bash
# Usando Vercel CLI
vc link # vincular al proyecto
vc --prod # deploy a producción
```

### Paso 2: Preparar el Frontend

#### 2.1 Crear repositorio GitHub para frontend
```bash
cd frontend
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/tu-usuario/frontend-repo.git
git push -u origin main
```

#### 2.2 Configurar variables en Vercel
1. Importar repositorio frontend a Vercel
2. Configurar `VITE_API_URL` con la URL del backend desplegado
3. Verificar que `vercel.json` esté configurado correctamente

#### 2.3 Desplegar frontend
```bash
vc link
vc --prod
```

### Paso 3: Configurar Base de Datos

#### 3.1 Crear base de datos en servicio elegido
- **Supabase**: Crear proyecto > Database > SQL Editor
- **PlanetScale**: Crear branch > Connect > Connection string

#### 3.2 Configurar conexión en backend
1. Obtener connection string
2. Agregar a variables de entorno de Vercel
3. Ejecutar migraciones (si aplica)

#### 3.3 Migrar base de datos
```bash
# Conectar a la base de datos
# Ejecutar migraciones de Alembic
alembic upgrade head
```

## 🔧 Configuración Avanzada

### 1. Dominio Personalizado
```bash
# Configurar dominio en Vercel
vc domains add tu-dominio.com
```

### 2. HTTPS Automático
Vercel proporciona HTTPS automático con Let's Encrypt.

### 3. Serverless Functions
El backend se desplegará como serverless functions automáticamente.

### 4. Environment Variables por Ambiente
```json
{
  "env": {
    "NODE_ENV": "production"
  },
  "build": {
    "env": {
      "VITE_API_URL": "@backend-url"
    }
  }
}
```

## 📊 Monitoreo y Logs

### 1. Logs de Vercel
```bash
vc logs # ver logs recientes
vc inspect # inspeccionar despliegue
```

### 2. Monitoreo de Base de Datos
- **Supabase**: Dashboard integrado
- **PlanetScale**: Metrics y alerts

### 3. Health Checks
El proyecto ya incluye endpoints:
- `/health` - Verificar API
- `/test-db` - Verificar conexión a base de datos

## 🚨 Troubleshooting Común

### Problema: Error de conexión a base de datos
**Solución**:
1. Verificar que la connection string sea correcta
2. Asegurar que la base de datos permita conexiones externas
3. Revisar firewall/security groups

### Problema: CORS errors
**Solución**:
1. Verificar `BACKEND_CORS_ORIGINS` en variables de entorno
2. Asegurar que incluya el dominio de Vercel
3. Reiniciar el despliegue

### Problema: Environment variables no cargadas
**Solución**:
1. Verificar que las variables estén configuradas en Settings
2. Asegurar que el despliegue se haya reiniciado
3. Usar `vercel env pull` para verificar localmente

### Problema: Memory limits
**Solución**:
1. Optimizar queries de base de datos
2. Considerar actualizar plan si es necesario
3. Usar caching donde sea apropiado

## 📁 Estructura de Archivos para Deploy

```
backend/
├── vercel.json              # Configuración Vercel
├── Dockerfile              # Opcional (recomendado)
├── requirements.txt         # Dependencias Python
└── .env.example           # Ejemplo variables

frontend/
├── vercel.json              # Configuración Vercel
├── package.json            # Dependencias Node
└── .env.example           # Ejemplo variables
```

## 🚀 Comandos Útiles

### Backend
```bash
# Deploy con Vercel CLI
vc --prod

# Ver logs
vc logs

# Inspeccionar despliegue
vc inspect
```

### Frontend
```bash
# Build local
npm run build

# Deploy
vc --prod

# Ver preview
vc --preview
```

## 📋 Checklist Final

- [ ] Cuentas creadas (Vercel, GitHub, servicio MySQL)
- [ ] Backend configurado y deployado
- [ ] Frontend configurado y deployado
- [ ] Base de datos creada y conectada
- [ ] Variables de entorno configuradas
- [ ] Migraciones ejecutadas
- [ ] Pruebas funcionales realizadas
- [ ] Dominio personalizado configurado (opcional)
- [ ] HTTPS activado
- [ ] Monitoreo configurado

## 📞 Soporte y Recursos

### Documentación Oficial
- [Vercel Docs](https://vercel.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Supabase Docs](https://supabase.com/docs)
- [PlanetScale Docs](https://planetscale.com/docs)

### Comunidad
- [Vercel Discord](https://discord.com/invite/vercel)
- [FastAPI GitHub](https://github.com/tiangolo/fastapi)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/vercel)

---

**Fecha de Creación**: 2025-02-06  
**Versión**: 1.0  
**Autor**: Guía de despliegue generada automáticamente