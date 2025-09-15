#!/bin/bash

# Enable job control
set -m

# Function to handle cleanup
cleanup() {
    echo "Shutting down services..."
    kill -TERM $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

echo "Starting AI Career Companion services..."

# Start FastAPI backend
echo "Starting backend on port 8000..."
cd /app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "Starting frontend on port 8080..."
cd /app/static
python -m http.server 8080 --bind 0.0.0.0 &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Backend available at: http://localhost:8000"
echo "Frontend available at: http://localhost:8080"
echo "API docs at: http://localhost:8000/docs"

# Wait for either process to exit
wait $BACKEND_PID $FRONTEND_PID

# If we get here, one of the processes exited
echo "One of the services exited, shutting down..."
cleanup