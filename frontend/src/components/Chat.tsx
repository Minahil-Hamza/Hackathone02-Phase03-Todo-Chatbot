"use client";

import { useState, useRef, useEffect } from "react";
import ChatMessage, { Message } from "./ChatMessage";
import ChatInput from "./ChatInput";
import Sidebar from "./Sidebar";
import NavSidebar from "./NavSidebar";
import { MessageSkeleton } from "./ui/Skeleton";
import { sendMessage, ChatResponse, fetchConversationMessages } from "@/lib/api";
import { useAuth } from "@/lib/auth";

function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

export default function Chat() {
  const { user, accessToken, isAuthenticated } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isNavOpen, setIsNavOpen] = useState(false);
  const [taskRefreshTrigger, setTaskRefreshTrigger] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const userId = user?.id || "";

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!isAuthenticated || !accessToken) return;

    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response: ChatResponse = await sendMessage(accessToken, content, conversationId);

      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: response.response,
        toolCalls: response.tool_calls,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      if (response.tool_calls && response.tool_calls.length > 0) {
        setTaskRefreshTrigger((prev) => prev + 1);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(undefined);
    setError(null);
  };

  const handleSelectConversation = async (convId: string) => {
    if (!accessToken) return;
    if (convId === conversationId) return;

    setIsLoading(true);
    setError(null);
    setConversationId(convId);

    try {
      const data = await fetchConversationMessages(accessToken, convId);
      const loadedMessages: Message[] = data.messages.map((msg) => ({
        id: msg.id,
        role: msg.role as "user" | "assistant",
        content: msg.content,
        toolCalls: msg.tool_calls,
        timestamp: new Date(msg.created_at),
      }));
      setMessages(loadedMessages);
    } catch {
      setError("Failed to load conversation");
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-white">
      {/* Left: Nav Sidebar */}
      <NavSidebar
        isOpen={isNavOpen}
        onClose={() => setIsNavOpen(false)}
        onNewChat={handleNewConversation}
        onSelectConversation={handleSelectConversation}
        activeConversationId={conversationId}
      />

      {/* Center: Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 flex items-center justify-between px-4 lg:px-6 border-b border-gray-200 glass">
          <div className="flex items-center gap-3">
            {/* Mobile nav toggle */}
            <button
              onClick={() => setIsNavOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-purple-50 text-gray-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <h1 className="font-bold gradient-text text-lg">TaskAI</h1>
              <p className="text-xs text-gray-500">AI-powered task assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleNewConversation}
              className="btn-secondary hidden sm:flex text-sm"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Chat
            </button>
            {/* Mobile task panel toggle */}
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-purple-50 text-gray-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </button>
          </div>
        </header>

        {/* Messages */}
        <main className="flex-1 overflow-y-auto" style={{
          background: "radial-gradient(ellipse at 20% 50%, rgba(139, 92, 246, 0.03) 0%, transparent 50%), radial-gradient(ellipse at 80% 50%, rgba(236, 72, 153, 0.03) 0%, transparent 50%)"
        }}>
          {messages.length === 0 ? (
            /* Welcome State */
            <div className="h-full flex items-center justify-center p-6">
              <div className="max-w-lg text-center animate-fade-in">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6"
                  style={{ background: "linear-gradient(135deg, #8B5CF6, #EC4899)" }}>
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h2 className="text-3xl font-bold mb-3">
                  <span className="gradient-text">Welcome to TaskAI</span>
                </h2>
                <p className="text-gray-600 mb-8">
                  I can help you manage your tasks using natural language. Just tell me what you need to do!
                </p>

                <div className="grid gap-3">
                  {[
                    { text: "Add a task to review project proposal", icon: "+" },
                    { text: "Show all my tasks", icon: "#" },
                    { text: "Mark the proposal task as done", icon: "v" },
                  ].map((suggestion, i) => (
                    <button
                      key={i}
                      onClick={() => handleSendMessage(suggestion.text)}
                      className="flex items-center gap-3 p-4 text-left rounded-xl bg-white border border-gray-100
                                 hover:border-purple-200 hover:shadow-md transition-all duration-200 group"
                    >
                      <span className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
                        style={{ background: `linear-gradient(135deg, ${
                          i === 0 ? "#8B5CF6, #EC4899" : i === 1 ? "#14B8A6, #06B6D4" : "#F97316, #FB7185"
                        })` }}>
                        {suggestion.icon}
                      </span>
                      <span className="text-sm text-gray-700 group-hover:text-gray-900">{suggestion.text}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Chat Messages */
            <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isLoading && <MessageSkeleton />}
              <div ref={messagesEndRef} />
            </div>
          )}
        </main>

        {/* Error Banner */}
        {error && (
          <div className="px-4 pb-4">
            <div className="max-w-3xl mx-auto p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 animate-fade-in">
              <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="flex-1 text-sm text-red-700">{error}</p>
              <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Input */}
        <ChatInput onSend={handleSendMessage} disabled={isLoading} />
      </div>

      {/* Right: Task Panel */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onNewChat={handleNewConversation}
        userId={userId}
        refreshTrigger={taskRefreshTrigger}
      />
    </div>
  );
}
