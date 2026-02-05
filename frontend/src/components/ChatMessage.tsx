"use client";

import { ToolCall } from "@/lib/api";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolCalls?: ToolCall[];
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

const toolGradients: Record<string, string> = {
  add_task: "linear-gradient(135deg, #8B5CF6, #EC4899)",
  list_tasks: "linear-gradient(135deg, #14B8A6, #06B6D4)",
  complete_task: "linear-gradient(135deg, #10B981, #34d399)",
  delete_task: "linear-gradient(135deg, #EF4444, #f87171)",
  update_task: "linear-gradient(135deg, #F97316, #FB7185)",
};

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-4 animate-fade-in ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
        style={{
          background: isUser
            ? "linear-gradient(135deg, #8B5CF6, #EC4899)"
            : "linear-gradient(135deg, #14B8A6, #06B6D4)",
        }}
      >
        {isUser ? (
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        ) : (
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        )}
      </div>

      {/* Content */}
      <div className={`flex flex-col max-w-[75%] ${isUser ? "items-end" : "items-start"}`}>
        <span className="text-xs font-medium text-gray-500 mb-1">
          {isUser ? "You" : "TaskAI"}
        </span>

        <div className={isUser ? "chat-user" : "chat-assistant"}>
          <p className="text-sm whitespace-pre-wrap leading-relaxed">
            {message.content}
          </p>

          {/* Tool Calls */}
          {message.toolCalls && message.toolCalls.length > 0 && (
            <div className={`mt-3 pt-3 ${isUser ? "border-t border-white/20" : "border-t border-purple-100"}`}>
              <p className={`text-xs font-medium mb-2 ${isUser ? "text-white/70" : "text-gray-500"}`}>
                Actions performed:
              </p>
              <div className="flex flex-wrap gap-2">
                {message.toolCalls.map((tool, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white"
                    style={{ background: toolGradients[tool.tool_name] || toolGradients.add_task }}
                  >
                    {tool.tool_name === "add_task" && "+ "}
                    {tool.tool_name === "list_tasks" && "# "}
                    {tool.tool_name === "complete_task" && "v "}
                    {tool.tool_name === "delete_task" && "x "}
                    {tool.tool_name === "update_task" && "~ "}
                    {tool.tool_name.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <span className="text-xs text-gray-400 mt-1">
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </span>
      </div>
    </div>
  );
}
