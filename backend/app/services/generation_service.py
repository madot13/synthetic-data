import requests
import json
import pandas as pd
from .prompt_parser import PromptParser
from .csv_service import CSVService
import random
import string

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODEL_NAME = "llama3"


class GenerationService:
    """
    Генератор синтетических данных.
    run/run_and_save_csv → генерация с нуля через Ollama
    run_and_fill → дополнение существующего DataFrame без генерации
    """

    def __init__(self):
        self.parser = PromptParser()
        self.csv_service = CSVService()

    def run(self, user_prompt: str, target_rows: int = None) -> pd.DataFrame:
        """
        Генерация данных с нуля через Ollama.
        """
        if target_rows is None:
            target_rows = self.parser.extract_rows(user_prompt)

        columns = self.parser.extract_columns(user_prompt)

        system_instruction = f"""
        You are a data generator. Return ONLY valid JSON.
        Format: {{ "data": [ {{ {", ".join([f'"{c}": "value"' for c in columns])} }} ] }}
        Generate exactly {target_rows} rows.
        Each column should contain realistic values:
        - id: unique number
        - name / имя: realistic first name
        - surname / фамилия: realistic last name
        - salary / зарплата: integer
        - возраст / age: realistic number
        - рост / height: realistic number
        - вес / weight: realistic number
        - пол / gender: M/F
        - Любые другие колонки → readable text
        Return ONLY valid JSON without extra text.
        """

        full_prompt = f"{system_instruction}\n\n{user_prompt}"

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 800}
                },
                timeout=120
            )
            raw = response.json().get("response", "")
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return pd.DataFrame()

        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            return pd.DataFrame()

        try:
            parsed = json.loads(raw[start:end+1])
            data = parsed.get("data", [])
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            print(f"JSON parsing error: {e}")
            return pd.DataFrame()

    def run_and_save_csv(self, user_prompt: str, target_rows: int = None) -> str:
        """
        Генерация через Ollama + сохранение в CSV.
        """
        df = self.run(user_prompt, target_rows)
        if df.empty:
            print("No data generated")
            return ""
        return self.csv_service.save(df)

    def run_and_fill(self, df_existing: pd.DataFrame, user_prompt: str) -> pd.DataFrame:
        """
        Дополнение существующего DataFrame недостающими колонками и строками.
        НЕ вызывает генерацию через Ollama.
        """
        columns = self.parser.extract_columns(user_prompt)
        target_rows = self.parser.extract_rows(user_prompt)

        # Сохраняем текущий max_id
        if "id" in df_existing.columns:
            max_id = df_existing["id"].max()
        else:
            max_id = 0
            df_existing["id"] = 0

        # Дополняем недостающие колонки для существующих строк
        for col in columns:
            if col not in df_existing.columns:
                df_existing[col] = [self._generate_placeholder(
                    col) for _ in range(len(df_existing))]

        # Добавляем недостающие строки
        if len(df_existing) < target_rows:
            new_records = []
            for i in range(len(df_existing) + 1, target_rows + 1):
                record = {"id": i}
                for col in columns:
                    if col != "id":
                        record[col] = self._generate_placeholder(col)
                new_records.append(record)
            df_new = pd.DataFrame(new_records)
            df_existing = pd.concat([df_existing, df_new], ignore_index=True)

        return df_existing

    def _generate_placeholder(self, column_name: str):
        """
        Генерация читаемых значений для неизвестных колонок.
        Используется только в run_and_fill, без Ollama.
        """
        column_name = column_name.lower()

        if "name" in column_name or "имя" in column_name:
            return random.choice(["Ivan", "Maria", "Olga", "Sergey", "Anna", "Dmitry"])
        if "surname" in column_name or "фамилия" in column_name:
            return random.choice(["Ivanov", "Petrov", "Sidorov", "Kuznetsov"])
        if "salary" in column_name or "зарплата" in column_name:
            return random.randint(30000, 200000)
        if "age" in column_name or "возраст" in column_name:
            return random.randint(18, 70)
        if "height" in column_name or "рост" in column_name:
            return round(random.uniform(150, 200), 1)
        if "weight" in column_name or "вес" in column_name:
            return round(random.uniform(50, 120), 1)
        if "gender" in column_name or "пол" in column_name:
            return random.choice(["M", "F"])
        # Любой другой текст
        length = random.randint(4, 10)
        return "".join(random.choices(string.ascii_letters, k=length))
