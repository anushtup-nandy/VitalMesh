from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import yaml

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

