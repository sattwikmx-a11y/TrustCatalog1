from __future__ import annotations

import pandas as pd

from backend.features.build_features import build_seller_features, build_listing_features
from backend.ml.anomaly import add_anomaly_scores
from backend.agents.orchestrator import Orchestrator

class RiskService:
    def __init__(self, data):
        self.data = data
        self.sellers = self._build()
        self.listings = build_listing_features(data)
        self.orchestrator = Orchestrator()
        self.analysis = self._analyze()

    def _build(self):
        return add_anomaly_scores(build_seller_features(self.data))

    def _analyze(self):
        rows = []
        for _, row in self.sellers.iterrows():
            result = self.orchestrator.analyze_row(row)
            rows.append({
                "seller_id": row["seller_id"],
                "risk_score": result["risk"]["risk_score"],
                "risk_level": result["risk"]["risk_level"],
                "cancellation_rate": row["recent_cancel_rate"],
                "delivery_delay_days": row["recent_avg_delay_days"],
                "deterioration": row["deterioration_failure_rate"],
                "anomaly_score": row["anomaly_score"],
                "orders": row["lifetime_orders"],
                "analysis": result,
            })
        return pd.DataFrame(rows).sort_values("risk_score", ascending=False).reset_index(drop=True)

    def overview(self):
        risk_counts = self.analysis["risk_level"].value_counts().to_dict()
        return {
            "total_sellers": int(len(self.analysis)),
            "total_orders": int(self.data["olist_orders_dataset.csv"].shape[0]),
            "high_risk_sellers": int(risk_counts.get("HIGH", 0)),
            "medium_risk_sellers": int(risk_counts.get("MEDIUM", 0)),
            "low_risk_sellers": int(risk_counts.get("LOW", 0)),
            "average_risk_score": round(float(self.analysis["risk_score"].mean()), 2),
            "anomalies": int(self.analysis["anomaly_score"].ge(0.7).sum()),
            "deteriorating_sellers": int(self.analysis["deterioration"].gt(0.03).sum()),
            "top_alerts": self.ranking(10),
        }

    def ranking(self, limit=100):
        cols = ["seller_id", "risk_score", "risk_level", "cancellation_rate", "delivery_delay_days", "deterioration", "anomaly_score", "orders"]
        return self.analysis[cols].head(limit).to_dict(orient="records")

    def seller(self, seller_id):
        match = self.analysis[self.analysis["seller_id"] == seller_id]
        if match.empty:
            return None
        row = match.iloc[0]
        return {
            "seller_id": seller_id,
            "risk_score": row["risk_score"],
            "risk_level": row["risk_level"],
            "metrics": self.sellers[self.sellers["seller_id"] == seller_id].iloc[0].to_dict(),
            "analysis": row["analysis"],
            "listing_summary": self.listings[self.listings["seller_id"] == seller_id].head(20).to_dict(orient="records"),
        }

    def agents(self, seller_id):
        result = self.seller(seller_id)
        return result["analysis"] if result else None
