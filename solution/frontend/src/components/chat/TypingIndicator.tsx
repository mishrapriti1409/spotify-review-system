"use client";
import { motion } from "framer-motion";

export default function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex items-end gap-2">
        <div className="w-8 h-8 rounded-full bg-spotify-dark-highlight flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
          AI
        </div>
        <div className="bg-spotify-dark-elevated border border-white/5 rounded-2xl rounded-bl-sm px-4 py-3">
          <div className="flex items-center gap-1">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="w-2 h-2 bg-spotify-green rounded-full"
                animate={{ scale: [1, 1.4, 1], opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
              />
            ))}
          </div>
          <p className="text-xs text-spotify-subdued mt-1">Searching reviews...</p>
        </div>
      </div>
    </div>
  );
}
