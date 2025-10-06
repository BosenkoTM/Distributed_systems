from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import docker
import redis
import json
import logging
from datetime import datetime
import os
import time
import uuid
import asyncio
from contextlib import asynccontextmanager

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# База данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/sql_verification_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))

# Docker
docker_client = docker.from_env()

# Модели базы данных
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    sql_query = Column(Text)
    expected_result = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    result = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer)
    verifier_name = Column(String(100))
    is_correct = Column(Boolean)
    confidence = Column(Float)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic модели
class TaskCreate(BaseModel):
    title: str
    description: str
    sql_query: str
    expected_result: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    sql_query: str
    expected_result: Optional[str]
    status: str
    result: Optional[str]
    execution_time: Optional[float]
    created_at: str

class VerificationCreate(BaseModel):
    task_id: int
    verifier_name: str
    is_correct: bool
    confidence: float
    comments: Optional[str] = None

class SQLExecutionRequest(BaseModel):
    sql_query: str
    timeout: int = 30

class SQLExecutionResponse(BaseModel):
    success: bool
    result: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    execution_time: float
    query_id: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    logger.info("SQL Verification Backend started")
    yield
    # Shutdown
    logger.info("SQL Verification Backend shutting down")

app = FastAPI(
    title="SQL Verification System",
    description="Упрощенная система верификации SQL-запросов с песочницей",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Зависимости
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQL Sandbox функции
def is_sql_safe(sql_query: str) -> bool:
    """Проверка безопасности SQL-запроса"""
    dangerous_operations = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE",
        "GRANT", "REVOKE", "EXEC", "EXECUTE", "SP_", "xp_", "cmdshell"
    ]
    
    sql_upper = sql_query.upper()
    
    for operation in dangerous_operations:
        if operation in sql_upper:
            return False
    
    injection_patterns = [
        "UNION SELECT", "OR 1=1", "OR '1'='1'", "'; DROP", "1; DROP",
        "EXEC(", "EXECUTE(", "SP_", "xp_", "cmdshell"
    ]
    
    for pattern in injection_patterns:
        if pattern in sql_upper:
            return False
    
    return True

async def execute_sql_in_sandbox(sql_query: str, timeout: int = 30) -> Dict[str, Any]:
    """Выполнение SQL-запроса в Docker песочнице"""
    start_time = time.time()
    query_id = f"query_{int(time.time())}_{hash(sql_query) % 10000}"
    
    try:
        # Проверка безопасности
        if not is_sql_safe(sql_query):
            raise Exception("Unsafe SQL query detected")
        
        # Создание временного контейнера
        container = docker_client.containers.run(
            image="postgres:15",
            detach=True,
            environment={
                "POSTGRES_DB": "sandbox",
                "POSTGRES_USER": "sandbox",
                "POSTGRES_PASSWORD": "sandbox"
            },
            mem_limit="512m",
            cpu_period=100000,
            cpu_quota=50000,  # 50% CPU
            remove=True,
            name=f"sql_sandbox_{int(time.time())}"
        )
        
        # Ожидание запуска PostgreSQL
        await asyncio.sleep(5)
        
        try:
            # Выполнение SQL-запроса
            exec_result = container.exec_run(
                cmd=[
                    "psql", "-U", "sandbox", "-d", "sandbox", 
                    "-c", sql_query, "-t", "-A", "-F", ","
                ],
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            if exec_result.exit_code != 0:
                error_msg = exec_result.output.decode()
                await log_execution(query_id, sql_query, None, False, error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "execution_time": execution_time,
                    "query_id": query_id
                }
            
            # Парсинг результата
            result = parse_sql_result(exec_result.output.decode())
            
            # Логирование
            await log_execution(query_id, sql_query, result, True)
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "query_id": query_id
            }
            
        finally:
            # Очистка контейнера
            try:
                container.remove(force=True)
            except:
                pass
                
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        await log_execution(query_id, sql_query, None, False, error_msg)
        
        return {
            "success": False,
            "error": error_msg,
            "execution_time": execution_time,
            "query_id": query_id
        }

