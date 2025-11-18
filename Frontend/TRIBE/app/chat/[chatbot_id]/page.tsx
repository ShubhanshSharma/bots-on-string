"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import fetchClient from "@/lib/apiClient";
import MessageBubble from "@/components/MessageBubble";
import Loader from "@/components/Loader";
import TypingDots from "@/components/TypingDots";
import "../style.css";

interface Message {
  id: string;
  sender: "You" | "Bot";
  text: string;
}

interface ContextItem {
  query: string;
  answer: string;
}

export default function ChatPage() {
  const params = useParams();
  const chatbotId = params.chatbot_id as string; // ← READ ROUTE PARAM HERE

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatContext, setChatContext] = useState<ContextItem[]>([]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "You",
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentQuery = input;

    setInput("");
    setLoading(true);

    try {
      const data = await fetchClient<{ reply: string }>(
        `/chat/chat/${chatbotId}/ollamaTesting`,
        {
          method: "POST",
          body: JSON.stringify({
            chatbotId,
            message: currentQuery,
            context: chatContext,
          }),
        }
      );

      const botResponse = data.reply || "🤖 No response received.";

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "Bot",
        text: botResponse,
      };

      setMessages((prev) => [...prev, botMessage]);

      // store last 3 context items
      setChatContext((prev) =>
        [...prev, { query: currentQuery, answer: botResponse }].slice(-3)
      );
    } catch (error) {
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
    <div className="chat-page">
      <div className="chat-container">
        <h1 className="chat-title">Chat with Your AI Bot 🤖</h1>

        {/* Show chatbot ID */}
        <p className="chatbot-id-display">Chatbot ID: {chatbotId}</p>

        <div className="chat-window">
          {messages.length === 0 && (
            <p className="chat-placeholder">👋 Start chatting with your bot!</p>
          )}

          {messages.map((msg) => (
            <MessageBubble key={msg.id} sender={msg.sender} text={msg.text} />
          ))}

          {loading && (
            <div className="typing-indicator">
              <TypingDots />
            </div>
          )}

          <div ref={chatEndRef}></div>
        </div>

        <form onSubmit={sendMessage} className="chat-input-bar">
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" disabled={loading}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
