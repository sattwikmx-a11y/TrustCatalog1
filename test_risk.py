import pandas as pd

from backend.agents.risk_aggregator import RiskAggregator
from backend.services.stress_runner import degrade_sellers


def test_risk_bounds():
    result = RiskAggregator().run(
        {"cancellation_signal": 1, "deterioration_signal": 1},
        {"shipping_signal": 1},
        {"fulfillment_signal": 1},
        {"anomaly_signal": 1},
    )
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] == "HIGH"


def test_degradation_changes_recent_signals():
    df = pd.DataFrame([{
        "seller_id": "S1",
        "recent_cancel_rate": 0.01,
        "recent_unavailable_rate": 0.01,
        "recent_failure_rate": 0.02,
        "recent_late_rate": 0.10,
        "recent_avg_delay_days": 1.0,
        "deterioration_cancel_rate": 0.0,
        "deterioration_failure_rate": 0.0,
        "deterioration_late_rate": 0.0,
        "deterioration_avg_delay_days": 0.0,
        "recent_review_score": 4.5,
    }])
    out = degrade_sellers(df, ["S1"], 1.0)
    assert out.loc[0, "recent_failure_rate"] > df.loc[0, "recent_failure_rate"]
    assert out.loc[0, "recent_avg_delay_days"] > df.loc[0, "recent_avg_delay_days"]
