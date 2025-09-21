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

# wait for a moment before starting backend
sleep 3

#start backend
osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'/backend\" && conda activate VitalMesh && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"'

echo "✅ All services started in separate terminals!"
echo "🌐 Coral Server: http://localhost:5555"
echo "🎤 Medical Agent: Check the second terminal window"
echo "🏥 EHR Agent: Check the third terminal window"
echo ""
echo "📋 System Overview:"
echo "   • Medical Agent: Handles voice triage and patient intake"
echo "   • EHR Agent: Processes patient data into structured YAML files"
echo "   • Both agents communicate via Coral Protocol"
echo "   • Backend: FastAPI server for managing interactions and data"
echo ""
echo "🚀 VitalMesh is up and running! Ready to assist with medical triage."
echo "🔗 Access the Coral Server to monitor agent communications."
echo "🗂️ Check the backend logs for any errors or issues."
echo "💡 Remember to keep the terminal windows open to maintain service connections."