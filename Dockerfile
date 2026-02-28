FROM python:3.10-slim

# Устанавливаем системные зависимости для работы с PDF и библиотеками Meta
RUN apt-get update && apt-get install -y \
    git \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Устанавливаем SDK от Meta прямо из репозитория или через локальный файл
RUN pip install -e "git+https://github.com/meta-llama/synthetic-data-kit.git#egg=synthetic-data-kit"
RUN pip install celery redis sqlalchemy psycopg2-binary python-dotenv

COPY . .

# Запуск воркера
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]