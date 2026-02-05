"use client";

import { ReactNode } from "react";

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

/**
 * EmptyState component for displaying when no content is available
 *
 * @example
 * <EmptyState
 *   title="No messages yet"
 *   description="Start a conversation to see messages here"
 *   action={<Button>Start Chat</Button>}
 * />
 */
export default function EmptyState({
  icon,
  title,
  description,
  action,
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center text-center py-12 px-4 ${className}`}
      role="status"
      aria-label={title}
    >
      {icon && (
        <div className="mb-4 text-slate-400 dark:text-slate-500">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
        {title}
      </h3>
      {description && (
        <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mb-6">
          {description}
        </p>
      )}
      {action && <div>{action}</div>}
    </div>
  );
}

/**
 * ChatEmptyState - Empty state for chat interface
 */
export function ChatEmptyState() {
  return (
    <EmptyState
      icon={
        <svg
          className="w-20 h-20"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      }
      title="Welcome to AI Todo Chatbot"
      description="Start a conversation to manage your tasks with natural language. Try asking me to create a task, show your tasks, or mark something as complete."
    />
  );
}

/**
 * NoTasksEmptyState - Empty state for tasks list
 */
export function NoTasksEmptyState() {
  return (
    <EmptyState
      icon={
        <svg
          className="w-16 h-16"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
      }
      title="No tasks yet"
      description="Create your first task by chatting with the AI assistant"
    />
  );
}
