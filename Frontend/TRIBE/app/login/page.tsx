"use client";
import "./login.css";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Login() {
  const [form, setForm] = useState({ username: "", password: "" });
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const res = await fetch("http://localhost:8000/company/company/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: form.username,
        password: form.password,
      }),
    });

    const data = await res.json();

    // If login fails
    if (!res.ok) {
      alert(data.detail || "Login failed");
      return;
    }

    // Save company ID
    localStorage.setItem("companyID", data.id);

    // Redirect to chatbots page
    router.push("/chatbot");
  };

  return (
    <div className="form-container">
      <h2>Login</h2>

      <form onSubmit={handleLogin}>
        <input
          type="text"
          placeholder="Email"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
        />

        <input
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />

        <button type="submit">Login</button>
      </form>
    </div>
  );
}
