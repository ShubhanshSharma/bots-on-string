"use client";

import React, { useState } from "react";
import { createCompany } from "@/lib/companyService";

const CompanyForm: React.FC = () => {
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createCompany({ name });
      alert("Company created successfully!");
      setName("");
      setIndustry("");
    } catch (err) {
      console.error(err);
      alert("Error creating company.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md"
    >
      <h2 className="text-lg font-semibold mb-4">Add New Company</h2>
      <input
        className="border p-2 w-full mb-3 rounded"
        placeholder="Company Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <input
        className="border p-2 w-full mb-3 rounded"
        placeholder="Industry"
        value={industry}
        onChange={(e) => setIndustry(e.target.value)}
      />
      <button
        type="submit"
        className="w-full bg-blue-500 text-white p-2 rounded"
        disabled={loading}
      >
        {loading ? "Submitting..." : "Create Company"}
      </button>
    </form>
  );
};

export default CompanyForm;
