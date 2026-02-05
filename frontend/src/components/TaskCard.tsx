"use client";

import { useState } from "react";

interface TaskCardProps {
  id: string;
  title: string;
  isCompleted: boolean;
  onToggle: (id: string) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onUpdate: (id: string, title: string) => Promise<void>;
}

export default function TaskCard({
  id,
  title,
  isCompleted,
  onToggle,
  onDelete,
  onUpdate,
}: TaskCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(title);
  const [isHovered, setIsHovered] = useState(false);

  const handleSave = async () => {
    const trimmed = editTitle.trim();
    if (trimmed && trimmed !== title) {
      await onUpdate(id, trimmed);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSave();
    if (e.key === "Escape") {
      setEditTitle(title);
      setIsEditing(false);
    }
  };

  return (
    <div
      className={`group relative p-3 rounded-xl border transition-all duration-200 ${
        isCompleted
          ? "bg-gray-50 border-gray-100"
          : "bg-white border-gray-100 hover:border-purple-200 hover:shadow-md"
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <button
          onClick={() => onToggle(id)}
          className={`mt-0.5 w-5 h-5 rounded-md flex-shrink-0 flex items-center justify-center
                     transition-all duration-200 ${
            isCompleted
              ? "text-white"
              : "border-2 border-gray-300 hover:border-purple-500"
          }`}
          style={isCompleted ? { background: "linear-gradient(135deg, #14B8A6, #06B6D4)" } : {}}
        >
          {isCompleted && (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>

        {/* Title */}
        {isEditing ? (
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onBlur={handleSave}
            onKeyDown={handleKeyDown}
            autoFocus
            className="flex-1 text-sm bg-transparent border-b-2 border-purple-400 outline-none py-0.5"
          />
        ) : (
          <p
            onDoubleClick={() => {
              if (!isCompleted) {
                setIsEditing(true);
              }
            }}
            className={`flex-1 text-sm leading-relaxed ${
              isCompleted
                ? "text-gray-400 line-through"
                : "text-gray-800"
            }`}
          >
            {title}
          </p>
        )}

        {/* Action buttons (visible on hover) */}
        {isHovered && !isEditing && (
          <div className="flex items-center gap-1 animate-fade-in">
            {!isCompleted && (
              <button
                onClick={() => setIsEditing(true)}
                className="p-1 rounded-md text-gray-400 hover:text-purple-600 hover:bg-purple-50 transition-colors"
                title="Edit"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            )}
            <button
              onClick={() => onDelete(id)}
              className="p-1 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
              title="Delete"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
