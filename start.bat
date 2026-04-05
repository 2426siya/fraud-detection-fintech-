@echo off
echo Starting TrustPay Fraud Detection System...
echo.

cd C:\Users\Sunil Kale\fraud-ai
call venv\Scripts\activate

echo Starting Backend...
start cmd /k "cd C:\Users\Sunil Kale\fraud-ai && venv\Scripts\activate && cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3

echo Starting Frontend...
start cmd /k "cd C:\Users\Sunil Kale\fraud-ai && venv\Scripts\activate && cd frontend && streamlit run app.py"

echo.
echo Both servers are starting...
echo Backend  → http://localhost:8000
echo Frontend → http://localhost:8501
echo.
pause