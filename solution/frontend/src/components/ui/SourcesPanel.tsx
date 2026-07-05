"use client";
import { useState, useEffect } from "react";
import { CheckCircle, XCircle, RefreshCw, Info } from "lucide-react";
import { triggerIngestion, getIngestionStatus, getIngestionStats } from "@/lib/api";
import { cn } from "@/lib/utils";

const SOURCE_INFO = [
  {
    key: "appstore",
    name: "Apple App Store",
    icon: "🍎",
    description: "Spotify iOS app reviews — fetched automatically, no setup needed.",
    requiresSetup: false,
  },
  {
    key: "playstore",
    name: "Google Play Store",
    icon: "🤖",
    description: "Spotify Android app reviews — fetched automatically, no setup needed.",
    requiresSetup: false,
  },
  {
    key: "reddit",
    name: "Reddit",
    icon: "👾",
    description: "Discussions from r/spotify, r/truespotify, r/music — loaded from local dataset.",
    requiresSetup: false,
  },
];

export default function SourcesPanel() {
  const [selected, setSelected] = useState<Set<string>>(
    new Set(["appstore", "playstore", "reddit"])
  );
  const [ingestStatus, setIngestStatus] = useState<string>("");
  const [running, setRunning] = useState(false);
  const [stats, setStats] = useState<{ total_documents?: number } | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  async function loadStats() {
    try {
      const s = await getIngestionStats();
      setStats(s);
    } catch {}
  }

  function toggleSource(key: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
  }

  async function handleIngest() {
    if (running || selected.size === 0) return;
    setRunning(true);
    setIngestStatus("Starting ingestion...");

    try {
      await triggerIngestion(Array.from(selected));

      const interval = setInterval(async () => {
        try {
          const s = await getIngestionStatus();
          setIngestStatus(s.progress || "Running...");
          if (!s.running) {
            clearInterval(interval);
            setRunning(false);
            if (s.error) {
              setIngestStatus(`Error: ${s.error}`);
            } else if (s.total_indexed > 0) {
              setIngestStatus(`✓ Done! ${s.total_indexed} reviews indexed.`);
              loadStats();
            }
          }
        } catch {
          clearInterval(interval);
          setRunning(false);
          setIngestStatus("Could not reach backend.");
        }
      }, 2000);
    } catch {
      setIngestStatus("Failed to start. Check backend is running.");
      setRunning(false);
    }
  }

  return (
    <div className="flex flex-col h-screen overflow-y-auto bg-spotify-dark-base px-6 py-6">
      <div className="max-w-2xl">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-white font-bold text-lg mb-1">Data Sources</h1>
          <p className="text-spotify-subdued text-sm">
            Select the sources to ingest into the knowledge base.
          </p>
        </div>

        {/* Current stats */}
        {stats && (
          <div className="mb-5 px-4 py-3 bg-spotify-green/10 border border-spotify-green/20 rounded-xl flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-spotify-green animate-pulse" />
            <p className="text-sm text-spotify-green font-medium">
              {stats.total_documents ?? 0} reviews currently indexed
            </p>
          </div>
        )}

        {/* Source cards */}
        <div className="space-y-3 mb-6">
          {SOURCE_INFO.map((src) => (
            <div
              key={src.key}
              className={cn(
                "flex items-center justify-between p-4 rounded-2xl border cursor-pointer transition-all select-none",
                selected.has(src.key)
                  ? "bg-spotify-green/10 border-spotify-green/40"
                  : "bg-spotify-dark-elevated border-white/5 hover:border-white/20"
              )}
              onClick={() => toggleSource(src.key)}
              role="checkbox"
              aria-checked={selected.has(src.key)}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{src.icon}</span>
                <div>
                  <p className="text-white font-medium text-sm">{src.name}</p>
                  <p className="text-spotify-subdued text-xs mt-0.5">{src.description}</p>
                </div>
              </div>
              {selected.has(src.key) ? (
                <CheckCircle size={20} className="text-spotify-green flex-shrink-0" />
              ) : (
                <XCircle size={20} className="text-white/20 flex-shrink-0" />
              )}
            </div>
          ))}
        </div>

        {/* Progress message */}
        {ingestStatus && (
          <div
            className={cn(
              "mb-4 px-4 py-3 rounded-xl text-sm border",
              ingestStatus.startsWith("✓")
                ? "bg-spotify-green/10 border-spotify-green/20 text-spotify-green"
                : ingestStatus.toLowerCase().includes("error") || ingestStatus.toLowerCase().includes("failed")
                ? "bg-red-500/10 border-red-500/20 text-red-400"
                : "bg-white/5 border-white/10 text-spotify-text"
            )}
          >
            {running && (
              <span className="inline-block w-2 h-2 rounded-full bg-yellow-400 animate-pulse mr-2" />
            )}
            {ingestStatus}
          </div>
        )}

        {/* Ingest button */}
        <button
          onClick={handleIngest}
          disabled={running || selected.size === 0}
          className={cn(
            "flex items-center gap-2 px-6 py-3 rounded-full font-semibold text-sm transition-all",
            running || selected.size === 0
              ? "bg-white/10 text-spotify-subdued cursor-not-allowed"
              : "bg-spotify-green text-black hover:bg-spotify-green-light active:scale-95"
          )}
        >
          <RefreshCw size={16} className={cn(running && "animate-spin")} />
          {running
            ? "Ingesting..."
            : `Ingest ${selected.size} Source${selected.size !== 1 ? "s" : ""}`}
        </button>

        {/* Info note */}
        <div className="mt-6 flex gap-2 text-xs text-spotify-subdued">
          <Info size={14} className="flex-shrink-0 mt-0.5" />
          <p>
            App Store and Play Store reviews are fetched directly. Reddit data is loaded
            from the local dataset included with this app. Ingestion takes 1–3 minutes
            on first run while the AI model processes reviews.
          </p>
        </div>
      </div>
    </div>
  );
}
