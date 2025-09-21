import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api";

export async function startVoiceAgent() {
  try {
    const res = await axios.post(`${API_BASE_URL}/start_agent`, {}, {
      timeout: 10000, // 10 second timeout
    });
    return res.data;
  } catch (error) {
    console.error("Error starting voice agent:", error);
    
    if (error.response) {
      // Server responded with error status
      throw new Error(`Server error: ${error.response.data.message || error.response.statusText}`);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error("No response from server. Is the backend running?");
    } else {
      // Something else happened
      throw new Error(`Request failed: ${error.message}`);
    }
  }
}

export async function stopVoiceAgent() {
  try {
    const res = await axios.post(`${API_BASE_URL}/stop_agent`, {}, {
      timeout: 5000, // 5 second timeout
    });
    return res.data;
  } catch (error) {
    console.error("Error stopping voice agent:", error);
    
    if (error.response) {
      throw new Error(`Server error: ${error.response.data.message || error.response.statusText}`);
    } else if (error.request) {
      throw new Error("No response from server. Is the backend running?");
    } else {
      throw new Error(`Request failed: ${error.message}`);
    }
  }
}

export async function getAgentStatus() {
  try {
    const res = await axios.get(`${API_BASE_URL}/agent_status`, {
      timeout: 5000,
    });
    return res.data;
  } catch (error) {
    console.error("Error getting agent status:", error);
    return { status: "unknown", error: error.message };
  }
}