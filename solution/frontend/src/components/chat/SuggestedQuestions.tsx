"use client";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

const SUGGESTED_QUESTIONS = [
  "Why do users struggle discovering new music?",
  "Why do users replay the same playlists?",
  "What complaints exist about recommendations?",
  "What feature requests appear most often?",
  "Compare Reddit and Play Store complaints.",
  "What do Premium users complain about?",
  "Which user segments struggle most?",
  "What unmet needs appear repeatedly?",
  "Why do users skip recommendations?",
  "What causes recommendation fatigue?",
];

interface SuggestedQuestionsProps {
  onSelect: (q: string) => void;
}

export default function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full px-6 py-8">
      {/* Spotify-style welcome */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="w-16 h-16 bg-spotify-green rounded-full flex items-center justify-center mx-auto mb-4">
          <svg viewBox="0 0 24 24" className="w-8 h-8 fill-black" aria-hidden="true">
            <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">
          What do customers think?
        </h2>
        <p className="text-spotify-subdued text-sm max-w-md">
          Ask questions about Spotify customer reviews. Every answer is grounded in real customer feedback.
        </p>
      </motion.div>

      {/* Question grid */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-2xl"
      >
        {SUGGESTED_QUESTIONS.map((q, i) => (
          <motion.button
            key={q}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 * i }}
            onClick={() => onSelect(q)}
            className="flex items-start gap-2 text-left px-4 py-3 rounded-xl bg-spotify-dark-elevated border border-white/5 hover:border-spotify-green/40 hover:bg-spotify-dark-highlight transition-all group text-sm text-spotify-text hover:text-white"
          >
            <Sparkles size={14} className="text-spotify-green mt-0.5 flex-shrink-0 group-hover:animate-pulse" />
            {q}
          </motion.button>
        ))}
      </motion.div>
    </div>
  );
}
