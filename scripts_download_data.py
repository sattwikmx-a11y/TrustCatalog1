"""Download the public Olist dataset using the Kaggle CLI.

The script refuses to overwrite an existing dataset copy. It is intentionally
separate from the runtime pipeline so production/demo runs never silently fetch data.
"""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
FILES = [
    "olist_customers_dataset.csv", "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv", "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv", "olist_orders_dataset.csv",
    "olist_products_dataset.csv", "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]

if any((RAW / f).exists() for f in FILES):
    raise SystemExit("A dataset file already exists in data/raw; refusing to download another copy.")

if shutil.which("kaggle") is None:
    raise SystemExit("Kaggle CLI is not installed. Install it separately and configure your Kaggle API token.")

RAW.mkdir(parents=True, exist_ok=True)
subprocess.run(["kaggle", "datasets", "download", "-d", "olistbr/brazilian-ecommerce", "-p", str(RAW), "--unzip"], check=True)
print("Olist dataset downloaded to", RAW)
