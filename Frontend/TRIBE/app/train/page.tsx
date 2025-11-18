"use client";

import { useEffect, useState } from "react";
import Loader from "@/components/Loader";
import "./style.css";
import { useRouter } from "next/navigation";

export default function TrainChatbotPage() {
  const router = useRouter();

  const [companyId, setCompanyId] = useState("");
  const [chatName, setChatName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [progressMessage, setProgressMessage] = useState("");

  const MAX_PDF_SIZE_MB = 5;
  const MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024;

  useEffect(() => {
    const stored = localStorage.getItem("companyID");
    setCompanyId(stored || "");
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!chatName) return alert(" Chat name required.");
    if (!file) return alert("Please upload a PDF file.");

    setLoading(true);
    setProgressMessage("Uploading PDF...");

    try {
      const BASE_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

      const formData = new FormData();
      formData.append("file", file);
      formData.append("companyId", companyId);
      formData.append("chatName", chatName);

      const res = await fetch(`${BASE_URL}/upload/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();
      setProgressMessage("✅ PDF uploaded and text extracted!");

      // 🚀 Redirect to /chat/{chatbot_id}
      if (data.chatbot_id) {
        router.push(`/chat/${data.chatbot_id}`);
      }
    } catch (error) {
      console.error(error);
      setProgressMessage("❌ Failed to upload.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploaded = e.target.files?.[0];
    if (!uploaded) return;

    if (uploaded.type !== "application/pdf")
      return alert("Only PDF files allowed.");

    if (uploaded.size > MAX_PDF_SIZE_BYTES)
      return alert(`PDF cannot exceed ${MAX_PDF_SIZE_MB} MB.`);

    setFile(uploaded);
  };

  return (
    <div className="train-page-container">
      {loading && <Loader message={progressMessage} />}

      <div className="train-card">
        <h1 className="train-title">📄 Train Chatbot with PDF</h1>

        <form onSubmit={handleSubmit} className="train-form">
          {/* <div>
            <label>Company ID</label>
            <input
              placeholder="Enter your company ID"
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
            />
          </div> */}

          <div>
            <label>Chat Name</label>
            <input
              placeholder="Enter your chat Name"
              value={chatName}
              onChange={(e) => setChatName(e.target.value)}
            />
          </div>

          <div>
            <label htmlFor="file">Upload PDF (max {MAX_PDF_SIZE_MB}MB)</label>
            <input
              id="file"
              type="file"
              accept="application/pdf"
              onChange={handleFileSelect}
            />

            {file && (
              <p className="selected-file">
                Selected: <strong>{file.name}</strong>
              </p>
            )}
          </div>

          <button type="submit" disabled={loading} className="train-submit">
            {loading ? "Uploading..." : "Upload PDF"}
          </button>
        </form>

        {!loading && progressMessage && (
          <p className="train-message">{progressMessage}</p>
        )}
      </div>
    </div>
  );
}
