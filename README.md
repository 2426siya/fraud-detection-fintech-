# fraud-detection-fintech-
🛡️ AI-Powered Real-Time Fraud Detection &amp; Payment Trust Engine built with FastAPI, Streamlit, MySQL, and RandomForest ML.
# 🛡️ TrustPay — AI-Powered Fraud Detection & Payment Trust Engine

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![ML](https://img.shields.io/badge/ML-RandomForest-purple)

## 🚀 Overview
TrustPay is a full-stack AI-powered fraud detection system that analyzes 
payment transactions in real time and assigns a risk score using a hybrid 
Rule-Based Engine + Machine Learning model. Built to simulate how real 
fintech companies like PayPal, Razorpay, and Stripe detect fraudulent 
transactions before they happen.

## ✨ Features
- 🔐 JWT Authentication (Register & Login)
- 💳 Payment Transaction Simulator
- 🤖 AI Fraud Detection using RandomForest ML Model
- 📊 Risk Scoring Engine (0-100)
- 🧠 Explainable AI — shows WHY a transaction was flagged
- 🚨 Three Alert Levels — Safe / Suspicious / Fraud
- 🗺️ Geo Anomaly Detection with live Fraud Heatmap
- 📈 Risk Trend Dashboard with charts
- ⚡ Velocity Check — detects rapid repeated transactions
- 🌍 Location Anomaly Detection

## 🎯 How It Works
Every payment goes through a 5-step AI pipeline:
1. User behavioral profile is built from transaction history
2. Rule-based engine checks for suspicious patterns
3. RandomForest ML model predicts fraud probability
4. Scores are combined into a final Risk Score (0-100)
5. Decision is made — ALLOW / OTP / BLOCK

## 🧱 Tech Stack
| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Frontend | Streamlit |
| Database | MySQL |
| ML Model | Scikit-learn RandomForest |
| Auth | JWT + bcrypt |
| ORM | SQLAlchemy |

## 📁 Project Structure
```
fraud-ai/
│
├── backend/
│   ├── main.py          ← FastAPI app entry point
│   ├── auth.py          ← JWT Authentication & password hashing
│   ├── db.py            ← MySQL database connection
│   ├── model.py         ← SQLAlchemy database models
│   ├── ml_model.py      ← RandomForest ML fraud model
│   ├── data.py          ← Pydantic request/response schemas
│   ├── payment.py       ← Core fraud detection engine
│   └── .env             ← Environment variables (DB credentials)
│
├── frontend/
│   └── app.py           ← Streamlit dashboard UI
│
├── schema.sql           ← MySQL database schema
├── requirements.txt     ← Python dependencies
├── start.bat            ← One click startup script
└── .gitignore           ← Git ignore file
```

## ⚙️ Installation & Setup

### 1. Clone the repository
git clone https://github.com/yourusername/fraud-ai.git
cd fraud-ai

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Setup MySQL database
mysql -u root -p < schema.sql

### 5. Configure environment
Edit backend/.env with your MySQL credentials

### 6. Start backend
cd backend
uvicorn main:app --reload --port 8000

### 7. Start frontend
cd frontend
streamlit run app.py

### 8. Open browser
http://localhost:8501

## 🎨 Screenshots
- 🔐 Login & Register Screen
- 💳 Payment Simulator with AI Analysis
- 📊 Risk Dashboard with Charts
- 🗺️ Fraud Heatmap

## 🔗 API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| POST | /register | Create account |
| POST | /login | Get JWT token |
| POST | /pay | Analyze payment |
| GET | /transactions | Get history |

## 🧠 ML Model Details
- Algorithm: RandomForestClassifier
- Training Data: 10,000 synthetic transactions
- Features: Amount, Time, Location, Velocity, Category
- Accuracy: ~95% on synthetic test data

## 👨‍💻 Author
Siya Kale
Built with ❤️ using FastAPI + Streamlit + Scikit-learn

## 📄 License
MIT License
