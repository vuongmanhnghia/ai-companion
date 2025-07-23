#!/bin/bash

# Script để chạy FastAPI backend trên NixOS
# Fix lỗi libstdc++.so.6 cho Google Cloud Speech API

# Set library path cho NixOS
export LD_LIBRARY_PATH="/nix/store/7c0v0kbrrdc2cqgisi78jdqxn73n3401-gcc-14.2.1.20250322-lib/lib:$LD_LIBRARY_PATH"

# Activate virtual environment
source venv/bin/activate

# Run FastAPI with uvicorn
echo "🚀 Starting AI Companion Backend..."
echo "📍 Running on: http://127.0.0.1:8000"
echo "🔧 With LD_LIBRARY_PATH for NixOS compatibility"

uvicorn main:socket_app --host 0.0.0.0 --port 8000 --reload 