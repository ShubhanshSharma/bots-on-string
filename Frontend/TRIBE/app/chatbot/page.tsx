"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import "./chatbot.css";

type Chatbot = {
  id: number;
  name: string;
  description: string;
  company_id: number;
};

export default function CreateChatbotPage() {
  const router = useRouter();

  const [chatbots, setChatbots] = useState([]);
  const [loading, setLoading] = useState(true);

  const goToTrain = () => {
    router.push("/train");
  };

  useEffect(() => {
    const fetchChatbots = async () => {
      try {
        const companyId = localStorage.getItem("company_id");
        if (!companyId) {
          setLoading(false);
          return;
        }

        const res = await fetch("http://localhost:8000/chatbot/chatbot");
        const data = await res.json();

        // Filter the chatbots by company_id
        const filtered = data.filter(
          (cb: any) => cb.company_id === parseInt(companyId)
        );

        setChatbots(filtered);
      } catch (error) {
        console.error("Failed to load chatbots:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchChatbots();
  }, []);

  return (
    <div className="page-container">
      <h1 className="page-title">Chatbot Setup 🤖</h1>

      <div className="card">
        <h2 className="section-title">Your Chatbots</h2>

        {loading ? (
          <p className="loading-text">Loading chatbots...</p>
        ) : chatbots.length === 0 ? (
          <p className="empty-text">No chatbots found for your company.</p>
        ) : (
          <ul className="chatbot-list">
            {chatbots.map((bot: any) => (
              <li key={bot.id} className="chatbot-item">
                <strong>{bot.name}</strong>
                <p className="chatbot-description">{bot.description}</p>
              </li>
            ))}
          </ul>
        )}

        <button className="train-button" onClick={goToTrain}>
          Go to Training Page
        </button>
      </div>
    </div>
  );
}
