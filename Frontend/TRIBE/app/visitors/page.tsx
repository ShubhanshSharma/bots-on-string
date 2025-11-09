"use client";

import { useEffect, useState } from "react";
import VisitorCard from "@/components/VisitorCard";
import { getVisitors, Visitor } from "@/lib/visitorService";

export default function VisitorsPage() {
  const [visitors, setVisitors] = useState<Visitor[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getVisitors();
      setVisitors(data);
    };
    fetchData();
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-4">
      <h1 className="text-2xl font-semibold mb-4">👥 Visitors List</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {visitors.map((v) => (
          <VisitorCard key={v.id} visitor={v} />
        ))}
      </div>
    </div>
  );
}
