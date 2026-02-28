import requests
import json

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODEL_NAME = "llama3"


class OllamaService:
    def generate_batch(self, prompt: str, columns: list, rows: int):
        """
        Отправляет запрос в Ollama и возвращает список словарей
        по колонкам с нужным количеством строк.
        """
        system_instruction = f"""
        You are a data generator. Return ONLY valid JSON.
        Format: {{ "data": [ {{ {", ".join([f'"{c}": "value"' for c in columns])} }} ] }}
        Generate exactly {rows} rows.
        """

        full_prompt = f"{system_instruction}\n\n{prompt}"

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
            return []

        # чистим лишние символы
        raw = raw.replace("\njson", "").replace("\n", "")
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            return []

        try:
            parsed = json.loads(raw[start:end+1])
            return parsed.get("data", [])
        except Exception as e:
            print(f"JSON parsing error: {e}")
            return []
