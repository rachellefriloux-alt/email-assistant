#!/bin/bash
set -euo pipefail

echo "Starting Gmail Email Assistant..."

cd "$(dirname "$0")"

cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload &

cd ../frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
