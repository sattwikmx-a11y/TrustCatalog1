from backend.services.data_loader import load_olist_data
from backend.services.risk_service import RiskService

_data = None
_service = None


def get_service():
    global _data, _service
    if _service is None:
        _data = load_olist_data()
        _service = RiskService(_data)
    return _service
