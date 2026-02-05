"use client";

import { useState } from "react";

interface AddTaskFormProps {
  onAdd: (title: string) => Promise<void>;
}

export default function AddTaskForm({ onAdd }: AddTaskFormProps) {
  const [title, setTitle] = useState("");
  const [isAdding, setIsAdding] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = title.trim();
    if (!trimmed || isAdding) return;

    setIsAdding(true);
    try {
      await onAdd(trimmed);
      setTitle("");
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Add a new task..."
        className="flex-1 px-3 py-2 text-sm bg-white/60 border border-gray-200 rounded-lg
                   placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500
                   focus:border-transparent transition-all"
      />
      <button
        type="submit"
        disabled={!title.trim() || isAdding}
        className="px-3 py-2 rounded-lg text-white text-sm font-medium
                   disabled:opacity-40 transition-all duration-200 hover:shadow-glow"
        style={{ background: "linear-gradient(135deg, #8B5CF6, #EC4899)" }}
      >
        {isAdding ? (
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        )}
      </button>
    </form>
  );
}
