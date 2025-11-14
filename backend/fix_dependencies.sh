#!/bin/bash

# Fix Dependencies Script for TradePal AI Backend
# Fixes architecture mismatch issue on Apple Silicon

set -e

echo "🔧 Fixing dependency architecture mismatch..."
echo ""

cd "$(dirname "$0")"

# Remove old virtual environment
if [ -d "venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "📦 Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Dependencies fixed!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the backend, run:"
echo "  python main.py"


