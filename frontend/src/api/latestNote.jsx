import axios from "axios";

export async function fetchLatestNote() {
  const res = await axios.get("http://localhost:8000/api/latest_note");
  return res.data;
}
