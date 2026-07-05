"use client";
import { useState, useRef, KeyboardEvent } from "react";
import { Send, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import type { SearchMode } from "@/types";

interface ChatInputProps {
  onSend: (message: string, mode: SearchMode) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<SearchMode>("semantic");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleSend() {
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed, mode);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleInput() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  const modes: { value: SearchMode; label: string }[] = [
    { value: "semantic", label: "Semantic" },
    { value: "keyword", label: "Keyword" },
    { value: "hybrid", label: "Hybrid" },
  ];

  return (
    <div className="px-4 pb-4 pt-2 border-t border-white/10 bg-spotify-dark-base">
      <div className="relative bg-spotify-dark-highlight rounded-2xl border border-white/10 focus-within:border-spotify-green/50 transition-colors">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            handleInput();
          }}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Ask about Spotify customer feedback..."
          rows={1}
          className="w-full bg-transparent text-white placeholder:text-spotify-subdued text-sm px-4 pt-3 pb-2 resize-none outline-none max-h-40 overflow-y-auto"
          aria-label="Chat message input"
        />

        <div className="flex items-center justify-between px-3 pb-2">
          {/* Search mode selector */}
          <div className="flex items-center gap-1 bg-black/30 rounded-full px-1 py-0.5">
            <Search size={11} className="text-spotify-subdued ml-1" />
            {modes.map((m) => (
              <button
                key={m.value}
                onClick={() => setMode(m.value)}
                className={cn(
                  "text-xs px-2.5 py-1 rounded-full transition-all",
                  mode === m.value
                    ? "bg-spotify-green text-black font-semibold"
                    : "text-spotify-subdued hover:text-white"
                )}
              >
                {m.label}
              </button>
            ))}
          </div>

          {/* Send button */}
          <button
            onClick={handleSend}
            disabled={!input.trim() || disabled}
            className={cn(
              "flex items-center justify-center w-8 h-8 rounded-full transition-all",
              input.trim() && !disabled
                ? "bg-spotify-green text-black hover:bg-spotify-green-light active:scale-95"
                : "bg-white/10 text-spotify-subdued cursor-not-allowed"
            )}
            aria-label="Send message"
          >
            <Send size={15} />
          </button>
        </div>
      </div>

      <p className="text-center text-xs text-spotify-subdued mt-2">
        Answers are grounded in real customer reviews only.
      </p>
    </div>
  );
}
