#!/bin/bash
# Development server for Soul Mirror React frontend

cd "$(dirname "$0")/.."

echo "🚀 Starting Soul Mirror frontend development server..."
echo "📍 Server will be available at: http://localhost:3000"
echo "🔌 Backend API expected at: http://localhost:8080"
echo ""

npm run dev
