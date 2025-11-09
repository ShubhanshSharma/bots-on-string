"use client";

interface MessageBubbleProps {
  sender: "You" | "Bot";
  text: string;
}

export default function MessageBubble({ sender, text }: MessageBubbleProps) {
  const isUser = sender === "You";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} my-2`}>
      <div
        className={`max-w-[75%] px-4 py-2 rounded-2xl shadow-md ${
          isUser
            ? "bg-blue-600 text-white rounded-br-none"
            : "bg-gray-200 text-gray-800 rounded-bl-none"
        }`}
      >
        <p className="text-sm whitespace-pre-line">{text}</p>
        <span className="block text-xs mt-1 opacity-70">
          {isUser ? "You" : "Bot"}
        </span>
      </div>
    </div>
  );
}
