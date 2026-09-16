from __future__ import annotations

import numpy as np
import pandas as pd

DATE_COLS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def _safe_rate(num, den):
    return np.where(den > 0, num / den, 0.0)


def prepare_order_level(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    orders = data["olist_orders_dataset.csv"].copy()
    items = data["olist_order_items_dataset.csv"].copy()
    reviews = data["olist_order_reviews_dataset.csv"].copy()

    for col in DATE_COLS:
        if col in orders.columns:
            orders[col] = pd.to_datetime(orders[col], errors="coerce")

    # Seller attribution is available through order_items, not orders.
    seller_per_order = (
        items.groupby("order_id")
        .agg(
            seller_id=("seller_id", "first"),
            item_count=("order_item_id", "count"),
            product_count=("product_id", "nunique"),
            order_value=("price", "sum"),
            freight_value=("freight_value", "sum"),
        )
        .reset_index()
    )

    # An order can have multiple review rows in the raw data. Aggregate safely.
    review_per_order = (
        reviews.groupby("order_id")
        .agg(review_score=("review_score", "mean"))
        .reset_index()
    )

    out = orders.merge(seller_per_order, on="order_id", how="left")
    out = out.merge(review_per_order, on="order_id", how="left")

    out["delivery_days"] = (
        out["order_delivered_customer_date"] - out["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    out["shipping_delay_days"] = (
        out["order_delivered_customer_date"] - out["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400
    out["shipping_delay_days"] = out["shipping_delay_days"].clip(lower=0)
    out["is_late"] = (out["shipping_delay_days"] > 0).astype(int)
    out["is_cancelled"] = out["order_status"].eq("canceled").astype(int)
    out["is_unavailable"] = out["order_status"].eq("unavailable").astype(int)
    out["is_failed_fulfillment"] = out[["is_cancelled", "is_unavailable"]].max(axis=1)
    out["is_delivered"] = out["order_status"].eq("delivered").astype(int)
    return out


def _period_features(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    g = df.groupby("seller_id")
    result = g.agg(
        **{
            f"{prefix}_orders": ("order_id", "nunique"),
            f"{prefix}_items": ("item_count", "sum"),
            f"{prefix}_cancel_rate": ("is_cancelled", "mean"),
            f"{prefix}_unavailable_rate": ("is_unavailable", "mean"),
            f"{prefix}_failure_rate": ("is_failed_fulfillment", "mean"),
            f"{prefix}_delivered_rate": ("is_delivered", "mean"),
            f"{prefix}_late_rate": ("is_late", "mean"),
            f"{prefix}_avg_delivery_days": ("delivery_days", "mean"),
            f"{prefix}_avg_delay_days": ("shipping_delay_days", "mean"),
            f"{prefix}_review_score": ("review_score", "mean"),
        }
    ).reset_index()
    return result


def build_seller_features(data: dict[str, pd.DataFrame], recent_days: int = 45, baseline_days: int = 120) -> pd.DataFrame:
    orders = prepare_order_level(data)
    orders = orders.dropna(subset=["seller_id", "order_purchase_timestamp"]).copy()
    max_date = orders["order_purchase_timestamp"].max()

    recent_start = max_date - pd.Timedelta(days=recent_days)
    baseline_start = max_date - pd.Timedelta(days=baseline_days)

    recent = orders[orders["order_purchase_timestamp"] >= recent_start]
    baseline = orders[
        (orders["order_purchase_timestamp"] < recent_start)
        & (orders["order_purchase_timestamp"] >= baseline_start)
    ]

    lifetime = _period_features(orders, "lifetime")
    recent_f = _period_features(recent, "recent")
    baseline_f = _period_features(baseline, "baseline")

    seller = lifetime.merge(recent_f, on="seller_id", how="left").merge(baseline_f, on="seller_id", how="left")

    numeric_cols = [c for c in seller.columns if c != "seller_id"]
    seller[numeric_cols] = seller[numeric_cols].fillna(0)

    # Deterioration is recent minus baseline. Positive is worse for the risk-oriented rates/delays.
    for metric in ["cancel_rate", "unavailable_rate", "failure_rate", "late_rate", "avg_delay_days"]:
        seller[f"deterioration_{metric}"] = seller[f"recent_{metric}"] - seller[f"baseline_{metric}"]
    seller["deterioration_review_score"] = seller["baseline_review_score"] - seller["recent_review_score"]

    seller["recent_vs_baseline_volume_change"] = np.where(
        seller["baseline_orders"] > 0,
        (seller["recent_orders"] - seller["baseline_orders"]) / seller["baseline_orders"],
        0.0,
    )

    return seller


def build_listing_features(data: dict[str, pd.DataFrame], recent_days: int = 45) -> pd.DataFrame:
    orders = prepare_order_level(data)
    items = data["olist_order_items_dataset.csv"].copy()
    orders = orders[["order_id", "order_purchase_timestamp", "order_status", "is_failed_fulfillment", "is_late", "shipping_delay_days", "delivery_days"]]
    joined = items.merge(orders, on="order_id", how="left")
    max_date = joined["order_purchase_timestamp"].max()
    joined["is_recent"] = joined["order_purchase_timestamp"] >= max_date - pd.Timedelta(days=recent_days)

    listing = joined.groupby(["seller_id", "product_id"]).agg(
        listing_orders=("order_id", "nunique"),
        listing_items=("order_item_id", "count"),
        listing_failure_rate=("is_failed_fulfillment", "mean"),
        listing_late_rate=("is_late", "mean"),
        listing_avg_delay_days=("shipping_delay_days", "mean"),
        listing_avg_delivery_days=("delivery_days", "mean"),
        recent_listing_orders=("is_recent", "sum"),
    ).reset_index()
    return listing
