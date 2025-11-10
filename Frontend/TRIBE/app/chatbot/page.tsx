"use client";

import { useState } from "react";
import { createChatbot } from "@/lib/chatBotService";

export default function CreateChatbotPage() {
  const [companyId, setCompanyId] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!companyId || !name) {
      alert("Please fill in Company ID and Chatbot Name");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const chatbot = await createChatbot({
        company_id: parseInt(companyId),
        name,
        description,
      });
      setMessage(`✅ Chatbot created successfully! ID: ${chatbot.id}`);
    } catch (error) {
      console.error(error);
      setMessage("❌ Failed to create chatbot");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-6">Create a Chatbot 🤖</h1>

      <form
        onSubmit={handleSubmit}
        className="bg-white p-6 rounded-xl shadow-md w-full max-w-md space-y-4"
      >
        <div>
          <label className="block text-sm font-medium mb-1">Company ID</label>
          <input
            type="number"
            placeholder="Enter Company ID"
            value={companyId}
            onChange={(e) => setCompanyId(e.target.value)}
            className="border rounded-md p-2 w-full"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Chatbot Name</label>
          <input
            type="text"
            placeholder="Enter chatbot name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="border rounded-md p-2 w-full"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea
            placeholder="Enter chatbot description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="border rounded-md p-2 w-full"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white w-full py-2 rounded-md hover:bg-blue-700"
        >
          {loading ? "Creating..." : "Create Chatbot"}
        </button>
      </form>

      {message && (
        <p className="mt-4 text-center text-gray-700 font-medium">{message}</p>
      )}
    </div>
  );
}
