"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquare, BarChart2, Database, Plus, Trash2, Clock
} from "lucide-react";
import { cn } from "@/lib/utils";
import { getConversations, deleteConversation } from "@/lib/api";
import type { Conversation, ActiveView } from "@/types";

interface SidebarProps {
  activeView: ActiveView;
  onViewChange: (view: ActiveView) => void;
  onNewChat: () => void;
  onLoadConversation: (id: string) => void;
  currentConversationId: string | null;
}

export default function Sidebar({
  activeView,
  onViewChange,
  onNewChat,
  onLoadConversation,
  currentConversationId,
}: SidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    if (activeView === "chat") {
      loadConversations();
    }
  }, [activeView, currentConversationId]);

  async function loadConversations() {
    try {
      const convs = await getConversations();
      setConversations(convs);
    } catch { /* backend may not be running */ }
  }

  async function handleDelete(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    await deleteConversation(id);
    setConversations((prev) => prev.filter((c) => c.id !== id));
  }

  const navItems = [
    { view: "chat" as ActiveView, icon: MessageSquare, label: "Chat" },
    { view: "dashboard" as ActiveView, icon: BarChart2, label: "Dashboard" },
    { view: "sources" as ActiveView, icon: Database, label: "Data Sources" },
  ];

  return (
    <aside className="flex flex-col w-64 h-screen bg-spotify-black border-r border-white/10 flex-shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2 px-6 py-5 border-b border-white/10">
        <svg viewBox="0 0 24 24" className="w-8 h-8 fill-spotify-green" aria-hidden="true">
          <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z" />
        </svg>
        <div>
          <p className="text-white font-bold text-sm leading-tight">Research</p>
          <p className="text-spotify-green text-xs font-semibold">Assistant</p>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="px-4 pt-4 pb-2">
        <button
          onClick={onNewChat}
          className="flex items-center gap-2 w-full px-4 py-2.5 rounded-full bg-spotify-green text-black font-bold text-sm hover:bg-spotify-green-light transition-colors"
        >
          <Plus size={16} />
          New Chat
        </button>
      </div>

      {/* Navigation */}
      <nav className="px-3 py-2">
        {navItems.map(({ view, icon: Icon, label }) => (
          <button
            key={view}
            onClick={() => onViewChange(view)}
            className={cn(
              "flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-all mb-1",
              activeView === view
                ? "bg-spotify-dark-highlight text-white"
                : "text-spotify-subdued hover:bg-spotify-dark-highlight hover:text-white"
            )}
          >
            <Icon size={18} />
            {label}
          </button>
        ))}
      </nav>

      {/* Chat History */}
      {activeView === "chat" && conversations.length > 0 && (
        <>
          <div className="px-4 pt-2 pb-1">
            <p className="text-xs font-semibold text-spotify-subdued uppercase tracking-wider flex items-center gap-1">
              <Clock size={12} /> Recent
            </p>
          </div>
          <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-1">
            <AnimatePresence>
              {conversations.slice(0, 20).map((conv) => (
                <motion.div
                  key={conv.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  className={cn(
                    "group flex items-center justify-between w-full px-3 py-2 rounded-lg text-xs cursor-pointer transition-all",
                    currentConversationId === conv.id
                      ? "bg-spotify-dark-highlight text-white"
                      : "text-spotify-subdued hover:bg-spotify-dark-highlight hover:text-white"
                  )}
                  onClick={() => onLoadConversation(conv.id)}
                >
                  <span className="truncate flex-1">{conv.preview}</span>
                  <button
                    onClick={(e) => handleDelete(conv.id, e)}
                    className="opacity-0 group-hover:opacity-100 ml-1 p-1 rounded hover:text-red-400 transition-all"
                    aria-label="Delete conversation"
                  >
                    <Trash2 size={12} />
                  </button>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </>
      )}

      {/* Footer */}
      <div className="px-4 py-3 border-t border-white/10 mt-auto">
        <p className="text-xs text-spotify-subdued text-center">
          Powered by Groq + ChromaDB
        </p>
      </div>
    </aside>
  );
}
