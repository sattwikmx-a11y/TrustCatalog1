from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler

ANOMALY_FEATURES = [
    "recent_failure_rate",
    "recent_late_rate",
    "recent_avg_delay_days",
    "deterioration_failure_rate",
    "deterioration_late_rate",
    "deterioration_avg_delay_days",
    "recent_vs_baseline_volume_change",
    "recent_review_score",
]


def add_anomaly_scores(seller: pd.DataFrame) -> pd.DataFrame:
    out = seller.copy()
    cols = [c for c in ANOMALY_FEATURES if c in out.columns]
    if len(out) < 20 or not cols:
        out["anomaly_score"] = 0.0
        out["anomaly_flag"] = 0
        return out

    X = out[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    X = RobustScaler().fit_transform(X)
    model = IsolationForest(
        n_estimators=300,
        contamination="auto",
        random_state=42,
    )
    model.fit(X)
    raw = -model.score_samples(X)
    lo, hi = np.percentile(raw, 1), np.percentile(raw, 99)
    out["anomaly_score"] = np.clip((raw - lo) / max(hi - lo, 1e-9), 0, 1)
    out["anomaly_flag"] = (model.predict(X) == -1).astype(int)
    return out
