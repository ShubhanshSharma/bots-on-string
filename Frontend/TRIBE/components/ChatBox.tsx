"use client";

import React, { useState } from "react";
import MessageBubble, { Message } from "./MessageBubble";
import { sendChatMessage } from "@/lib/chatService";
import Loader from "./Loader";

interface ChatBoxProps {
  visitorId: string;
}

const ChatBox: React.FC<ChatBoxProps> = ({ visitorId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      sender: "You",
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // ✅ Pass visitorId and message
      const data = await sendChatMessage(visitorId, input);

      const botMessage: Message = {
        id: crypto.randomUUID(),
        sender: "Bot",
        text: data.reply,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 flex flex-col h-full">
      <div className="flex-1 overflow-y-auto">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {loading && <Loader />}
      </div>
      <div className="mt-4 flex">
        <input
          className="flex-1 border p-2 rounded"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button
          onClick={handleSend}
          className="ml-2 bg-blue-500 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
