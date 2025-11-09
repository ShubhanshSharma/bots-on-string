"use client";

import { motion } from "framer-motion";

export default function Loader({
  message = "Loading...",
}: {
  message?: string;
}) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 backdrop-blur-sm flex flex-col items-center justify-center z-50">
      <motion.div
        className="w-16 h-16 border-4 border-t-transparent border-white rounded-full animate-spin"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
      />
      <p className="mt-4 text-white text-lg font-medium">{message}</p>
    </div>
  );
}