def parse_sql_result(output: str) -> List[Dict[str, Any]]:
    """Парсинг результата SQL-запроса"""
    if not output.strip():
        return []
    
    lines = output.strip().split('\n')
    if not lines:
        return []
    
    result = []
    for line in lines:
        if line.strip():
            values = line.split(',')
            row = {}
            for i, value in enumerate(values):
                row[f"column_{i+1}"] = value.strip()
            result.append(row)
    
    return result

async def log_execution(query_id: str, sql_query: str, result: Optional[List[Dict[str, Any]]], success: bool, error: Optional[str] = None):
    """Логирование выполнения SQL-запроса"""
    try:
        log_entry = {
            "query_id": query_id,
            "sql_query": sql_query,
            "success": success,
            "error": error,
            "result_count": len(result) if result else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Сохранение в Redis
        redis_client.lpush("execution_logs", json.dumps(log_entry))
        redis_client.ltrim("execution_logs", 0, 9999)
        
        # Логирование в файл
        logger.info(f"SQL Execution: {query_id} - {'SUCCESS' if success else 'FAILED'}")
        
    except Exception as e:
        logger.error(f"Failed to log execution: {e}")

# API Endpoints

@app.get("/")
async def root():
    return {"message": "SQL Verification System", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    try:
        # Проверка Docker
        docker_client.ping()
        docker_status = "healthy"
    except:
        docker_status = "unhealthy"
    
    try:
        # Проверка Redis
        redis_client.ping()
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"
    
    return {
        "status": "healthy",
        "services": {
            "docker": docker_status,
            "redis": redis_status
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# SQL Execution
@app.post("/sql/execute", response_model=SQLExecutionResponse)
async def execute_sql(request: SQLExecutionRequest):
    """Выполнение SQL-запроса в песочнице"""
    result = await execute_sql_in_sandbox(request.sql_query, request.timeout)
    return SQLExecutionResponse(**result)

@app.get("/sql/validate/{query_id}")
async def validate_sql(query_id: str):
    """Валидация SQL-запроса"""
    try:
        # Поиск в логах
        logs = redis_client.lrange("execution_logs", 0, -1)
        for log_json in logs:
            log_entry = json.loads(log_json)
            if log_entry["query_id"] == query_id:
                return {
                    "query_id": query_id,
                    "valid": log_entry["success"],
                    "error": log_entry.get("error"),
                    "timestamp": log_entry["timestamp"]
                }
        
        raise HTTPException(status_code=404, detail="Query not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Tasks
@app.post("/tasks/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Создание новой задачи"""
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return TaskResponse(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        sql_query=db_task.sql_query,
        expected_result=db_task.expected_result,
        status=db_task.status,
        result=db_task.result,
        execution_time=db_task.execution_time,
        created_at=db_task.created_at.isoformat()
    )

@app.get("/tasks/", response_model=List[TaskResponse])
async def get_tasks(db: Session = Depends(get_db)):
    """Получение списка задач"""
    tasks = db.query(Task).all()
    return [
        TaskResponse(
            id=t.id,
            title=t.title,
            description=t.description,
            sql_query=t.sql_query,
            expected_result=t.expected_result,
            status=t.status,
            result=t.result,
            execution_time=t.execution_time,
            created_at=t.created_at.isoformat()
        )
        for t in tasks
    ]

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Получение задачи по ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        sql_query=task.sql_query,
        expected_result=task.expected_result,
        status=task.status,
        result=task.result,
        execution_time=task.execution_time,
        created_at=task.created_at.isoformat()
    )

@app.post("/tasks/{task_id}/execute")
async def execute_task(task_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Выполнение задачи"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Обновление статуса
    task.status = "running"
    db.commit()
    
    # Выполнение в фоне
    background_tasks.add_task(execute_task_background, task_id, task.sql_query, db)
    
    return {"message": f"Task {task_id} execution started"}

async def execute_task_background(task_id: int, sql_query: str, db: Session):
    """Фоновое выполнение задачи"""
    try:
        result = await execute_sql_in_sandbox(sql_query)
        
        # Обновление задачи
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "completed" if result["success"] else "failed"
            task.result = json.dumps(result.get("result", []))
            task.execution_time = result["execution_time"]
            task.completed_at = datetime.utcnow()
            db.commit()
            
    except Exception as e:
        logger.error(f"Failed to execute task {task_id}: {e}")
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.result = json.dumps({"error": str(e)})
            task.completed_at = datetime.utcnow()
            db.commit()

# Verifications
@app.post("/verifications/", response_model=Dict[str, Any])
async def create_verification(verification: VerificationCreate, db: Session = Depends(get_db)):
    """Создание верификации"""
    db_verification = Verification(**verification.dict())
    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)
    
    return {
        "id": db_verification.id,
        "task_id": db_verification.task_id,
        "verifier_name": db_verification.verifier_name,
        "is_correct": db_verification.is_correct,
        "confidence": db_verification.confidence,
        "created_at": db_verification.created_at.isoformat()
    }

@app.get("/verifications/task/{task_id}", response_model=List[Dict[str, Any]])
async def get_task_verifications(task_id: int, db: Session = Depends(get_db)):
    """Получение верификаций для задачи"""
    verifications = db.query(Verification).filter(Verification.task_id == task_id).all()
    return [
        {
            "id": v.id,
            "verifier_name": v.verifier_name,
            "is_correct": v.is_correct,
            "confidence": v.confidence,
            "comments": v.comments,
            "created_at": v.created_at.isoformat()
        }
        for v in verifications
    ]

# Monitoring
@app.get("/monitoring/stats")
async def get_monitoring_stats():
    """Получение статистики системы"""
    try:
        # Статистика из базы данных
        db = SessionLocal()
        try:
            total_tasks = db.query(Task).count()
            completed_tasks = db.query(Task).filter(Task.status == "completed").count()
            failed_tasks = db.query(Task).filter(Task.status == "failed").count()
            total_verifications = db.query(Verification).count()
        finally:
            db.close()
        
        # Статистика из Redis
        try:
            total_logs = len(redis_client.lrange("execution_logs", 0, -1))
        except:
            total_logs = 0
        
        return {
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
            },
            "verifications": {
                "total": total_verifications
            },
            "logs": {
                "total": total_logs
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get monitoring stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/logs")
async def get_execution_logs(limit: int = 100):
    """Получение логов выполнения"""
    try:
        logs = redis_client.lrange("execution_logs", 0, limit - 1)
        return [json.loads(log) for log in logs]
    except Exception as e:
        logger.error(f"Failed to get execution logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Инициализация базы данных
@app.post("/init")
async def init_database():
    """Инициализация базы данных с тестовыми данными"""
    db = SessionLocal()
    
    try:
        # Создание тестовых задач
        test_tasks = [
            {
                "title": "Простой SELECT запрос",
                "description": "Выбрать все записи из таблицы users",
                "sql_query": "SELECT * FROM users LIMIT 10;",
                "expected_result": "Список пользователей"
            },
            {
                "title": "Запрос с WHERE",
                "description": "Выбрать активных пользователей",
                "sql_query": "SELECT name, email FROM users WHERE active = true;",
                "expected_result": "Активные пользователи"
            },
            {
                "title": "Агрегатный запрос",
                "description": "Подсчитать количество пользователей",
                "sql_query": "SELECT COUNT(*) as user_count FROM users;",
                "expected_result": "Общее количество пользователей"
            }
        ]
        
        for task_data in test_tasks:
            if not db.query(Task).filter(Task.title == task_data["title"]).first():
                task = Task(**task_data)
                db.add(task)
        
        db.commit()
        return {"message": "Database initialized successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
