#!/bin/bash

# Ensure Redis is running (if running Docker locally)
echo "Starting Redis..."
docker run --name redis -p 6379:6379 -d redis:latest

# Activate virtual environment if needed
echo "Activating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI application using Uvicorn
echo "Starting FastAPI server..."
python3 app_uc/main.py       