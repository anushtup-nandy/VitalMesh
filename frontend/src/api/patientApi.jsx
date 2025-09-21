import axios from "axios";

const API_BASE = "http://localhost:8000/api"; // FastAPI default

export async function fetchPatient(patientId) {
  try {
    const response = await axios.get(`${API_BASE}/patient/${patientId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching patient:", error);
    throw error;
  }
}
