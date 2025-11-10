"use client";

import { useEffect, useRef, useState } from "react";
import fetchClient from "@/lib/apiClient";
import MessageBubble from "@/components/MessageBubble";
import Loader from "@/components/Loader";

interface Message {
  id: string;
  sender: "You" | "Bot";
  text: string;
}

export default function ChatPage() {
  const [chatbotId, setChatbotId] = useState("");
  const [companyId, setCompanyId] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ---- SEND MESSAGE ----
  const sendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || !chatbotId || !companyId) {
      alert("Please fill Chatbot ID, Company ID, and your message.");
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "You",
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // ✅ Correct fetch usage (no .post)
      const data = await fetchClient<{ answer: string }>(
        `/chatbot/chatbot/${chatbotId}/query`,
        {
          method: "POST",
          body: JSON.stringify({
            company_id: companyId,
            query: userMessage.text,
          }),
        }
      );

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "Bot",
        text: data.answer || "🤖 No response received.",
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error: unknown) {
      console.error("Chat error:", error);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          sender: "Bot",
          text: "⚠️ Something went wrong while chatting.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center">
      {loading && <Loader message="Bot is thinking..." />}

      <div className="w-full max-w-2xl mt-10 bg-white rounded-xl shadow-lg p-4 flex flex-col h-[80vh]">
        <h1 className="text-2xl font-bold mb-4 text-center text-blue-700">
          Chat with Your AI Bot 🤖
        </h1>

        {/* IDs input */}
        <div className="flex gap-4 mb-4">
          <input
            type="number"
            placeholder="Company ID"
            value={companyId}
            onChange={(e) => setCompanyId(e.target.value)}
            className="border rounded-md p-2 w-full"
          />
          <input
            type="number"
            placeholder="Chatbot ID"
            value={chatbotId}
            onChange={(e) => setChatbotId(e.target.value)}
            className="border rounded-md p-2 w-full"
          />
        </div>

        {/* Chat Window */}
        <div className="flex-1 overflow-y-auto border rounded-md p-3 bg-gray-50">
          {messages.length === 0 && (
            <p className="text-gray-400 text-center mt-10">
              👋 Start chatting with your trained chatbot!
            </p>
          )}
          {messages.map((msg) => (
            <MessageBubble key={msg.id} sender={msg.sender} text={msg.text} />
          ))}
          <div ref={chatEndRef}></div>
        </div>

        {/* Input Box */}
        <form onSubmit={sendMessage} className="mt-4 flex gap-2">
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="border rounded-md p-2 flex-1"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white rounded-md px-4 hover:bg-blue-700"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
