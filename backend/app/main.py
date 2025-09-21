from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import yaml
import os
import subprocess
from fastapi import BackgroundTasks

app = FastAPI()

# CORS so frontend can fetch from backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EHR_OUTPUTS_DIR = Path(__file__).resolve().parent.parent.parent / "agents" / "ehr_agent" / "ehr_outputs"

# print("Looking for YAMLs in:", EHR_OUTPUTS_DIR)
# if not EHR_OUTPUTS_DIR.exists():
#     print("❌ Directory does not exist!")
# else:
#     files = list(EHR_OUTPUTS_DIR.glob("*.yaml"))
#     if not files:
#         print("⚠️ No YAML files found")
#     else:
#         print("✅ Found YAML files:", [f.name for f in files])


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
            print(f"❌ Error parsing {yaml_file.name}: {e}")
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
    command = f'osascript -e \'tell application "Terminal" to do script "cd \\"$(pwd)/agents/medical_agent\\" && conda activate VitalMesh && ./run.sh"\''
    
    def run_agent():
        subprocess.run(command, shell=True, executable="/bin/bash")
    
    background_tasks.add_task(run_agent)
    return {"status": "starting"}
