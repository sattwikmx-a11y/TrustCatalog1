from dataclasses import dataclass
import pandas as pd

@dataclass
class SellerBehaviorAgent:
    def run(self, row: pd.Series) -> dict:
        cancellation = min(max(float(row.get("recent_cancel_rate", 0)), 0), 1)
        deterioration = min(max(float(row.get("deterioration_failure_rate", 0)) * 3, 0), 1)
        return {
            "seller_id": row["seller_id"],
            "cancellation_signal": cancellation,
            "reliability_signal": min(max(float(row.get("recent_failure_rate", 0)), 0), 1),
            "deterioration_signal": deterioration,
            "evidence": {
                "recent_cancel_rate": float(row.get("recent_cancel_rate", 0)),
                "recent_failure_rate": float(row.get("recent_failure_rate", 0)),
                "baseline_failure_rate": float(row.get("baseline_failure_rate", 0)),
            },
        }
