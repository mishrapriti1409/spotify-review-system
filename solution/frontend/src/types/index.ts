export interface RetrievedDoc {
  text: string;
  score: number;
  platform: string;
  rating: number | string;
  date: string;
  sentiment: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  confidence: "High" | "Medium" | "Low";
  retrieved_count: number;
  retrieved_docs: RetrievedDoc[];
  conversation_id: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  sources?: string[];
  confidence?: string;
  retrieved_docs?: RetrievedDoc[];
  retrieved_count?: number;
}

export interface Conversation {
  id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  preview: string;
}

export interface IngestStatus {
  running: boolean;
  progress: string;
  total_ingested: number;
  total_indexed: number;
  error: string | null;
  completed_at: string | null;
}

export interface AnalyticsData {
  generated_at: string;
  total_reviews: number;
  reviews_by_source: Record<string, number>;
  sentiment_distribution: { positive: number; neutral: number; negative: number };
  rating_distribution: Record<string, number>;
  topic_distribution: Record<string, number>;
  pain_point_frequency: Record<string, number>;
  discovery_challenges: Record<string, number>;
  recommendation_complaints: Record<string, number>;
  feature_requests: string[];
  listening_behaviors: Record<string, number>;
  timeline_trends: Array<{
    month: string;
    count: number;
    positive: number;
    negative: number;
    neutral: number;
  }>;
  top_keywords: Array<{ text: string; value: number }>;
  avg_rating_by_platform: Record<string, number>;
}

export type SearchMode = "semantic" | "keyword" | "hybrid";
export type ActiveView = "chat" | "dashboard" | "sources";
