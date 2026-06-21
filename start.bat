@echo off
echo =========================================
echo Starting Synapse Cognitive Engine...
echo =========================================

echo.
echo [1/2] Starting FastAPI Backend on port 8000...
start "Synapse Backend" cmd /k "python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo [2/2] Starting React Frontend...
start "Synapse Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo All services have been launched in separate windows!
echo - Backend API: http://127.0.0.1:8000
echo - MindSentry UI: http://127.0.0.1:8000/mindsentry/index.html
echo - React Dashboard: Usually http://localhost:5173 (Check the frontend window)
echo.
pause
