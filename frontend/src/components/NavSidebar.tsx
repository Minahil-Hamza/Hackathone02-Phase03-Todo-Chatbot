"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { fetchConversations, deleteConversation, ConversationItem } from "@/lib/api";

interface NavSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  activeConversationId?: string;
}

export default function NavSidebar({
  isOpen,
  onClose,
  onNewChat,
  onSelectConversation,
  activeConversationId,
}: NavSidebarProps) {
  const router = useRouter();
  const { logout, isAuthenticated, user, accessToken } = useAuth();
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    const loadConversations = async () => {
      if (!isAuthenticated || !accessToken) return;
      setIsLoading(true);
      try {
        const data = await fetchConversations(accessToken);
        setConversations(data);
      } catch {
        setConversations([]);
      } finally {
        setIsLoading(false);
      }
    };
    loadConversations();
  }, [isAuthenticated, accessToken]);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
      router.push("/login");
    } finally {
      setIsLoggingOut(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent, convId: string) => {
    e.stopPropagation();
    if (!accessToken) return;
    try {
      await deleteConversation(accessToken, convId);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (activeConversationId === convId) {
        onNewChat();
      }
    } catch {
      // Silently fail
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/40 z-40 lg:hidden" onClick={onClose} />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:relative top-0 left-0 h-full w-64 z-50
        bg-gray-900 text-white
        transform transition-transform duration-200 ease-out
        flex flex-col
        ${isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
      `}>
        {/* Header */}
        <div className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center"
              style={{ background: "linear-gradient(135deg, #8B5CF6, #EC4899)" }}>
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <span className="text-lg font-bold">TaskAI</span>
          </div>
          <button onClick={onClose} className="lg:hidden p-1 rounded-md hover:bg-gray-800 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* New Chat Button */}
        <div className="px-3 mb-2">
          <button
            onClick={() => {
              onNewChat();
              onClose();
            }}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium
                       border border-gray-700 hover:bg-gray-800 transition-all duration-200
                       hover:border-purple-500/50"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto px-3 space-y-1">
          {isLoading ? (
            <div className="space-y-2 pt-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-10 bg-gray-800 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center pt-8">
              <p className="text-sm text-gray-500">No conversations yet</p>
            </div>
          ) : (
            conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => {
                  onSelectConversation(conv.id);
                  onClose();
                }}
                className={`w-full group flex items-center gap-2 px-3 py-2.5 rounded-lg text-left
                           transition-all duration-150 ${
                  activeConversationId === conv.id
                    ? "bg-gray-800 border border-purple-500/30"
                    : "hover:bg-gray-800/60"
                }`}
              >
                <svg className="w-4 h-4 flex-shrink-0 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate text-gray-300">
                    {conv.preview}
                  </p>
                  <p className="text-2xs text-gray-600">{formatDate(conv.updated_at)}</p>
                </div>
                <button
                  onClick={(e) => handleDelete(e, conv.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-gray-700
                             text-gray-500 hover:text-red-400 transition-all"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </button>
            ))
          )}
        </div>

        {/* User Section */}
        {isAuthenticated && (
          <div className="p-3 border-t border-gray-800">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                style={{ background: "linear-gradient(135deg, #8B5CF6, #EC4899)" }}>
                {user?.email?.charAt(0).toUpperCase() || "U"}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-300 truncate">
                  {user?.email || "User"}
                </p>
              </div>
              <button
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="p-1.5 rounded-md text-gray-500 hover:text-red-400 hover:bg-gray-800 transition-colors"
                title="Sign out"
              >
                {isLoggingOut ? (
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        )}
      </aside>
    </>
  );
}
