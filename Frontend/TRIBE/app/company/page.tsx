"use client";

import CompanyForm from "@/components/CompanyForm";

export default function CompanyPage() {
  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">🏢 Company Management</h1>
      <CompanyForm />
    </div>
  );
}
