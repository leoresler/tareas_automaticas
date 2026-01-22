# Tareas Automáticas

Proyecto full-stack con Python + FastAPI, React, MySQL y Tailwind CSS.

## 🚀 Stack

- **Backend:** FastAPI, Python, SQLAlchemy
- **Frontend:** React, Vite, Tailwind CSS
- **Database:** MySQL (XAMPP)

## 📋 Prerequisitos

- Python 3.11+
- Node.js 20+
- MySQL (XAMPP)

## 🛠️ Instalacion

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

## ▶️ Correr el proyecto

### Iniciar Backend
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Iniciar Frontend
```bash
cd frontend
npm run dev
```

## 🌐 Acesso

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs