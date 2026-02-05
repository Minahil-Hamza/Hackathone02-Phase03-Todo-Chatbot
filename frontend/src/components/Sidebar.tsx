"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { fetchTasks, createTask, toggleTask, deleteTask, updateTask, TaskItem } from "@/lib/api";
import TaskCard from "./TaskCard";
import AddTaskForm from "./AddTaskForm";
import CircularProgress from "./CircularProgress";
import { TaskCardSkeleton } from "./ui/Skeleton";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  userId: string;
  refreshTrigger?: number;
}

type Filter = "all" | "active" | "completed";

export default function Sidebar({
  isOpen,
  onClose,
  refreshTrigger = 0,
}: SidebarProps) {
  const { isAuthenticated, accessToken } = useAuth();
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [filter, setFilter] = useState<Filter>("all");

  const loadTasks = async () => {
    if (!isAuthenticated || !accessToken) return;
    setIsLoading(true);
    try {
      const data = await fetchTasks(accessToken);
      setTasks(data.tasks);
    } catch {
      setTasks([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [isAuthenticated, accessToken, refreshTrigger]);

  const filteredTasks = tasks.filter((t) =>
    filter === "all" ? true : filter === "active" ? !t.is_completed : t.is_completed
  );

  const completedCount = tasks.filter((t) => t.is_completed).length;
  const activeCount = tasks.filter((t) => !t.is_completed).length;
  const totalCount = tasks.length;
  const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  const handleAddTask = async (title: string) => {
    if (!accessToken) return;
    const newTask = await createTask(accessToken, title);
    setTasks((prev) => [newTask, ...prev]);
  };

  const handleToggle = async (id: string) => {
    if (!accessToken) return;
    const updated = await toggleTask(accessToken, id);
    setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
  };

  const handleDelete = async (id: string) => {
    if (!accessToken) return;
    await deleteTask(accessToken, id);
    setTasks((prev) => prev.filter((t) => t.id !== id));
  };

  const handleUpdate = async (id: string, title: string) => {
    if (!accessToken) return;
    const updated = await updateTask(accessToken, id, { title });
    setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
  };

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/20 z-40 lg:hidden" onClick={onClose} />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:relative top-0 right-0 h-full w-80 z-50
        bg-gray-50 border-l border-gray-200
        transform transition-transform duration-200 ease-out
        ${isOpen ? "translate-x-0" : "translate-x-full lg:translate-x-0"}
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
            <h2 className="font-bold text-gray-900">Tasks</h2>
            <button onClick={onClose} className="lg:hidden p-1.5 rounded-md hover:bg-gray-100 transition-colors">
              <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="p-4 space-y-4 overflow-y-auto flex-1">
            {/* Add Task Form */}
            <AddTaskForm onAdd={handleAddTask} />

            {/* Stats Row */}
            <div className="grid grid-cols-3 gap-2">
              {/* Total */}
              <div className="rounded-xl p-3 text-center text-white"
                style={{ background: "linear-gradient(135deg, #8B5CF6, #EC4899)" }}>
                <div className="text-xl font-bold">{totalCount}</div>
                <div className="text-xs opacity-80">Total</div>
              </div>
              {/* Active */}
              <div className="rounded-xl p-3 text-center text-white"
                style={{ background: "linear-gradient(135deg, #F97316, #FB7185)" }}>
                <div className="text-xl font-bold">{activeCount}</div>
                <div className="text-xs opacity-80">Active</div>
              </div>
              {/* Done */}
              <div className="rounded-xl p-3 text-center text-white"
                style={{ background: "linear-gradient(135deg, #14B8A6, #06B6D4)" }}>
                <div className="text-xl font-bold">{completedCount}</div>
                <div className="text-xs opacity-80">Done</div>
              </div>
            </div>

            {/* Circular Progress */}
            <div className="flex justify-center py-2">
              <CircularProgress percentage={progress} />
            </div>

            {/* Filter Tabs */}
            <div className="flex gap-1 p-1 bg-gray-100 rounded-lg">
              {(["all", "active", "completed"] as Filter[]).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all duration-200 ${
                    filter === f
                      ? "text-white shadow-sm"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                  style={filter === f ? { background: "linear-gradient(135deg, #8B5CF6, #EC4899)" } : {}}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>

            {/* Task List */}
            <div className="space-y-2">
              {isLoading ? (
                <>
                  <TaskCardSkeleton />
                  <TaskCardSkeleton />
                  <TaskCardSkeleton />
                </>
              ) : filteredTasks.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-3"
                    style={{ background: "linear-gradient(135deg, #8B5CF6, #EC4899)", opacity: 0.2 }}>
                    <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-900">No tasks</p>
                  <p className="text-xs text-gray-500 mt-1">Add a task above or chat with AI</p>
                </div>
              ) : (
                filteredTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    id={task.id}
                    title={task.title}
                    isCompleted={task.is_completed}
                    onToggle={handleToggle}
                    onDelete={handleDelete}
                    onUpdate={handleUpdate}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
