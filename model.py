from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base


class User(Base):
    __tablename__ = "users"

    id               = Column(Integer, primary_key=True, index=True)
    username         = Column(String(100), unique=True, nullable=False, index=True)
    email            = Column(String(191), unique=True, nullable=False)
    hashed_password  = Column(String(255), nullable=False)
    created_at       = Column(DateTime, default=datetime.utcnow)

    transactions     = relationship("Transaction", back_populates="user")


class Transaction(Base):
    __tablename__ = "transactions"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)

    amount          = Column(Float, nullable=False)
    merchant        = Column(String(191), nullable=False)
    category        = Column(String(100), nullable=False)

    latitude        = Column(Float, nullable=True)
    longitude       = Column(Float, nullable=True)
    location_name   = Column(String(191), nullable=True)

    risk_score      = Column(Float, default=0.0)
    decision        = Column(String(20), default="ALLOW")
    alert_level     = Column(String(20), default="Safe")
    reasons         = Column(Text, nullable=True)

    timestamp       = Column(DateTime, default=datetime.utcnow)

    user            = relationship("User", back_populates="transactions")