import axios from "axios";
import type { ChatResponse, AnalyticsData, IngestStatus, Conversation } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
  timeout: 60000,  // 60s — first query loads the embedding model (~30s), subsequent ones are fast
});

// ── Chat ──────────────────────────────────────────────────────────────────────

export async function sendMessage(
  question: string,
  conversationId: string | null,
  searchMode: string = "semantic"
): Promise<ChatResponse> {
  const res = await api.post<ChatResponse>("/chat/", {
    question,
    conversation_id: conversationId,
    search_mode: searchMode,
  });
  return res.data;
}

export async function createConversation(): Promise<string> {
  const res = await api.post<{ conversation_id: string }>("/chat/new");
  return res.data.conversation_id;
}

export async function getConversations(): Promise<Conversation[]> {
  const res = await api.get<{ conversations: Conversation[] }>("/chat/conversations");
  return res.data.conversations;
}

export async function getConversation(id: string) {
  const res = await api.get(`/chat/conversations/${id}`);
  return res.data;
}

export async function deleteConversation(id: string) {
  await api.delete(`/chat/conversations/${id}`);
}

// ── Ingestion ─────────────────────────────────────────────────────────────────

export async function triggerIngestion(
  sources?: string[],
  reset: boolean = false
): Promise<void> {
  await api.post("/ingest/", { sources, reset });
}

export async function getIngestionStatus(): Promise<IngestStatus> {
  const res = await api.get<IngestStatus>("/ingest/status");
  return res.data;
}

export async function getIngestionStats() {
  const res = await api.get("/ingest/stats");
  return res.data;
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export async function getAnalytics(): Promise<AnalyticsData> {
  const res = await api.get<AnalyticsData>("/analytics/");
  return res.data;
}

export async function refreshAnalytics(): Promise<AnalyticsData> {
  const res = await api.post<AnalyticsData>("/analytics/refresh");
  return res.data;
}

// ── Search ────────────────────────────────────────────────────────────────────

export async function searchReviews(query: string, mode: string = "semantic", topK: number = 10) {
  const res = await api.post("/search/", { query, top_k: topK, search_mode: mode });
  return res.data;
}

// ── Health ────────────────────────────────────────────────────────────────────

export async function getHealth() {
  const res = await api.get("/health");
  return res.data;
}
