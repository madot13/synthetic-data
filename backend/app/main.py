from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from celery.result import AsyncResult
import pandas as pd

from app.celery_client import celery_app

app = FastAPI()

# --- CORS ---
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Статика ---
app.mount("/storage", StaticFiles(directory="/app/storage"), name="storage")

# --- Модели ---


class GenerateRequest(BaseModel):
    prompt: str
    rows: int = 10  # по умолчанию

# --- Роуты ---


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0"}


@app.post("/generate-tabular")
def generate_tabular(request: GenerateRequest):
    if request.rows < 1:
        request.rows = 10

    task = celery_app.send_task(
        "worker.tasks.generate_data_task",
        args=[request.prompt, request.rows]
    )
    return {"task_id": task.id, "status": "processing"}


@app.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.state == "PENDING":
        return {"status": "pending"}
    if task_result.state == "SUCCESS":
        return {"status": "completed", "result": task_result.result}
    if task_result.state == "FAILURE":
        return {"status": "failed", "error": str(task_result.result)}
    return {"status": task_result.state.lower()}


# --- Новый эндпоинт для загрузки файла и дополнения ---
@app.post("/upload-and-extend")
async def upload_and_extend(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    rows: int = Form(10)
):
    # Сохраняем загруженный файл во временную папку
    temp_path = f"/app/storage/temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Отправляем задачу Celery для дополнения
    task = celery_app.send_task(
        "worker.tasks.extend_data_task",
        args=[temp_path, prompt, rows]
    )
    return {"task_id": task.id, "status": "processing"}
