from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
import json
import pika
from datetime import datetime
import asyncio

from database import get_db, engine
from models import Base, Task, TaskStatus
from auth import verify_token
from parser import process_file_to_jsonl

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Service", version="1.0.0")
security = HTTPBearer()

# RabbitMQ connection
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:5672")

def get_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    return connection

# Pydantic models
class TaskCreate(BaseModel):
    target_level: str = "Автоматически"
    augment: bool = False
    aug_factor: int = 1

class TaskResponse(BaseModel):
    id: str
    filename: str
    status: str
    target_level: str
    augment: bool
    aug_factor: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    initial_count: Optional[int] = None
    total_count: Optional[int] = None
    error_message: Optional[str] = None

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For simplicity, we'll use username as user_id
    # In a real app, you'd query the user service
    return {"username": username, "user_id": 1}

# Background task for processing files
async def process_file_task(task_id: str, file_path: str, target_level: str, augment: bool, aug_factor: int, db: Session):
    try:
        # Update task status to processing
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.PROCESSING
            db.commit()
        
        # Send processing started event
        send_task_event("task_processing_started", task_id, {"status": "processing"})
        
        # Process the file
        output_path = f"/app/results/{task_id}.jsonl"
        initial_count, total_count = process_file_to_jsonl(
            file_path, output_path, target_level, augment, aug_factor
        )
        
        # Update task with results
        if task:
            task.status = TaskStatus.COMPLETED
            task.initial_count = initial_count
            task.total_count = total_count
            task.updated_at = datetime.utcnow()
            db.commit()
        
        # Send completion event
        send_task_event("task_completed", task_id, {
            "status": "completed",
            "initial_count": initial_count,
            "total_count": total_count
        })
        
    except Exception as e:
        # Update task with error
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.updated_at = datetime.utcnow()
            db.commit()
        
        # Send error event
        send_task_event("task_failed", task_id, {
            "status": "failed",
            "error": str(e)
        })

def send_task_event(event_type: str, task_id: str, data: dict):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.queue_declare(queue='task_events', durable=True)
        
        message = {
            'event_type': event_type,
            'task_id': task_id,
            'timestamp': datetime.utcnow().isoformat(),
            **data
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='task_events',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to send task event: {e}")

# Routes
@app.post("/upload", response_model=TaskResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_level: str = "Автоматически",
    augment: bool = False,
    aug_factor: int = 1,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.csv')):
        raise HTTPException(status_code=400, detail="Only .xlsx and .csv files are allowed")
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Save uploaded file
    upload_dir = "/app/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{task_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create task record
    task = Task(
        id=task_id,
        filename=file.filename,
        file_path=file_path,
        status=TaskStatus.PENDING,
        target_level=target_level,
        augment=augment,
        aug_factor=aug_factor,
        user_id=current_user["user_id"]
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Start background processing
    background_tasks.add_task(
        process_file_task,
        task_id,
        file_path,
        target_level,
        augment,
        aug_factor,
        db
    )
    
    # Send task created event
    send_task_event("task_created", task_id, {
        "filename": file.filename,
        "status": "pending",
        "user_id": current_user["user_id"]
    })
    
    return TaskResponse(
        id=task.id,
        filename=task.filename,
        status=task.status.value,
        target_level=task.target_level,
        augment=task.augment,
        aug_factor=task.aug_factor,
        created_at=task.created_at,
        updated_at=task.updated_at,
        user_id=task.user_id
    )

@app.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tasks = db.query(Task).filter(Task.user_id == current_user["user_id"]).offset(skip).limit(limit).all()
    total = db.query(Task).filter(Task.user_id == current_user["user_id"]).count()
    
    return TaskListResponse(
        tasks=[
            TaskResponse(
                id=task.id,
                filename=task.filename,
                status=task.status.value,
                target_level=task.target_level,
                augment=task.augment,
                aug_factor=task.aug_factor,
                created_at=task.created_at,
                updated_at=task.updated_at,
                user_id=task.user_id,
                initial_count=task.initial_count,
                total_count=task.total_count,
                error_message=task.error_message
            ) for task in tasks
        ],
        total=total
    )

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user["user_id"]).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        id=task.id,
        filename=task.filename,
        status=task.status.value,
        target_level=task.target_level,
        augment=task.augment,
        aug_factor=task.aug_factor,
        created_at=task.created_at,
        updated_at=task.updated_at,
        user_id=task.user_id,
        initial_count=task.initial_count,
        total_count=task.total_count,
        error_message=task.error_message
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "task-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
