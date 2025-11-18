"use client";

import Link from "next/link";
import "./style.css";

export default function HomePage() {
  return (
    <div className="home-container">
      <h1 className="home-title">Welcome to T.R.I.B.E 🤖</h1>

      <p className="home-description">
        Build intelligent chatbots trained on your documents and website
        content. Upload your files, train your AI, and chat with it instantly.
      </p>

      <div className="home-buttons">
        <Link href="/train" className="btn btn-blue">
          🚀 Train Chatbot
        </Link>

        <Link href="/chat" className="btn btn-green">
          💬 Chat
        </Link>
      </div>
    </div>
  );
}
