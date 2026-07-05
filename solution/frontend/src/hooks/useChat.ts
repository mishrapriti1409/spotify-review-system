"use client";
import { useState, useCallback, useRef } from "react";
import { sendMessage, createConversation } from "@/lib/api";
import type { ChatMessage, ChatResponse } from "@/types";

function uuid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startNewChat = useCallback(async () => {
    const id = await createConversation();
    setConversationId(id);
    setMessages([]);
    setError(null);
  }, []);

  const sendQuestion = useCallback(
    async (question: string, searchMode: string = "semantic") => {
      if (!question.trim()) return;
      setError(null);

      const userMsg: ChatMessage = {
        id: uuid(),
        role: "user",
        content: question,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      try {
        const res: ChatResponse = await sendMessage(question, conversationId, searchMode);
        if (!conversationId) setConversationId(res.conversation_id);

        const assistantMsg: ChatMessage = {
          id: uuid(),
          role: "assistant",
          content: res.answer,
          timestamp: new Date().toISOString(),
          sources: res.sources,
          confidence: res.confidence,
          retrieved_docs: res.retrieved_docs,
          retrieved_count: res.retrieved_count,
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Failed to get response";
        setError(message);
        const errorMsg: ChatMessage = {
          id: uuid(),
          role: "assistant",
          content: "Sorry, I encountered an error. Please check the backend is running and try again.",
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId]
  );

  return {
    messages,
    isLoading,
    conversationId,
    error,
    sendQuestion,
    startNewChat,
    setMessages,
  };
}
