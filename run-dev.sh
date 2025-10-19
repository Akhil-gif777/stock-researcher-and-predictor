#!/bin/bash

# Development script to run both backend and frontend

echo "🚀 Starting Stock Research & Prediction Application..."
echo ""

# Add uv to PATH
export PATH="$HOME/.local/bin:$PATH"

# Check if .env files exist
if [ ! -f backend/.env ]; then
    echo "⚠️  Backend .env file not found. Copying from .env.example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env and add your API keys!"
    echo ""
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo ""
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "📦 Starting Backend (FastAPI)..."
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Failed to start backend. Make sure uv is installed and backend dependencies are available."
    exit 1
fi
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Frontend (Vite)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Failed to start frontend. Make sure npm dependencies are installed."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
cd ..

echo ""
echo "✅ Application started!"
echo ""
echo "📍 Backend API: http://localhost:8000"
echo "📍 Frontend UI: http://localhost:5173"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for processes
wait

