#!/usr/bin/env bash

# ==============================================================================
# Network Intrusion Detection System (Review 3) - Unified Application Launcher
# ==============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Ensure user-space Node is in PATH
export PATH="$HOME/.local/node/bin:$PATH"

# Identify Python Virtual Environment
VENV_PYTHON=""
if [ -f "$PROJECT_ROOT/../BD_Review3/venv/bin/python" ]; then
    VENV_PYTHON="$PROJECT_ROOT/../BD_Review3/venv/bin/python"
elif [ -f "$PROJECT_ROOT/venv/bin/python" ]; then
    VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    VENV_PYTHON="$(command -v python3)"
fi

echo "========================================================================"
echo " Starting Network Intrusion Detection System (NSL-KDD Review 3)"
echo "========================================================================"
echo " Project Directory : $PROJECT_ROOT"
echo " Python Runtime    : $VENV_PYTHON"
echo " Node.js Runtime   : $(which node 2>/dev/null || echo 'Not in PATH')"
echo "========================================================================"

# Check MongoDB status
if nc -z localhost 27017 2>/dev/null || timeout 1 bash -c "</dev/tcp/localhost/27017" 2>/dev/null; then
    echo "[Database] MongoDB is running on port 27017 (Primary storage active)."
else
    echo "[Database] MongoDB is offline. Local persistent JSON store will be used."
fi

echo ""
echo "[1/2] Starting FastAPI Backend (Apache Spark MLlib Engine)..."
"$VENV_PYTHON" -m uvicorn api.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID 2>/dev/null || true
    wait $FRONTEND_PID 2>/dev/null || true
    echo "Application stopped."
    exit 0
}

trap cleanup INT TERM

# Wait for backend to initialize
sleep 4

echo ""
echo "[2/2] Starting React Frontend (Vite)..."
cd "$PROJECT_ROOT/frontend"
npm run dev -- --host 127.0.0.1 --port 5173 &
FRONTEND_PID=$!

echo ""
echo "========================================================================"
echo " Full-Stack Application is running!"
echo " 👉 Web Application : http://127.0.0.1:5173"
echo " 👉 Backend API Docs: http://127.0.0.1:8000/docs"
echo " Press Ctrl+C to stop all services."
echo "========================================================================"

wait
