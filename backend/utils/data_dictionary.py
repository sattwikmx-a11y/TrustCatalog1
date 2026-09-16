import json
from pathlib import Path
from backend.services.data_loader import load_olist_data
from backend.config import PROCESSED_DIR


def build_dictionary():
    data = load_olist_data()
    result = {}
    for name, df in data.items():
        result[name] = {
            "rows": len(df),
            "columns": [
                {"name": c, "dtype": str(df[c].dtype), "nulls": int(df[c].isna().sum())}
                for c in df.columns
            ],
        }
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / "data_dictionary.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return path

if __name__ == "__main__":
    print(build_dictionary())
