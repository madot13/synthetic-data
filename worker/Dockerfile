FROM python:3.11-slim

WORKDIR /app

# Копируем весь backend, чтобы сохранить структуру
COPY backend ./backend
COPY worker/tasks.py ./tasks.py

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r backend/requirements.txt

CMD ["celery", "-A", "tasks.celery_app", "worker", "--loglevel=info"]