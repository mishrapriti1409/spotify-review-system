"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { ChevronDown, ChevronUp, ExternalLink } from "lucide-react";
import { cn, confidenceColor, sentimentColor, platformIcon, ratingStars, formatDate } from "@/lib/utils";
import type { ChatMessage } from "@/types";

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const [showEvidence, setShowEvidence] = useState(false);
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={cn("flex", isUser ? "justify-end" : "justify-start")}
    >
      <div className={cn("max-w-[85%]", isUser ? "order-1" : "order-2")}>
        {/* Avatar */}
        <div className={cn("flex items-end gap-2", isUser ? "flex-row-reverse" : "flex-row")}>
          <div
            className={cn(
              "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold",
              isUser ? "bg-spotify-green text-black" : "bg-spotify-dark-highlight text-white"
            )}
          >
            {isUser ? "You" : "AI"}
          </div>

          <div
            className={cn(
              "rounded-2xl px-4 py-3 text-sm",
              isUser
                ? "bg-spotify-green text-black rounded-br-sm"
                : "bg-spotify-dark-elevated text-white rounded-bl-sm border border-white/5"
            )}
          >
            {isUser ? (
              <p>{message.content}</p>
            ) : (
              <div className="prose prose-invert prose-sm max-w-none">
                <ReactMarkdown
                  components={{
                    h2: ({ children }) => (
                      <h2 className="text-spotify-green font-bold text-sm mt-3 mb-1 first:mt-0">{children}</h2>
                    ),
                    ul: ({ children }) => <ul className="list-disc list-inside space-y-1 my-1">{children}</ul>,
                    li: ({ children }) => <li className="text-spotify-text">{children}</li>,
                    p: ({ children }) => <p className="mb-2 last:mb-0 text-white/90">{children}</p>,
                    strong: ({ children }) => <strong className="text-white font-semibold">{children}</strong>,
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
          </div>
        </div>

        {/* Metadata row for assistant messages */}
        {!isUser && (message.sources?.length || message.confidence) && (
          <div className="flex flex-wrap items-center gap-2 mt-2 ml-10 text-xs">
            {/* Confidence badge */}
            {message.confidence && (
              <span className={cn("font-medium", confidenceColor(message.confidence))}>
                {message.confidence} confidence
              </span>
            )}

            {/* Sources */}
            {message.sources?.map((src) => (
              <span
                key={src}
                className="flex items-center gap-1 px-2 py-0.5 bg-white/5 rounded-full text-spotify-subdued border border-white/10"
              >
                {platformIcon(src)} {src}
              </span>
            ))}

            {/* Retrieved count */}
            {message.retrieved_count !== undefined && message.retrieved_count > 0 && (
              <span className="text-spotify-subdued">
                {message.retrieved_count} reviews retrieved
              </span>
            )}

            {/* Toggle evidence */}
            {message.retrieved_docs && message.retrieved_docs.length > 0 && (
              <button
                onClick={() => setShowEvidence((v) => !v)}
                className="flex items-center gap-1 text-spotify-green hover:text-spotify-green-light transition-colors"
              >
                {showEvidence ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                {showEvidence ? "Hide" : "Show"} evidence
              </button>
            )}
          </div>
        )}

        {/* Evidence panel */}
        {showEvidence && message.retrieved_docs && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-2 ml-10 space-y-2"
          >
            {message.retrieved_docs.map((doc, i) => (
              <div
                key={i}
                className="bg-spotify-dark-highlight/50 border border-white/5 rounded-xl p-3 text-xs backdrop-blur-xs"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="flex items-center gap-1 text-spotify-green font-medium">
                    {platformIcon(doc.platform)} {doc.platform}
                  </span>
                  <div className="flex items-center gap-2 text-spotify-subdued">
                    {doc.rating && <span>{ratingStars(doc.rating)}</span>}
                    {doc.date && <span>{doc.date}</span>}
                    <span className={sentimentColor(doc.sentiment)}>{doc.sentiment}</span>
                    <span className="text-spotify-green">Score: {doc.score.toFixed(2)}</span>
                  </div>
                </div>
                <p className="text-white/80 leading-relaxed">{doc.text}</p>
              </div>
            ))}
          </motion.div>
        )}

        <p className="text-xs text-spotify-subdued mt-1 ml-10">
          {new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </p>
      </div>
    </motion.div>
  );
}
