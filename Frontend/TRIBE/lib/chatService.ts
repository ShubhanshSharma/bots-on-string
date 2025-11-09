// lib/chatService.ts
import { api } from "./apiClient";
import apiClient from "./apiClient";

export interface ChatResponse {
  reply: string;
}

export interface ChatMessage {
  message: string;
  visitor_id: string;
}

export async function sendChatMessage(visitorId: string, message: string) {
  try {
    const chatbotId = 1; // ⚙️ temporary static bot ID
    const response = await apiClient.post(`/chat/${chatbotId}/message`, {
      visitor_anonymous_id: visitorId,
      message,
    });
    return response.data;
  } catch (err: unknown) {
    console.error("Error sending chat message:", err);
    throw err;
  }
}

export const sendMessage = async (message: string, visitorId: string) => {
  const payload: ChatMessage = { message, visitor_id: visitorId };
  const res = await api.post("/api/v1/chat", payload);
  return res.data;
};

export const getChatHistory = async (visitorId: string) => {
  const res = await api.get(`/api/v1/chat/${visitorId}`);
  return res.data;
};
