from dataclasses import dataclass

@dataclass
class ExplanationAgent:
    def run(self, row: dict, risk: dict) -> dict:
        evidence = []
        recent_cancel = row.get("recent_cancel_rate", 0)
        base_cancel = row.get("baseline_cancel_rate", 0)
        recent_delay = row.get("recent_avg_delay_days", 0)
        base_delay = row.get("baseline_avg_delay_days", 0)
        recent_failure = row.get("recent_failure_rate", 0)
        base_failure = row.get("baseline_failure_rate", 0)
        anomaly = row.get("anomaly_score", 0)

        if recent_cancel > base_cancel + 0.03:
            evidence.append(f"Recent cancellation rate is {recent_cancel:.1%}, versus {base_cancel:.1%} in the baseline period.")
        if recent_delay > base_delay + 1:
            evidence.append(f"Average recent delivery delay is {recent_delay:.1f} days, versus {base_delay:.1f} days in the baseline period.")
        if recent_failure > base_failure + 0.03:
            evidence.append(f"Recent fulfillment failure rate is {recent_failure:.1%}, versus {base_failure:.1%} historically.")
        if anomaly >= 0.7:
            evidence.append(f"Isolation Forest marked the seller as behaviorally unusual with anomaly score {anomaly:.2f}.")
        if not evidence:
            evidence.append("No single signal dominates; the score is driven by the combined behavioral indicators.")

        if risk["risk_level"] == "HIGH":
            action = "Review active listings, inventory synchronization, and fulfillment capacity before accepting more orders."
        elif risk["risk_level"] == "MEDIUM":
            action = "Monitor the seller closely and review recent fulfillment exceptions."
        else:
            action = "Continue routine monitoring."

        return {"summary": " ".join(evidence), "evidence": evidence, "recommended_action": action}
