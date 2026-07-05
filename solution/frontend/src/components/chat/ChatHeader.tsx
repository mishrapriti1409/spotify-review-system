"use client";
import { RefreshCw, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import type { IngestStatus } from "@/types";

interface ChatHeaderProps {
  onRetrieveLatest: () => void;
  ingestStatus: IngestStatus;
  isPolling: boolean;
}

export default function ChatHeader({
  onRetrieveLatest,
  ingestStatus,
  isPolling,
}: ChatHeaderProps) {
  const isRunning = ingestStatus.running || isPolling;
  const hasError = !!ingestStatus.error;
  const isComplete =
    !isRunning && !hasError && !!ingestStatus.completed_at;

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-spotify-dark-base/80 backdrop-blur-sm">
      <div>
        <h1 className="text-white font-bold text-lg">Customer Intelligence Chat</h1>
        <p className="text-spotify-subdued text-xs mt-0.5">
          Ask questions about Spotify customer feedback
        </p>
      </div>

      <div className="flex items-center gap-3">
        {/* Status badge */}
        <AnimatePresence mode="wait">
          {isRunning && (
            <motion.div
              key="running"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex items-center gap-2 text-xs text-yellow-400 bg-yellow-400/10 px-3 py-1.5 rounded-full border border-yellow-400/20"
            >
              <Loader2 size={12} className="animate-spin" />
              <span className="max-w-[200px] truncate">{ingestStatus.progress || "Fetching..."}</span>
            </motion.div>
          )}
          {isComplete && !isRunning && (
            <motion.div
              key="complete"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2 text-xs text-spotify-green bg-spotify-green/10 px-3 py-1.5 rounded-full border border-spotify-green/20"
            >
              <CheckCircle size={12} />
              <span>{ingestStatus.total_indexed} reviews indexed</span>
            </motion.div>
          )}
          {hasError && (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2 text-xs text-red-400 bg-red-400/10 px-3 py-1.5 rounded-full border border-red-400/20"
            >
              <AlertCircle size={12} />
              <span>Fetch failed</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Retrieve Latest Reviews Button */}
        <button
          onClick={onRetrieveLatest}
          disabled={isRunning}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold transition-all",
            isRunning
              ? "bg-white/10 text-spotify-subdued cursor-not-allowed"
              : "bg-spotify-green text-black hover:bg-spotify-green-light active:scale-95"
          )}
        >
          <RefreshCw size={14} className={cn(isRunning && "animate-spin")} />
          Retrieve Latest Reviews
        </button>
      </div>
    </header>
  );
}
