"use client";

import { useState } from "react";
import apiClient from "@/lib/apiClient";
import axios from "axios";
import Loader from "@/components/Loader";

export default function TrainChatbotPage() {
  const [companyId, setCompanyId] = useState("");
  const [chatbotId, setChatbotId] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [progressMessage, setProgressMessage] = useState("");

  const handleFileUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!files || !companyId || !chatbotId) {
      alert("Please fill all required fields and select files.");
      return;
    }

    const formData = new FormData();
    formData.append("company_id", companyId);
    formData.append("chatbot_id", chatbotId);
    Array.from(files).forEach((file) => formData.append("files", file));

    setLoading(true);
    setProgressMessage("Uploading and training your chatbot...");

    try {
      await apiClient.post("/chatbot/train-files", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setProgressMessage("✅ Training complete!");
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        setProgressMessage(
          error.response?.data?.detail || "Training failed ❌"
        );
      } else {
        setProgressMessage("Unexpected error occurred ❌");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUrlTrain = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!url || !companyId || !chatbotId) {
      alert("Please fill all required fields and enter a URL.");
      return;
    }

    const formData = new FormData();
    formData.append("company_id", companyId);
    formData.append("chatbot_id", chatbotId);
    formData.append("url", url);

    setLoading(true);
    setProgressMessage("Crawling website and training chatbot...");

    try {
      await apiClient.post("/chatbot/train-url", formData);
      setProgressMessage("✅ Website training complete!");
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        setProgressMessage(
          error.response?.data?.detail || "URL training failed ❌"
        );
      } else {
        setProgressMessage("Unexpected error occurred ❌");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col items-center relative">
      {loading && <Loader message={progressMessage} />}

      <h1 className="text-3xl font-bold mb-4">Train Your Chatbot 🤖</h1>

      <div className="bg-white shadow-md rounded-xl p-6 w-full max-w-lg space-y-6">
        <div className="flex gap-4">
          <div className="w-full">
            <label
              htmlFor="companyId"
              className="block text-sm font-medium mb-1"
            >
              Company ID
            </label>
            <input
              id="companyId"
              name="companyId"
              type="number"
              placeholder="Enter Company ID"
              title="Enter Company ID"
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              className="border rounded-md p-2 w-full"
            />
          </div>

          <div className="w-full">
            <label
              htmlFor="chatbotId"
              className="block text-sm font-medium mb-1"
            >
              Chatbot ID
            </label>
            <input
              id="chatbotId"
              name="chatbotId"
              type="number"
              placeholder="Enter Chatbot ID"
              title="Enter Chatbot ID"
              value={chatbotId}
              onChange={(e) => setChatbotId(e.target.value)}
              className="border rounded-md p-2 w-full"
            />
          </div>
        </div>

        {/* --- FILE TRAINING FORM --- */}
        <form onSubmit={handleFileUpload} className="space-y-3">
          <label htmlFor="fileInput" className="block text-sm font-semibold">
            Train using files
          </label>
          <input
            id="fileInput"
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.html"
            title="Upload training files"
            onChange={(e) => setFiles(e.target.files)}
            className="block border rounded-md p-2 w-full"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white rounded-md py-2 px-4 hover:bg-blue-700"
          >
            {loading ? "Training..." : "Upload & Train"}
          </button>
        </form>

        <div className="border-t my-4"></div>

        {/* --- URL TRAINING FORM --- */}
        <form onSubmit={handleUrlTrain} className="space-y-3">
          <label htmlFor="websiteUrl" className="block text-sm font-semibold">
            Train from website URL
          </label>
          <input
            id="websiteUrl"
            type="url"
            placeholder="https://example.com"
            title="Enter website URL for training"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="border rounded-md p-2 w-full"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-green-600 text-white rounded-md py-2 px-4 hover:bg-green-700"
          >
            {loading ? "Training..." : "Crawl & Train"}
          </button>
        </form>

        {!loading && progressMessage && (
          <p className="mt-4 text-center text-gray-700 font-medium animate-pulse">
            {progressMessage}
          </p>
        )}
      </div>
    </div>
  );
}
