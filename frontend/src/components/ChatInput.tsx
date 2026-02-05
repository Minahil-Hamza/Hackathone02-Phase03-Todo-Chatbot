"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({
  onSend,
  disabled = false,
  placeholder = "Type a message...",
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSubmit = () => {
    const trimmed = message.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white/80 backdrop-blur-lg p-4">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              className="w-full px-4 py-3 text-sm bg-white/60 border border-gray-200 rounded-xl
                         resize-none placeholder:text-gray-400 text-gray-900
                         focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent
                         backdrop-blur-sm transition-all duration-200"
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={disabled || !message.trim()}
            className="p-3 rounded-xl text-white disabled:opacity-40 transition-all duration-200
                       hover:shadow-glow active:scale-95"
            style={{ background: "linear-gradient(135deg, #8B5CF6, #EC4899)" }}
          >
            {disabled ? (
              <div className="flex gap-1">
                <span className="loading-dot w-1.5 h-1.5 bg-white rounded-full" />
                <span className="loading-dot w-1.5 h-1.5 bg-white rounded-full" />
                <span className="loading-dot w-1.5 h-1.5 bg-white rounded-full" />
              </div>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>

        <p className="text-xs text-gray-400 mt-2 text-center">
          Press <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-xs">Enter</kbd> to send
          {" · "}
          <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-xs">Shift + Enter</kbd> for new line
        </p>
      </div>
    </div>
  );
}
