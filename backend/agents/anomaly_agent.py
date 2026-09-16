from dataclasses import dataclass
import pandas as pd

@dataclass
class AnomalyDetectionAgent:
    def run(self, row: pd.Series) -> dict:
        return {
            "seller_id": row["seller_id"],
            "anomaly_signal": float(row.get("anomaly_score", 0)),
            "anomaly_flag": int(row.get("anomaly_flag", 0)),
            "evidence": {
                "anomaly_score": float(row.get("anomaly_score", 0)),
                "anomaly_flag": int(row.get("anomaly_flag", 0)),
            },
        }
