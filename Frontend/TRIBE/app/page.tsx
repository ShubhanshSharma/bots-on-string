"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center">
      <h1 className="text-4xl font-bold mb-4">Welcome to T.R.I.B.E 🤖</h1>
      <p className="text-gray-600 mb-6 max-w-xl">
        Build intelligent chatbots trained on your documents and website
        content. Start by uploading your files or chatting with your trained
        bot.
      </p>

      <div className="flex gap-4">
        <Link
          href="/train"
          className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Train Chatbot
        </Link>
        <Link
          href="/chat"
          className="bg-green-600 text-white px-5 py-2 rounded-lg hover:bg-green-700 transition"
        >
          Chat
        </Link>
      </div>
    </div>
  );
}
