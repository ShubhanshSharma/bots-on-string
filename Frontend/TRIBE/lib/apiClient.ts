// lib/apiClient.ts
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

/**
 * Wrapper around fetch that automatically attaches JWT token and handles JSON response.
 */
export async function fetchClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = new Headers({
    "Content-Type": "application/json",
    ...(options.headers || {}),
  });

  // Attach token if available
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(
      `Fetch error: ${response.status} ${response.statusText} - ${errorBody}`
    );
  }

  try {
    return (await response.json()) as T;
  } catch {
    return {} as T;
  }
}

export default fetchClient;
