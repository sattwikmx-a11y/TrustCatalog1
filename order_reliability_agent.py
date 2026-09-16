from dataclasses import dataclass
import pandas as pd

@dataclass
class OrderReliabilityAgent:
    def run(self, row: pd.Series) -> dict:
        failure = float(row.get("recent_failure_rate", 0))
        unavailable = float(row.get("recent_unavailable_rate", 0))
        signal = min(max(failure * 0.7 + unavailable * 0.3, 0), 1)
        return {
            "seller_id": row["seller_id"],
            "fulfillment_signal": signal,
            "evidence": {
                "recent_failure_rate": failure,
                "recent_unavailable_rate": unavailable,
                "recent_delivered_rate": float(row.get("recent_delivered_rate", 0)),
            },
        }
