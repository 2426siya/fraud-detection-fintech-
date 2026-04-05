from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PaymentRequest(BaseModel):
    amount: float
    merchant: str
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = "Unknown"


class RiskResult(BaseModel):
    transaction_id: int
    amount: float
    merchant: str
    category: str
    location_name: str

    risk_score: float
    ml_score: float
    rule_score: float

    decision: str
    alert_level: str

    reasons: List[str]

    latitude: Optional[float]
    longitude: Optional[float]

    timestamp: str


class TransactionSummary(BaseModel):
    id: int
    amount: float
    merchant: str
    risk_score: float
    decision: str
    alert_level: str
    latitude: Optional[float]
    longitude: Optional[float]
    timestamp: str

    class Config:
        from_attributes = True