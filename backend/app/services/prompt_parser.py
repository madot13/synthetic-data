import re


class PromptParser:
    """
    Извлечение колонок и количества строк из промпта.
    Любая цифра в строке = количество строк.
    """
    @staticmethod
    def extract_rows(prompt: str) -> int:
        match = re.search(r"\b(\d+)\b", prompt)
        if match:
            return int(match.group(1))
        return 10

    @staticmethod
    def extract_columns(prompt: str) -> list:
        match = re.search(
            r"(?:где|columns?|:)\s*([\w ,а-яА-ЯёЁ]+)",
            prompt,
            re.IGNORECASE
        )
        if match:
            cols = match.group(1)
            return [c.strip() for c in re.split(r"[,\s]+", cols) if c.strip()]
        return ["name", "value"]
