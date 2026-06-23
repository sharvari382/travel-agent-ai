import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export interface ChatResponse {
  session_id: string;
  reply: string;
}

export async function sendMessage(message: string, sessionId: string | null) {
  const res = await axios.post<ChatResponse>(`${API_BASE}/chat`, {
    message,
    session_id: sessionId,
  });
  return res.data;
}

export async function listSessions() {
  const res = await axios.get(`${API_BASE}/sessions`);
  return res.data;
}

export async function getSession(sessionId: string) {
  const res = await axios.get(`${API_BASE}/sessions/${sessionId}`);
  return res.data;
}
