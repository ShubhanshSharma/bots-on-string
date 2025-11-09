import React from "react";

interface VisitorCardProps {
  visitor: {
    id: number;
    anonymous_id: string;
    created_at?: string;
  };
}

const VisitorCard: React.FC<VisitorCardProps> = ({ visitor }) => (
  <div className="bg-white shadow-md rounded-lg p-4 mb-3">
    <h3 className="text-lg font-semibold">🧑 Visitor #{visitor.id}</h3>
    <p className="text-gray-600">
      Anonymous ID:{" "}
      <span className="font-mono text-blue-600">{visitor.anonymous_id}</span>
    </p>
    <small className="text-gray-400">
      Joined:{" "}
      {visitor.created_at
        ? new Date(visitor.created_at).toLocaleString()
        : "N/A"}
    </small>
  </div>
);

export default VisitorCard;
