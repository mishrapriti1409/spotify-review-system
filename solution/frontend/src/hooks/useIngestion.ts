"use client";
import { useState, useCallback, useRef, useEffect } from "react";
import { triggerIngestion, getIngestionStatus } from "@/lib/api";
import type { IngestStatus } from "@/types";

export function useIngestion() {
  const [status, setStatus] = useState<IngestStatus>({
    running: false,
    progress: "",
    total_ingested: 0,
    total_indexed: 0,
    error: null,
    completed_at: null,
  });
  const [isPolling, setIsPolling] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    setIsPolling(false);
  }, []);

  const startPolling = useCallback(() => {
    setIsPolling(true);
    pollRef.current = setInterval(async () => {
      try {
        const s = await getIngestionStatus();
        setStatus(s);
        if (!s.running) {
          stopPolling();
        }
      } catch {
        stopPolling();
      }
    }, 2000);
  }, [stopPolling]);

  const retrieveLatestReviews = useCallback(
    async (reset: boolean = false) => {
      try {
        await triggerIngestion(undefined, reset);
        startPolling();
      } catch (err) {
        console.error("Failed to trigger ingestion:", err);
      }
    },
    [startPolling]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  return {
    status,
    isPolling,
    retrieveLatestReviews,
  };
}
