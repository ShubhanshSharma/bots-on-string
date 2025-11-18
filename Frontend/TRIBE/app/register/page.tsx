"use client";
import "./register.css";
import { useState } from "react";

export default function Register() {
  const [form, setForm] = useState({
    company_name: "",
    company_email: "",
    password: "",
    confirm_password: "",
    description: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [message, setMessage] = useState("");

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Frontend validations
    if (
      !form.company_name ||
      !form.company_email ||
      !form.password ||
      !form.confirm_password
    ) {
      setMessage("Please fill all required fields.");
      return;
    }

    if (form.password !== form.confirm_password) {
      setMessage("Passwords do not match.");
      return;
    }

    const registerData = {
      name: form.company_name,
      email: form.company_email,
      password: form.password,
      description: form.description,
    };

    // 🔥 Updated API route
    const res = await fetch("http://localhost:8000/company/company/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(registerData),
    });

    const data = await res.json();
    setMessage(data.message || data.detail || "Registered successfully");
  };

  const passwordsMatch =
    form.password.length > 0 &&
    form.confirm_password.length > 0 &&
    form.password === form.confirm_password;

  return (
    <div className="form-container">
      <h2>Register</h2>

      <form onSubmit={handleRegister}>
        <input
          type="text"
          placeholder="Company Name *"
          value={form.company_name}
          onChange={(e) => setForm({ ...form, company_name: e.target.value })}
        />

        <input
          type="email"
          placeholder="Company Email *"
          value={form.company_email}
          onChange={(e) => setForm({ ...form, company_email: e.target.value })}
        />

        {/* Password Field */}
        <div className="password-container">
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password *"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          <span
            className="toggle-visibility"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? "Hide" : "Show"}
          </span>
        </div>

        {/* Confirm Password Field */}
        <div className="password-container">
          <input
            type={showConfirmPassword ? "text" : "password"}
            placeholder="Confirm Password *"
            value={form.confirm_password}
            onChange={(e) =>
              setForm({ ...form, confirm_password: e.target.value })
            }
          />
          <span
            className="toggle-visibility"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
          >
            {showConfirmPassword ? "Hide" : "Show"}
          </span>
        </div>

        {/* Live password match check */}
        {form.confirm_password.length > 0 && (
          <p className={passwordsMatch ? "match" : "no-match"}>
            {passwordsMatch ? "Passwords match ✓" : "Passwords do not match ✗"}
          </p>
        )}

        <textarea
          placeholder="Company Description (optional)"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />

        <button type="submit">Register</button>
      </form>

      <p className="msg">{message}</p>
    </div>
  );
}
