import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  try {
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

export function truncate(str: string, maxLen: number): string {
  if (!str) return "";
  return str.length > maxLen ? str.slice(0, maxLen) + "..." : str;
}

export function confidenceColor(confidence: string): string {
  switch (confidence?.toLowerCase()) {
    case "high": return "text-spotify-green";
    case "medium": return "text-yellow-400";
    case "low": return "text-red-400";
    default: return "text-spotify-subdued";
  }
}

export function sentimentColor(sentiment: string): string {
  switch (sentiment?.toLowerCase()) {
    case "positive": return "text-spotify-green";
    case "negative": return "text-red-400";
    default: return "text-spotify-subdued";
  }
}

export function platformIcon(platform: string): string {
  const lower = platform.toLowerCase();
  if (lower.includes("apple") || lower.includes("app store")) return "🍎";
  if (lower.includes("google") || lower.includes("play")) return "🤖";
  if (lower.includes("reddit")) return "🤖";
  if (lower.includes("twitter") || lower.includes("x")) return "🐦";
  if (lower.includes("youtube")) return "▶️";
  if (lower.includes("community")) return "💬";
  return "📝";
}

export function ratingStars(rating: number | string): string {
  const r = parseFloat(String(rating));
  if (isNaN(r)) return "";
  return "★".repeat(Math.round(r)) + "☆".repeat(5 - Math.round(r));
}
