from backend.agents.seller_behavior_agent import SellerBehaviorAgent
from backend.agents.shipping_agent import ShippingAgent
from backend.agents.order_reliability_agent import OrderReliabilityAgent
from backend.agents.anomaly_agent import AnomalyDetectionAgent
from backend.agents.risk_aggregator import RiskAggregator
from backend.agents.explanation_agent import ExplanationAgent

class Orchestrator:
    def __init__(self):
        self.seller_agent = SellerBehaviorAgent()
        self.shipping_agent = ShippingAgent()
        self.order_agent = OrderReliabilityAgent()
        self.anomaly_agent = AnomalyDetectionAgent()
        self.aggregator = RiskAggregator()
        self.explanation_agent = ExplanationAgent()

    def analyze_row(self, row):
        seller = self.seller_agent.run(row)
        shipping = self.shipping_agent.run(row)
        order = self.order_agent.run(row)
        anomaly = self.anomaly_agent.run(row)
        risk = self.aggregator.run(seller, shipping, order, anomaly)
        explanation = self.explanation_agent.run(row.to_dict(), risk)
        return {
            "seller_behavior": seller,
            "shipping": shipping,
            "order_reliability": order,
            "anomaly": anomaly,
            "risk": risk,
            "explanation": explanation,
        }
