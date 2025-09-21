// <project-root>/frontend/src/api/chatbot.jsx
import axios from "axios";

const API_BASE = "http://localhost:8000/api"; // FastAPI default

export async function sendChatMessage(message) {
  try {
    const response = await axios.post(`${API_BASE}/chatbot/message`, {
      message,
    });
    return response.data;
  } catch (error) {
    console.error("Error sending chat message:", error);
    throw error;
  }
}

export async function refreshChatbotData() {
  try {
    const response = await axios.post(`${API_BASE}/chatbot/refresh`);
    return response.data;
  } catch (error) {
    console.error("Error refreshing chatbot data:", error);
    throw error;
  }
}

export async function getChatbotStatus() {
  try {
    const response = await axios.get(`${API_BASE}/chatbot/status`);
    return response.data;
  } catch (error) {
    console.error("Error getting chatbot status:", error);
    throw error;
  }
}