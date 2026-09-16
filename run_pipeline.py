from backend.services.data_loader import load_olist_data, inspect_dataframes
from backend.features.build_features import build_seller_features, build_listing_features
from backend.ml.anomaly import add_anomaly_scores
from backend.config import PROCESSED_DIR


def main():
    data = load_olist_data()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    inspect_dataframes(data).to_csv(PROCESSED_DIR / "dataset_inventory.csv", index=False)
    sellers = add_anomaly_scores(build_seller_features(data))
    listings = build_listing_features(data)
    sellers.to_parquet(PROCESSED_DIR / "seller_features.parquet", index=False)
    listings.to_parquet(PROCESSED_DIR / "listing_features.parquet", index=False)
    print("Pipeline complete:", len(sellers), "sellers;", len(listings), "seller-product listings")

if __name__ == "__main__":
    main()
