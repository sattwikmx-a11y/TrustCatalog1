from dataclasses import dataclass
import pandas as pd

@dataclass
class ShippingAgent:
    def run(self, row: pd.Series) -> dict:
        delay = float(row.get("recent_avg_delay_days", 0))
        late_rate = float(row.get("recent_late_rate", 0))
        signal = min(max((delay / 10.0) * 0.6 + late_rate * 0.4, 0), 1)
        return {
            "seller_id": row["seller_id"],
            "shipping_signal": signal,
            "evidence": {
                "recent_avg_delay_days": delay,
                "baseline_avg_delay_days": float(row.get("baseline_avg_delay_days", 0)),
                "recent_late_rate": late_rate,
            },
        }
