import pandas as pd
import os
from datetime import datetime


class CSVService:
    """
    Сохраняет DataFrame в CSV.
    """

    def save(self, df: pd.DataFrame) -> str:
        output_dir = "/app/storage/results"
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"synthetic_{timestamp}.csv"
        file_path = os.path.join(output_dir, filename)

        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        return filename
