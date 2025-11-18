const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export interface Chatbot {
  id?: number;
  name: string;
  description?: string;
  company_id: number;
}

export interface QueryResponse {
  answer: string;
}

/** Helper for JSON requests */
async function fetchClient<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      ...(options?.body instanceof FormData
        ? {}
        : { "Content-Type": "application/json" }),
    },
    ...options,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`HTTP ${res.status}: ${errorText}`);
  }

  return res.json() as Promise<T>;
}

/** Create a new chatbot */
export async function createChatbot(data: Chatbot): Promise<Chatbot> {
  return await fetchClient<Chatbot>("/chatbot/chatbot/create", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/** Train chatbot using uploaded files */
export async function trainChatbotWithFiles(
  companyId: number,
  chatbotId: number,
  files: FileList
): Promise<{ message: string }> {
  const formData = new FormData();
  formData.append("company_id", companyId.toString());
  formData.append("chatbot_id", chatbotId.toString());
  Array.from(files).forEach((file) => formData.append("files", file));

  const res = await fetch(`${API_BASE_URL}/chatbot/chatbot/train-files`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`HTTP ${res.status}: ${errorText}`);
  }
  return res.json();
}

/** Train chatbot using website URL */
export async function trainChatbotWithUrl(
  companyId: number,
  chatbotId: number,
  url: string
): Promise<{ message: string }> {
  const formData = new FormData();
  formData.append("company_id", companyId.toString());
  formData.append("chatbot_id", chatbotId.toString());
  formData.append("url", url);

  const res = await fetch(`${API_BASE_URL}/chatbot/chatbot/train-url`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`HTTP ${res.status}: ${errorText}`);
  }
  return res.json();
}

/** Query chatbot */
export async function queryChatbot(
  companyId: number,
  chatbotId: number,
  query: string
): Promise<QueryResponse> {
  return await fetchClient<QueryResponse>(
    `/chatbot/chatbot/${chatbotId}/query`,
    {
      method: "POST",
      body: JSON.stringify({
        company_id: companyId,
        chatbotId: chatbotId,
        query,
      }),
    }
  );
}
