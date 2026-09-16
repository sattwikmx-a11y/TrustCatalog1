from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.app_state import get_service
from backend.services.stress_runner import run_stress_test

router = APIRouter(prefix="/api")

class StressTestRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=100)
    severity: float = Field(default=1.0, ge=0.1, le=3.0)

@router.get("/health")
def health():
    return {"status": "ok", "project": "TrustCatalog"}

@router.get("/overview")
def overview():
    return get_service().overview()

@router.get("/sellers")
def sellers(limit: int = 100):
    return get_service().ranking(max(1, min(limit, 1000)))

@router.get("/sellers/{seller_id}")
def seller(seller_id: str):
    result = get_service().seller(seller_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Seller not found")
    return result

@router.get("/risk-ranking")
def risk_ranking(limit: int = 100):
    return get_service().ranking(max(1, min(limit, 1000)))

@router.get("/agents/{seller_id}")
def agents(seller_id: str):
    result = get_service().agents(seller_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Seller not found")
    return result

@router.post("/stress-test")
def stress_test(payload: StressTestRequest):
    return run_stress_test(get_service(), payload.count, payload.severity)

@router.get("/evaluation")
def evaluation():
    return {
        "note": "Olist has no direct ghost-listing ground-truth label in the public dataset. Evaluation must therefore use controlled simulated degradation labels.",
        "metrics": "Run POST /api/stress-test to calculate detection_rate and top-k detection from the actual run.",
    }
