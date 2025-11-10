#!/bin/bash

# TradePal AI - Frontend Development Server Startup Script
# This script handles common issues and starts the dev server

set -e

echo "🚀 Starting TradePal AI Frontend..."
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Kill any existing Next.js processes
echo "🧹 Cleaning up existing processes..."
pkill -f "next dev" 2>/dev/null || true

# Clear Next.js cache for fresh start
if [ -d ".next" ]; then
    echo "🗑️  Clearing Next.js cache..."
    rm -rf .next
fi

echo ""
echo "✨ Starting development server..."
echo "📱 The app will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the dev server
npm run dev





