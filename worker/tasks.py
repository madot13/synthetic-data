from celery import Celery
import os
import pandas as pd
from backend.app.services.generation_service import GenerationService

celery_app = Celery(
    "worker",
    broker=os.environ.get("CELERY_BROKER_URL"),
    backend=os.environ.get("CELERY_RESULT_BACKEND"),
)

generation_service = GenerationService()


@celery_app.task(bind=True, name="worker.tasks.generate_data_task")
def generate_data_task(self, prompt: str, rows: int):
    try:
        df = generation_service.run(prompt, rows)
        filename = generation_service.csv_service.save(df)
        return {"status": "completed", "filename": filename, "rows": len(df), "columns": df.columns.tolist()}
    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise


@celery_app.task(bind=True, name="worker.tasks.extend_data_task")
def extend_data_task(self, file_path: str, prompt: str, rows: int):
    try:
        # Загружаем существующий CSV
        df_existing = pd.read_csv(file_path)

        # Генерируем новые строки на основе промпта
        df_new = generation_service.run(prompt, rows)

        # Объединяем
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)

        # Сохраняем итоговый CSV
        filename = generation_service.csv_service.save(df_combined)
        return {"status": "completed", "filename": filename, "rows": len(df_combined), "columns": df_combined.columns.tolist()}
    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise
