import axios from "axios";

export async function startVoiceAgent() {
  const res = await axios.post("http://localhost:8000/api/start_agent");
  return res.data;
}
