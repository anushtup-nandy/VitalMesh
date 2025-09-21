# <project-root>/backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import yaml
import os
import subprocess
from fastapi import BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# CORS so frontend can fetch from backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import the chatbot class
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "agents" / "chatbot_agent"))

# Import with a different module name to avoid circular import
import importlib.util
chatbot_spec = importlib.util.spec_from_file_location(
    "chatbot_main", 
    Path(__file__).resolve().parent.parent.parent / "agents" / "chatbot_agent" / "main.py"
)
chatbot_module = importlib.util.module_from_spec(chatbot_spec)
chatbot_spec.loader.exec_module(chatbot_module)
MedicalChatbot = chatbot_module.MedicalChatbot

print("chatbot module loaded :", chatbot_spec)

# Initialize chatbot instance
chatbot_instance = None

def get_chatbot():
    global chatbot_instance
    if chatbot_instance is None:
        try:
            # ADD DEBUG INFO
            api_key = os.getenv("API_KEY")
            if not api_key:
                print("❌ ERROR: API_KEY environment variable not found!")
                return None
            
            print(f"✅ API_KEY found: {api_key[:10]}...")
            print(f"✅ LLM_MODEL: {os.getenv('LLM_MODEL', 'llama-3.1-8b-instant')}")
            
            chatbot_instance = MedicalChatbot()
            print(f"✅ Chatbot initialized successfully with {len(chatbot_instance.patient_data)} patients")
        except Exception as e:
            print(f"❌ Failed to initialize chatbot: {e}")
            import traceback
            traceback.print_exc()
            return None
    return chatbot_instance

# Rest of your code remains the same...
EHR_OUTPUTS_DIR = Path(__file__).resolve().parent.parent.parent / "agents" / "ehr_agent" / "ehr_outputs"

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

@app.get("/api/patient/{patient_id}")
def get_patient(patient_id: str):
    yaml_path = EHR_OUTPUTS_DIR / f"{patient_id}.yaml"
    if not yaml_path.exists():
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing YAML: {e}")

    return data

@app.get("/api/patients")
def get_all_patients():
    patients = []
    for yaml_file in EHR_OUTPUTS_DIR.glob("*.yaml"):
        try:
            with open(yaml_file, "r") as f:
                data = yaml.safe_load(f)
            patient_id = yaml_file.stem
            patients.append({"id": patient_id, **data})
        except yaml.YAMLError as e:
            print(f"⚠️ Error parsing {yaml_file.name}: {e}")
            # skip this file
            continue

    return {"patients": patients}

PATIENT_NOTES_DIR = Path(__file__).resolve().parent.parent.parent / "agents" / "medical_agent" / "patient_notes"

@app.get("/api/latest_note")
def get_latest_note():
    if not PATIENT_NOTES_DIR.exists():
        raise HTTPException(status_code=404, detail="Notes directory not found")

    yaml_files = list(PATIENT_NOTES_DIR.glob("*.yaml"))
    if not yaml_files:
        raise HTTPException(status_code=404, detail="No patient notes found")

    # Pick the most recently modified file
    latest_file = max(yaml_files, key=os.path.getmtime)

    with open(latest_file, "r") as f:
        data = yaml.safe_load(f)

    sessions = data.get("sessions", [])
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions in notes")

    latest_session = sessions[-1]  # last session in the list
    return {
        "patient_name": latest_session.get("patient_name"),
        "chief_complaint": latest_session.get("chief_complaint"),
        "symptoms": latest_session.get("symptoms", []),
    }


@app.post("/api/start_agent")
def start_agent(background_tasks: BackgroundTasks):
    """Start the voice agent in a new terminal."""
    # Get the project root directory (where main.py backend is located)
    project_root = Path(__file__).resolve().parent.parent.parent
    medical_agent_path = project_root / "agents" / "medical_agent"
    
    # Ensure the path exists
    if not medical_agent_path.exists():
        raise HTTPException(status_code=404, detail=f"Medical agent directory not found: {medical_agent_path}")
    
    command = f'osascript -e \'tell application "Terminal" to do script "cd \\"{medical_agent_path}\\" && conda activate VitalMesh && ./run.sh"\''
    
    def run_agent():
        subprocess.run(command, shell=True, executable="/bin/bash")
    
    background_tasks.add_task(run_agent)
    return {"status": "starting"}

@app.post("/api/stop_agent")
def stop_agent():
    """Stop the voice agent by closing the terminal."""
    # Kill any python processes running the medical agent
    command = 'pkill -f "medical_agent"'
    subprocess.run(command, shell=True)
    
    # Also try to close the terminal window - look for more specific process names
    close_command = 'osascript -e \'tell application "Terminal" to close (every window whose name contains "run.sh")\''
    subprocess.run(close_command, shell=True, stderr=subprocess.DEVNULL)
    
    return {"status": "stopped"}

# New chatbot endpoints
@app.post("/api/chatbot/message", response_model=ChatResponse)
def send_message(message: ChatMessage):
    """Send a message to the medical chatbot and get a response."""
    try:
        chatbot = get_chatbot()
        if chatbot is None:
            return ChatResponse(
                response="Sorry, the chatbot is currently unavailable. Please check your API configuration and ensure API_KEY environment variable is set.",
                success=False,
                error="Chatbot initialization failed"
            )
        
        response = chatbot.chat(message.message)
        return ChatResponse(response=response, success=True)
    
    except Exception as e:
        return ChatResponse(
            response="An error occurred while processing your message.",
            success=False,
            error=str(e)
        )

@app.post("/api/chatbot/refresh")
def refresh_chatbot_data():
    """Refresh the chatbot's patient data."""
    try:
        chatbot = get_chatbot()
        if chatbot is None:
            raise HTTPException(status_code=500, detail="Chatbot not available")
        
        chatbot.refresh_data()
        patient_count = len(chatbot.patient_data)
        return {"status": "success", "message": f"Data refreshed! Now tracking {patient_count} patients."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh data: {str(e)}")

@app.get("/api/chatbot/status")
def get_chatbot_status():
    """Get the current status of the chatbot."""
    try:
        chatbot = get_chatbot()
        if chatbot is None:
            return {"status": "unavailable", "patient_count": 0, "error": "Chatbot initialization failed - check API_KEY"}
        
        return {
            "status": "available",
            "patient_count": len(chatbot.patient_data),
            "model": chatbot.llm_model
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "patient_count": 0}