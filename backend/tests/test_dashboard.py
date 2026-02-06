# Tests para endpoints del dashboard

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base, User, Task
from app.core.security import create_access_token, get_password_hash

# Crear base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user(test_db):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_superuser=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}

class TestDashboard:
    """Clase de tests para el dashboard"""
    
    def test_health_endpoint(self, client):
        """Test que el health endpoint funciona"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_dashboard_stats_requires_auth(self, client, test_db):
        """Test que el dashboard stats requiere autenticación"""
        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_dashboard_stats_with_auth(self, client, test_db, test_user, auth_headers):
        """Test que el dashboard stats funciona con auth"""
        # Crear algunas tareas de prueba
        task1 = Task(
            title="Tarea 1",
            description="Descripción 1",
            status="pendiente",
            user_id=test_user.id,
            priority="media"
        )
        task2 = Task(
            title="Tarea 2", 
            description="Descripción 2",
            status="en_progreso",
            user_id=test_user.id,
            priority="alta"
        )
        task3 = Task(
            title="Tarea 3",
            description="Descripción 3",
            status="finalizado",
            user_id=test_user.id,
            priority="baja"
        )
        
        test_db.add_all([task1, task2, task3])
        test_db.commit()
        
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        stats = data["data"]
        assert stats["total_tasks"] == 3
        assert stats["pending_count"] == 1
        assert stats["in_progress_count"] == 1
        assert stats["completed_count"] == 1
        assert "completion_rate" in stats

    def test_tasks_by_status_endpoint(self, client, test_db, test_user, auth_headers):
        """Test endpoint de tareas por estado"""
        # Crear tareas con diferentes estados
        tasks = [
            Task(title="Pendiente 1", status="pendiente", user_id=test_user.id),
            Task(title="Pendiente 2", status="pendiente", user_id=test_user.id),
            Task(title="En Progreso 1", status="en_progreso", user_id=test_user.id),
            Task(title="Finalizado 1", status="finalizado", user_id=test_user.id),
        ]
        
        test_db.add_all(tasks)
        test_db.commit()
        
        response = client.get("/api/v1/dashboard/tasks-by-status", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        status_data = data["data"]
        assert len(status_data) == 3  # pendiente, en_progreso, finalizado
        
        # Verificar que cada estado tiene los datos correctos
        for item in status_data:
            assert "status" in item
            assert "count" in item
            assert "color" in item

    def test_recent_tasks_endpoint(self, client, test_db, test_user, auth_headers):
        """Test endpoint de tareas recientes"""
        tasks = [
            Task(title="Reciente 1", status="pendiente", user_id=test_user.id),
            Task(title="Reciente 2", status="en_progreso", user_id=test_user.id),
        ]
        
        test_db.add_all(tasks)
        test_db.commit()
        
        response = client.get("/api/v1/dashboard/recent-tasks", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        recent_tasks = data["data"]
        assert len(recent_tasks) == 2

    def test_today_tasks_endpoint(self, client, test_db, test_user, auth_headers):
        """Test endpoint de tareas de hoy"""
        from datetime import datetime, timedelta
        
        # Crear tarea para hoy
        today_task = Task(
            title="Tarea de Hoy",
            status="pendiente",
            user_id=test_user.id,
            scheduled_datetime=datetime.now()
        )
        
        # Crear tarea para ayer
        yesterday_task = Task(
            title="Tarea de Ayer",
            status="pendiente", 
            user_id=test_user.id,
            scheduled_datetime=datetime.now() - timedelta(days=1)
        )
        
        test_db.add_all([today_task, yesterday_task])
        test_db.commit()
        
        response = client.get("/api/v1/dashboard/today-tasks", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        today_tasks = data["data"]
        assert len(today_tasks) == 1  # Solo la tarea de hoy
        assert today_tasks[0]["title"] == "Tarea de Hoy"