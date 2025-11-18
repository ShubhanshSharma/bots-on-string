# app/services/ollama_service.py

import os
import httpx
from app.services.qdrant_service import search_similar_vectors
from app.services.qdrant_service import retrieve_chunks

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.2")  # change to the model you pulled via `ollama pull`


# chat history
def build_chat_history(history: list[dict]) -> str:
    if not history:
        return "No previous messages."

    formatted = []
    for item in history:
        formatted.append(f"User: {item['query']}")
        formatted.append(f"Bot: {item['answer']}")

    return "\n".join(formatted)


async def generate_reply(message: str, chatbot_id: str, history: list[dict]):

    print("🔵 OLLAMA_URL =", OLLAMA_URL)

    # 1️⃣ Retrieve relevant context from Qdrant
    user_message = message
    chunks = retrieve_chunks(user_message, chatbot_id)

    context = (
        "No knowledge base found for this chatbot."
        if not chunks else "\n\n".join(chunks)
    )

    chat_history = build_chat_history(history)

    # 2️⃣ Build prompt
    prompt = [
        {
            "role": "system",
            "content": (
                "You are a helpful company assistant.\n"
                "Use the provided knowledge-base context when answering factual questions.\n"
                "If the user's message is conversational (like 'ok', 'thanks', 'yes', 'continue', etc.), "
                "respond naturally without requiring context.\n"
                "If the user asks a factual question and the answer is NOT found in the knowledge context, reply:\n"
                "'I don’t have information about that.'\n"
                "Never invent facts.\n"
                "Keep responses clear, concise, friendly, and conversational."
            )
        },
        {
            "role": "user",
            "content": (
                f"Knowledge Base Context:\n{context}\n\n"
                f"Conversation History:\n{chat_history}\n\n"
                f"User question: {user_message}"
            )
        }
    ]

    # 3️⃣ Call Ollama
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": LLM_MODEL,
                "messages": prompt,
                "stream": False
            }
        )

    data = response.json()
    print("🔥 OLLAMA RAW RESPONSE:", data)

    # 4️⃣ Handle different Ollama response formats safely
    if "message" in data:
        return data["message"]["content"]

    if "messages" in data and isinstance(data["messages"], list):
        return data["messages"][-1]["content"]

    if "response" in data:
        return data["response"]

    return "⚠️ Could not read response from Ollama."
