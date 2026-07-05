"use client";
import { useState, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Sidebar from "@/components/sidebar/Sidebar";
import ChatArea from "@/components/chat/ChatArea";
import Dashboard from "@/components/dashboard/Dashboard";
import SourcesPanel from "@/components/ui/SourcesPanel";
import { useChat } from "@/hooks/useChat";
import { useIngestion } from "@/hooks/useIngestion";
import type { ActiveView, SearchMode } from "@/types";
import { getConversation } from "@/lib/api";
import type { ChatMessage } from "@/types";

function uuid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

export default function Home() {
  const [activeView, setActiveView] = useState<ActiveView>("chat");
  const { messages, isLoading, conversationId, sendQuestion, startNewChat, setMessages } = useChat();
  const { status: ingestStatus, isPolling, retrieveLatestReviews } = useIngestion();

  const handleNewChat = useCallback(async () => {
    await startNewChat();
    setActiveView("chat");
  }, [startNewChat]);

  const handleLoadConversation = useCallback(async (id: string) => {
    try {
      const conv = await getConversation(id);
      const loaded: ChatMessage[] = [];
      for (const msg of conv.messages || []) {
        loaded.push({
          id: uuid(),
          role: "user",
          content: msg.user_question,
          timestamp: msg.timestamp,
        });
        loaded.push({
          id: uuid(),
          role: "assistant",
          content: msg.response,
          timestamp: msg.timestamp,
          sources: msg.sources,
          confidence: msg.confidence,
        });
      }
      setMessages(loaded);
      setActiveView("chat");
    } catch { }
  }, [setMessages]);

  const handleSend = useCallback(
    (msg: string, mode: SearchMode) => {
      sendQuestion(msg, mode);
    },
    [sendQuestion]
  );

  return (
    <div className="flex h-screen overflow-hidden bg-spotify-black">
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        onNewChat={handleNewChat}
        onLoadConversation={handleLoadConversation}
        currentConversationId={conversationId}
      />

      <main className="flex-1 overflow-hidden">
        <AnimatePresence mode="wait">
          {activeView === "chat" && (
            <motion.div
              key="chat"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full"
            >
              <ChatArea
                messages={messages}
                isLoading={isLoading}
                onSend={handleSend}
                onRetrieveLatest={() => retrieveLatestReviews(false)}
                ingestStatus={ingestStatus}
                isPolling={isPolling}
              />
            </motion.div>
          )}

          {activeView === "dashboard" && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full"
            >
              <Dashboard />
            </motion.div>
          )}

          {activeView === "sources" && (
            <motion.div
              key="sources"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full"
            >
              <SourcesPanel />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
