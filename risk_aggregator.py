from dataclasses import dataclass
import pandas as pd

from backend.config import RISK_WEIGHTS


def _clip(v):
    return max(0.0, min(1.0, float(v)))

@dataclass
class RiskAggregator:
    def run(self, seller_signal: dict, shipping_signal: dict, fulfillment_signal: dict, anomaly_signal: dict) -> dict:
        deterioration = _clip(seller_signal["deterioration_signal"])
        cancellation = _clip(seller_signal["cancellation_signal"])
        shipping = _clip(shipping_signal["shipping_signal"])
        fulfillment = _clip(fulfillment_signal["fulfillment_signal"])
        anomaly = _clip(anomaly_signal["anomaly_signal"])
        components = {
            "cancellation": cancellation,
            "shipping": shipping,
            "fulfillment": fulfillment,
            "deterioration": deterioration,
            "anomaly": anomaly,
        }
        score = 100 * sum(components[k] * RISK_WEIGHTS[k] for k in components)
        level = "LOW" if score < 40 else "MEDIUM" if score < 70 else "HIGH"
        return {"risk_score": round(score, 2), "risk_level": level, "components": components}
