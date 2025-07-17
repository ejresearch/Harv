#!/bin/bash
echo "🚀 Starting Harv Platform Backend..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
