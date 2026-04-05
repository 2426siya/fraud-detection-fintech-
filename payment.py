import json
import math
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from data import PaymentRequest, RiskResult, TransactionSummary
from db import get_db
from ml_model import fraud_ml_model
from model import Transaction, User

router = APIRouter()

CATEGORY_RISK = {
    "Grocery":       0,
    "Entertainment": 1,
    "Electronics":   2,
    "Travel":        2,
    "Luxury":        3,
    "Crypto":        3,
    "Gaming":        1,
    "Dining":        0,
    "Healthcare":    1,
    "Other":         1,
}

def build_user_profile(user_id: int, db: Session) -> dict:
    cutoff = datetime.utcnow() - timedelta(days=90)
    history = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.timestamp >= cutoff)
        .all()
    )

    if not history:
        return {"avg_amount": 100.0, "known_lats": [], "known_lons": [], "active_hours": list(range(8, 22))}

    amounts      = [t.amount for t in history]
    known_lats   = [t.latitude  for t in history if t.latitude  is not None]
    known_lons   = [t.longitude for t in history if t.longitude is not None]
    active_hours = [t.timestamp.hour for t in history]

    return {
        "avg_amount":   sum(amounts) / len(amounts),
        "known_lats":   known_lats,
        "known_lons":   known_lons,
        "active_hours": active_hours,
    }

def velocity_in_last_hour(user_id: int, db: Session) -> int:
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.timestamp >= one_hour_ago)
        .count()
    )

def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def min_geo_distance(lat, lon, known_lats, known_lons) -> float:
    if not known_lats:
        return 0.0
    distances = [haversine_distance(lat, lon, la, lo) for la, lo in zip(known_lats, known_lons)]
    return min(distances)

def compute_risk(req: PaymentRequest, user: User, db: Session) -> dict:
    now      = datetime.utcnow()
    hour     = now.hour
    reasons  = []

    profile    = build_user_profile(user.id, db)
    avg_amount = profile["avg_amount"]
    velocity   = velocity_in_last_hour(user.id, db)

    is_night     = 1 if (hour >= 23 or hour <= 5) else 0
    cat_risk     = CATEGORY_RISK.get(req.category, 1)
    amount_ratio = req.amount / avg_amount if avg_amount > 0 else 1.0

    geo_dist        = 0.0
    is_new_location = 0
    if req.latitude and req.longitude and profile["known_lats"]:
        geo_dist = min_geo_distance(req.latitude, req.longitude, profile["known_lats"], profile["known_lons"])
        is_new_location = 1 if geo_dist > 300 else 0
    elif req.latitude and req.longitude and not profile["known_lats"]:
        is_new_location = 0
        geo_dist = 0.0

    rule_score = 0.0

    if req.amount > 2000:
        rule_score += 30
        reasons.append("Very high transaction amount (>${:.0f})".format(req.amount))
    elif req.amount > avg_amount * 3:
        rule_score += 20
        reasons.append("Amount is {:.1f}x higher than your average".format(amount_ratio))

    if is_night:
        rule_score += 15
        reasons.append("Transaction at unusual hour ({:02d}:{:02d})".format(hour, now.minute))

    if velocity >= 5:
        rule_score += 25
        reasons.append("High frequency: {} transactions in the last hour".format(velocity))
    elif velocity >= 3:
        rule_score += 10
        reasons.append("Multiple rapid transactions ({} in 1 hour)".format(velocity))

    if geo_dist > 1000:
        rule_score += 25
        reasons.append("Transaction location is {:.0f} km from your usual area".format(geo_dist))
    elif is_new_location:
        rule_score += 12
        reasons.append("New or unfamiliar location detected")

    if cat_risk >= 3:
        rule_score += 10
        reasons.append("High-risk merchant category: {}".format(req.category))
    elif cat_risk == 2:
        rule_score += 5

    rule_score = min(rule_score, 60.0)

    ml_features = [
        req.amount,
        hour,
        is_night,
        velocity,
        geo_dist,
        amount_ratio,
        is_new_location,
        cat_risk,
    ]
    ml_proba = fraud_ml_model.predict(ml_features)
    ml_score = ml_proba * 40.0

    if ml_proba > 0.75:
        reasons.append("AI model detected suspicious pattern (confidence: {:.0f}%)".format(ml_proba * 100))
    elif ml_proba > 0.5:
        reasons.append("AI model indicates moderate fraud risk")

    risk_score = round(rule_score + ml_score, 1)
    risk_score = min(risk_score, 100.0)

    if risk_score >= 70:
        alert_level = "Fraud"
        decision    = "BLOCK"
    elif risk_score >= 40:
        alert_level = "Suspicious"
        decision    = "OTP"
    else:
        alert_level = "Safe"
        decision    = "ALLOW"
        if not reasons:
            reasons.append("Transaction appears normal — no risk signals detected")

    return {
        "risk_score":  risk_score,
        "ml_score":    round(ml_proba, 4),
        "rule_score":  round(rule_score, 1),
        "alert_level": alert_level,
        "decision":    decision,
        "reasons":     reasons,
        "geo_dist":    geo_dist,
    }

@router.post("/pay", response_model=RiskResult)
def process_payment(
    req: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    risk = compute_risk(req, current_user, db)

    txn = Transaction(
        user_id       = current_user.id,
        amount        = req.amount,
        merchant      = req.merchant,
        category      = req.category,
        latitude      = req.latitude,
        longitude     = req.longitude,
        location_name = req.location_name or "Unknown",
        risk_score    = risk["risk_score"],
        decision      = risk["decision"],
        alert_level   = risk["alert_level"],
        reasons       = json.dumps(risk["reasons"]),
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    return RiskResult(
        transaction_id = txn.id,
        amount         = req.amount,
        merchant       = req.merchant,
        category       = req.category,
        location_name  = req.location_name or "Unknown",
        risk_score     = risk["risk_score"],
        ml_score       = risk["ml_score"],
        rule_score     = risk["rule_score"],
        decision       = risk["decision"],
        alert_level    = risk["alert_level"],
        reasons        = risk["reasons"],
        latitude       = req.latitude,
        longitude      = req.longitude,
        timestamp      = txn.timestamp.isoformat(),
    )

@router.get("/transactions", response_model=List[TransactionSummary])
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    txns = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.timestamp.desc())
        .limit(50)
        .all()
    )
    return [
        TransactionSummary(
            id          = t.id,
            amount      = t.amount,
            merchant    = t.merchant,
            risk_score  = t.risk_score,
            decision    = t.decision,
            alert_level = t.alert_level,
            latitude    = t.latitude,
            longitude   = t.longitude,
            timestamp   = t.timestamp.isoformat(),
        )
        for t in txns
    ]