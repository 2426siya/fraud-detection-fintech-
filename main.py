"""
Adaptive AI-Powered Fraud Detection & Payment Trust Engine
Backend Entry Point - FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from payment import router as payment_router
from db import engine, Base

# ─── Initialize Tables ───────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── App Instance ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Fraud Detection & Payment Trust Engine",
    description="AI-powered real-time fraud detection for payment transactions",
    version="1.0.0"
)

# ─── CORS Middleware ──────────────────────────────────────────────────────────
# Allow Streamlit frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # In production, replace with exact frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Route Registration ───────────────────────────────────────────────────────
app.include_router(auth_router, tags=["Authentication"])
app.include_router(payment_router, tags=["Payments"])


@app.get("/", tags=["Health"])
def health_check():
    """Root endpoint to verify the API is running."""
    return {"status": "online", "service": "Fraud Detection Engine v1.0"}