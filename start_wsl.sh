#!/bin/bash
set -e

SESSION="vitalmesh"

echo "Starting VitalMesh Medical Triage System with GNU screen..."

# Kill any existing session
screen -S $SESSION -X quit || true

# Start new detached session
screen -dmS $SESSION -t coral-server bash -c "cd \"$(pwd)/coral-server\" && CONFIG_PATH=\"../\" ./gradlew run"

# Medical Agent
screen -S $SESSION -X screen -t medical-agent bash -c "cd \"$(pwd)/agents/medical_agent\" && conda activate VitalMesh && ./run.sh"

# EHR Agent
screen -S $SESSION -X screen -t ehr-agent bash -c "cd \"$(pwd)/agents/ehr_agent\" && conda activate VitalMesh && ./run.sh main.py"

# Backend
screen -S $SESSION -X screen -t backend bash -c "cd \"$(pwd)/backend\" && conda activate VitalMesh && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# Frontend
screen -S $SESSION -X screen -t frontend bash -c "cd \"$(pwd)/frontend\" && npm run dev"

# Chatbot Agent
screen -S $SESSION -X screen -t chatbot-agent bash -c "cd \"$(pwd)/agents/chatbot_agent\" && conda activate VitalMesh && python main.py"

echo "✅ All services started inside GNU screen session: $SESSION"
echo "👉 To attach:  screen -r $SESSION"
echo "👉 To detach:  Ctrl+a d"
echo "👉 To kill session:  screen -S $SESSION -X quit"
