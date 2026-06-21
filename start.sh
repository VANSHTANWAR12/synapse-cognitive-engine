#!/bin/bash
echo "========================================="
echo "Starting Synapse Cognitive Engine..."
echo "========================================="

# Trap SIGINT (Ctrl+C) and kill child processes
trap 'echo -e "\nStopping services..."; kill 0' SIGINT

echo -e "\n[1/2] Starting FastAPI Backend on port 8000..."
python -m uvicorn backend:app --host 127.0.0.1 --port 8000 &

echo -e "\n[2/2] Starting React Frontend..."
cd frontend && npm run dev &

echo -e "\nAll services have been launched!"
echo "- Backend API: http://127.0.0.1:8000"
echo "- MindSentry UI: http://127.0.0.1:8000/mindsentry/index.html"
echo "- React Dashboard: Usually http://localhost:5173"
echo -e "\nPress Ctrl+C to stop all services."

# Wait for background processes to finish
wait
