#!/bin/bash

# Medical Agent System Runner
echo "🏥 Starting Medical Agent System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys"
    exit 1
fi

# Check if directories exist
if [ ! -d "patient_data" ] || [ ! -d "prompts" ]; then
    echo "📁 Setting up directories and prompts..."
    python setup.py
fi

# Check if Coral server is running
echo "🔍 Checking Coral server connection..."
if curl -s http://localhost:5555/health > /dev/null; then
    echo "✅ Coral server is running"
else
    echo "❌ Coral server not found at localhost:5555"
    echo "Please start your Coral server first"
    exit 1
fi

# Start the medical agent
echo "🚀 Starting Medical Agent System..."
python medical_agent.py console

echo "👋 Medical Agent System stopped"