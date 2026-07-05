"use client";
import { useEffect, useRef } from "react";
import { AnimatePresence } from "framer-motion";
import ChatHeader from "./ChatHeader";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import SuggestedQuestions from "./SuggestedQuestions";
import ChatInput from "./ChatInput";
import type { ChatMessage, IngestStatus, SearchMode } from "@/types";

interface ChatAreaProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSend: (msg: string, mode: SearchMode) => void;
  onRetrieveLatest: () => void;
  ingestStatus: IngestStatus;
  isPolling: boolean;
}

export default function ChatArea({
  messages,
  isLoading,
  onSend,
  onRetrieveLatest,
  ingestStatus,
  isPolling,
}: ChatAreaProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-screen flex-1 overflow-hidden bg-spotify-dark-base">
      {/* Header with Retrieve Latest Reviews button */}
      <ChatHeader
        onRetrieveLatest={onRetrieveLatest}
        ingestStatus={ingestStatus}
        isPolling={isPolling}
      />

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <SuggestedQuestions onSelect={(q) => onSend(q, "semantic")} />
        ) : (
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
            <AnimatePresence initial={false}>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
            </AnimatePresence>
            {isLoading && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <ChatInput onSend={onSend} disabled={isLoading} />
    </div>
  );
}
