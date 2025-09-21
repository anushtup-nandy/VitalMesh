import axios from "axios";

const API_BASE = "http://localhost:8000/api"; // adjust for deployment

export async function fetchPatients() {
  const res = await axios.get(`${API_BASE}/patients`);
  return res.data.patients;
}
