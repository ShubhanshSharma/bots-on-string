// lib/chatService.ts
import fetchClient from "./apiClient";

export interface ChatResponse {
  reply: string;
}

export interface ChatMessage {
  message: string;
  visitor_id: string;
}

/**
 * Send a message to the chatbot (dynamic or static chatbotId)
 */
export async function sendChatMessage(
  visitorId: string,
  message: string,
  chatbotId = 1 // default bot ID (can replace with dynamic)
): Promise<ChatResponse> {
  const payload = {
    visitor_anonymous_id: visitorId,
    message,
  };

  return await fetchClient<ChatResponse>(`/chat/${chatbotId}/message`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Send message and get response (used in chat UI)
 */
export const sendMessage = async (
  message: string,
  visitorId: string
): Promise<ChatResponse> => {
  const payload: ChatMessage = { message, visitor_id: visitorId };
  return await fetchClient<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
};

/**
 * Fetch chat history for a visitor
 */
export const getChatHistory = async (
  visitorId: string
): Promise<ChatMessage[]> => {
  return await fetchClient<ChatMessage[]>(`/chat/${visitorId}`, {
    method: "GET",
  });
};
