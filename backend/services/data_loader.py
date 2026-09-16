from pathlib import Path
import pandas as pd

from backend.config import RAW_DIR, REQUIRED_FILES


def load_olist_data(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    missing = [f for f in REQUIRED_FILES if not (raw_dir / f).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing Olist CSV files: " + ", ".join(missing) +
            ". Download the public Olist dataset and place the CSVs in data/raw/."
        )
    return {f: pd.read_csv(raw_dir / f) for f in REQUIRED_FILES}


def inspect_dataframes(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, df in data.items():
        rows.append({
            "file": name,
            "rows": len(df),
            "columns": len(df.columns),
            "null_cells": int(df.isna().sum().sum()),
            "columns_list": ", ".join(df.columns),
        })
    return pd.DataFrame(rows)
