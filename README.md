# Synthetic Data Generator 🧬

Платформа для генерации синтетических данных с использованием локальных языковых моделей (LLM). Проект позволяет развернуть полноценное веб-приложение для создания реалистичных датасетов без отправки данных на внешние API.

## ✨ Возможности

- **Генерация данных с нуля** - Создание датасетов на основе текстовых описаний
- **Расширение существующих данных** - Загрузка CSV файлов и дополнение их новыми строками
- **Локальные LLM** - Работа с Ollama для полной конфиденциальности данных
- **Асинхронная обработка** - Фоновые задачи через Celery для больших объемов данных
- **Веб-интерфейс** - Удобный Next.js фронтенд для управления генерацией
- **Экспорт** - Выгрузка результатов в CSV и JSON форматах

## 🏗 Архитектура

Проект построен по микросервисной архитектуре с использованием Docker Compose:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Worker        │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Celery)      │
│   :3000         │    │   :8000         │    │   LLM Tasks     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   Redis         │
                       │   :5432         │    │   :6379         │
                       └─────────────────┘    └─────────────────┘
```

### Компоненты системы

**Frontend (Next.js + TypeScript)**
- Современный веб-интерфейс с Tailwind CSS
- Формы для создания задач генерации данных
- Мониторинг статуса задач в реальном времени
- Загрузка и скачивание файлов

**Backend (FastAPI + Python)**
- RESTful API для обработки запросов
- Интеграция с Celery для фоновых задач
- Работа с PostgreSQL для хранения метаданных
- Обработка загрузки файлов и валидация данных

**Worker (Celery + Python)**
- Асинхронная генерация данных через Ollama LLM
- Интеллектуальный парсинг промптов
- Обработка больших объемов данных без блокировки API
- Интеграция с локальными моделями (Llama 3 и др.)

**Infrastructure**
- PostgreSQL - основная база данных
- Redis - брокер сообщений для Celery
- Docker Compose - оркестрация всех сервисов

---

## 🛠 Предварительные требования

Перед запуском убедитесь, что у вас установлены:

1. **Docker** и **Docker Compose** (версия 20.10+)
2. **Ollama** (для запуска локальных моделей)
3. **Минимум 8GB RAM** для работы LLM моделей

### Установка Ollama

1. Скачайте и установите Ollama с [официального сайта](https://ollama.com/)
2. Запустите Ollama сервис:
```bash
ollama serve
```

3. Скачайте рекомендованную модель (Llama 3 8B):
```bash
ollama pull llama3:8b
```

4. Проверьте работу модели:
```bash
ollama run llama3:8b "Hello, can you generate some sample data?"
```

*Убедитесь, что Ollama запущена и доступна по адресу `http://localhost:11434`.*

---

## 🚀 Быстрый запуск

### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd synthetic-data-generator
```

### 2. Запуск через Docker Compose

Самый простой способ поднять все сервисы сразу:

```bash
docker-compose up --build
```

Это запустит:

- **Веб-интерфейс** на `http://localhost:3000`
- **API бэкенда** на `http://localhost:8000`
- **PostgreSQL** на `localhost:5432`
- **Redis** на `localhost:6379`
- **Celery воркеры** для фоновых задач

### 3. Проверка работоспособности

Откройте в браузере `http://localhost:3000` и убедитесь, что интерфейс загружается корректно.

---

## 📖 Использование платформы

### Генерация данных с нуля

1. **Создание задачи**: В веб-интерфейсе опишите структуру данных, которую вы хотите получить
   ```
   Пример промпта:
   "Сгенерируй 100 строк данных о сотрудниках:
   - id (уникальный номер)
   - имя (русское имя)
   - фамилия (русская фамилия) 
   - возраст (25-60 лет)
   - зарплата (30000-150000)
   - отдел (IT, Sales, Marketing, HR)"
   ```

2. **Мониторинг**: Следите за статусом задачи в реальном времени
3. **Результат**: Скачайте готовый CSV файл сгенерированных данных

### Расширение существующих данных

1. **Загрузка CSV**: Загрузите существующий файл через интерфейс
2. **Описание дополнения**: Укажите, какие данные нужно добавить
   ```
   Пример промпта:
   "Добавь 50 новых сотрудников в тех же отделах, 
   но с возрастом 30-45 лет и зарплатой 50000-120000"
   ```
3. **Получение результата**: Скачайте обновленный файл

---

## 📂 Структура проекта

```
synthetic-data-generator/
├── backend/                 # FastAPI приложение
│   ├── app/
│   │   ├── main.py         # Основной файл приложения
│   │   ├── models.py       # Модели данных
│   │   └── services/       # Бизнес-логика
│   │       ├── generation_service.py  # Генерация данных
│   │       ├── ollama_service.py      # Работа с LLM
│   │       ├── csv_service.py         # Работа с CSV
│   │       └── prompt_parser.py       # Парсинг промптов
│   ├── requirements.txt    # Python зависимости
│   └── Dockerfile         # Docker конфигурация
├── frontend/               # Next.js приложение
│   ├── app/               # React компоненты
│   ├── package.json       # Node.js зависимости
│   └── Dockerfile         # Docker конфигурация
├── worker/                 # Celery воркеры
│   ├── tasks.py          # Фоновые задачи
│   ├── requirements.txt  # Python зависимости
│   └── Dockerfile        # Docker конфигурация
├── storage/               # Хранилище файлов
├── docker-compose.yml     # Оркестрация сервисов
└── README.md             # Документация
```

---

## 🔧 API Эндпоинты

### Основные эндпоинты

- `GET /health` - Проверка работоспособности API
- `POST /generate-tabular` - Генерация данных с нуля
- `GET /task-status/{task_id}` - Статус фоновой задачи
- `POST /upload-and-extend` - Загрузка и расширение данных

### Пример запроса

```bash
curl -X POST "http://localhost:8000/generate-tabular" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Сгенерируй 50 пользователей с именем, email и возрастом",
       "rows": 50
     }'
```

---

## 🧪 Локальная разработка

Для разработки без Docker:

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Worker

```bash
cd worker
pip install -r requirements.txt
celery -A tasks.celery_app worker --loglevel=info
```

---

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/synthetic_db

# Redis/Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Ollama
OLLAMA_URL=http://host.docker.internal:11434/api/generate
MODEL_NAME=llama3:8b

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🐛 Troubleshooting

### Частые проблемы

1. **Ollama недоступна**
   - Убедитесь, что `ollama serve` запущен
   - Проверьте доступность `http://localhost:11434`

2. **Модель не найдена**
   - Скачайте модель: `ollama pull llama3:8b`
   - Проверьте список моделей: `ollama list`

3. **Память insufficient**
   - Требуется минимум 8GB RAM для LLM моделей
   - Используйте более легкие модели при необходимости

4. **Docker проблемы**
   - Очистите контейнеры: `docker-compose down -v`
   - Пересоберите: `docker-compose up --build --force-recreate`

---

## 🤝 Вклад в проект

1. Fork проекта
2. Создайте feature branch: `git checkout -b feature/new-feature`
3. Commit изменения: `git commit -am 'Add new feature'`
4. Push в branch: `git push origin feature/new-feature`
5. Создайте Pull Request

---

## 📄 Лицензия

Проект распространяется под MIT License. См. файл LICENSE для деталей.

---

## 🆘 Поддержка

Если у вас возникли вопросы или проблемы:

- Создайте Issue в GitHub репозитории
- Проверьте раздел Troubleshooting выше
- Обратитесь к документации API

---

**Создано с ❤️ для сообщества Data Science**
