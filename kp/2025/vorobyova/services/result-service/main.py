from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os
import json
import pika
from datetime import datetime

from database import get_db, engine
from models import Base, Result
from auth import verify_token

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Result Service", version="1.0.0")
security = HTTPBearer()

# RabbitMQ connection
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:5672")

def get_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    return connection

# Pydantic models
class ResultResponse(BaseModel):
    id: str
    task_id: str
    filename: str
    status: str
    file_path: str
    initial_count: Optional[int] = None
    total_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    user_id: int

class ResultListResponse(BaseModel):
    results: List[ResultResponse]
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

# RabbitMQ consumer for task events
def consume_task_events():
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.queue_declare(queue='task_events', durable=True)
        
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                event_type = message.get('event_type')
                task_id = message.get('task_id')
                
                if event_type == 'task_completed':
                    # Create result record
                    db = next(get_db())
                    try:
                        result = Result(
                            id=task_id,
                            task_id=task_id,
                            filename=f"{task_id}.jsonl",
                            status="completed",
                            file_path=f"/app/results/{task_id}.jsonl",
                            initial_count=message.get('initial_count'),
                            total_count=message.get('total_count'),
                            user_id=1  # This should come from the message
                        )
                        db.add(result)
                        db.commit()
                        
                        # Send result created event
                        send_result_event("result_created", task_id, {
                            "status": "completed",
                            "initial_count": message.get('initial_count'),
                            "total_count": message.get('total_count')
                        })
                    finally:
                        db.close()
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error processing task event: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        channel.basic_consume(queue='task_events', on_message_callback=callback)
        channel.start_consuming()
    except Exception as e:
        print(f"Failed to start task event consumer: {e}")

def send_result_event(event_type: str, result_id: str, data: dict):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.queue_declare(queue='result_events', durable=True)
        
        message = {
            'event_type': event_type,
            'result_id': result_id,
            'timestamp': datetime.utcnow().isoformat(),
            **data
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='result_events',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to send result event: {e}")

# Routes
@app.get("/results", response_model=ResultListResponse)
async def get_results(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = db.query(Result).filter(Result.user_id == current_user["user_id"]).offset(skip).limit(limit).all()
    total = db.query(Result).filter(Result.user_id == current_user["user_id"]).count()
    
    return ResultListResponse(
        results=[
            ResultResponse(
                id=result.id,
                task_id=result.task_id,
                filename=result.filename,
                status=result.status,
                file_path=result.file_path,
                initial_count=result.initial_count,
                total_count=result.total_count,
                created_at=result.created_at,
                updated_at=result.updated_at,
                user_id=result.user_id
            ) for result in results
        ],
        total=total
    )

@app.get("/results/{result_id}", response_model=ResultResponse)
async def get_result(
    result_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.query(Result).filter(Result.id == result_id, Result.user_id == current_user["user_id"]).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return ResultResponse(
        id=result.id,
        task_id=result.task_id,
        filename=result.filename,
        status=result.status,
        file_path=result.file_path,
        initial_count=result.initial_count,
        total_count=result.total_count,
        created_at=result.created_at,
        updated_at=result.updated_at,
        user_id=result.user_id
    )

@app.get("/results/{result_id}/download")
async def download_result(
    result_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.query(Result).filter(Result.id == result_id, Result.user_id == current_user["user_id"]).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    if result.status != "completed":
        raise HTTPException(status_code=400, detail="Result not ready for download")
    
    if not os.path.exists(result.file_path):
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        path=result.file_path,
        filename=result.filename,
        media_type='application/octet-stream'
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "result-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
