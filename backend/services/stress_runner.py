from __future__ import annotations

import numpy as np
import pandas as pd

from backend.ml.anomaly import add_anomaly_scores
from backend.agents.orchestrator import Orchestrator


def degrade_sellers(seller_features: pd.DataFrame, seller_ids: list[str], severity: float = 1.0) -> pd.DataFrame:
    out = seller_features.copy(deep=True)
    mask = out["seller_id"].isin(seller_ids)
    for col, multiplier in [
        ("recent_cancel_rate", 3.0),
        ("recent_unavailable_rate", 3.0),
        ("recent_failure_rate", 2.5),
        ("recent_late_rate", 1.8),
        ("recent_avg_delay_days", 2.5),
    ]:
        if col in out.columns:
            base = out.loc[mask, col].astype(float)
            out.loc[mask, col] = np.clip(base * (1 + severity * (multiplier - 1)), 0, None)
    for col in ["deterioration_cancel_rate", "deterioration_failure_rate", "deterioration_late_rate", "deterioration_avg_delay_days"]:
        if col in out.columns:
            out.loc[mask, col] = out.loc[mask, col].astype(float) + severity * 0.20
    out.loc[mask, "recent_review_score"] = np.maximum(1.0, out.loc[mask, "recent_review_score"] - severity * 1.0)
    return out


def score_features(features: pd.DataFrame) -> pd.DataFrame:
    features = add_anomaly_scores(features)
    orchestrator = Orchestrator()
    rows = []
    for _, row in features.iterrows():
        a = orchestrator.analyze_row(row)
        rows.append({
            "seller_id": row["seller_id"],
            "risk_score": a["risk"]["risk_score"],
            "risk_level": a["risk"]["risk_level"],
            "anomaly_score": row["anomaly_score"],
        })
    return pd.DataFrame(rows).sort_values("risk_score", ascending=False).reset_index(drop=True)


def run_stress_test(service, count=10, severity=1.0, seed=42):
    rng = np.random.default_rng(seed)
    candidates = service.sellers[service.sellers["lifetime_orders"] >= 10]["seller_id"].tolist()
    if len(candidates) < count:
        count = len(candidates)
    ids = rng.choice(candidates, size=count, replace=False).tolist()
    before = service.analysis[["seller_id", "risk_score", "risk_level"]].copy()
    degraded = degrade_sellers(service.sellers, ids, severity)
    after = score_features(degraded)
    k = min(max(count, 10), len(after))
    top_k = after.head(k)
    positive = set(ids)
    detected = positive.intersection(set(top_k["seller_id"]))
    false_positives = len(set(top_k["seller_id"]) - positive)
    negatives = max(len(after) - count, 0)
    false_positive_rate = false_positives / negatives if negatives else 0.0
    precision_at_k = len(detected) / k if k else 0.0
    recall = len(detected) / count if count else 0.0
    f1 = (2 * precision_at_k * recall / (precision_at_k + recall)) if (precision_at_k + recall) else 0.0
    return {
        "selected_sellers": ids,
        "before": before[before["seller_id"].isin(ids)].to_dict(orient="records"),
        "after": after[after["seller_id"].isin(ids)].to_dict(orient="records"),
        "ranking_top_k": top_k.to_dict(orient="records"),
        "k": k,
        "degraded_count": count,
        "detected_in_top_k": len(detected),
        "detection_rate": round(recall, 4),
        "precision_at_k": round(precision_at_k, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "false_positive_rate": round(false_positive_rate, 4),
        "labels_are_simulated": True,
    }
