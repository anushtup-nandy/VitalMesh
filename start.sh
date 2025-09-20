#!/bin/bash

# Exit on error
set -e

echo "Starting VitalMesh Medical Triage System..."

# Start Coral Server in new terminal
osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'/coral-server\" && CONFIG_PATH=\"../\" ./gradlew run"'

# Wait a bit for server to start
echo "Waiting 8 seconds for Coral Server to start..."
sleep 8

# Start Medical Triage Agent in new terminal  
osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'/agents/medical_agent\" && conda activate VitalMesh && ./run.sh"'

# Wait a moment before starting EHR agent
sleep 3

# Start EHR Agent in new terminal
osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'/agents/ehr_agent\" && conda activate VitalMesh && ./run.sh main.py"'

echo "✅ All services started in separate terminals!"
echo "🌐 Coral Server: http://localhost:5555"
echo "🎤 Medical Agent: Check the second terminal window"
echo "🏥 EHR Agent: Check the third terminal window"
echo ""
echo "📋 System Overview:"
echo "   • Medical Agent: Handles voice triage and patient intake"
echo "   • EHR Agent: Processes patient data into structured YAML files"
echo "   • Both agents communicate via Coral Protocol"