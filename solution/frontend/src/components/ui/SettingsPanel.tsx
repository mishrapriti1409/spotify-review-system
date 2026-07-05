"use client";
import { useState, useEffect } from "react";
import { Save } from "lucide-react";
import { cn } from "@/lib/utils";

interface Settings {
  apiUrl: string;
  searchMode: string;
  topK: number;
  groqModel: string;
}

const GROQ_MODELS = [
  "llama-3.3-70b-versatile",
  "llama3-70b-8192",
  "mixtral-8x7b-32768",
];

export default function SettingsPanel() {
  const [settings, setSettings] = useState<Settings>({
    apiUrl: "http://localhost:8000",
    searchMode: "semantic",
    topK: 10,
    groqModel: "llama-3.3-70b-versatile",
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("spotify_rag_settings");
    if (stored) {
      try { setSettings(JSON.parse(stored)); } catch { }
    }
  }, []);

  function handleSave() {
    localStorage.setItem("spotify_rag_settings", JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <div className="flex flex-col h-screen overflow-y-auto bg-spotify-dark-base px-6 py-6">
      <div className="max-w-lg">
        <h1 className="text-white font-bold text-lg mb-1">Settings</h1>
        <p className="text-spotify-subdued text-sm mb-6">Configure your research assistant.</p>

        <div className="space-y-5">
          {/* API URL */}
          <div>
            <label className="block text-sm text-spotify-subdued mb-1.5">Backend API URL</label>
            <input
              type="text"
              value={settings.apiUrl}
              onChange={(e) => setSettings({ ...settings, apiUrl: e.target.value })}
              className="w-full bg-spotify-dark-highlight border border-white/10 text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-spotify-green/50"
            />
          </div>

          {/* Search Mode */}
          <div>
            <label className="block text-sm text-spotify-subdued mb-1.5">Default Search Mode</label>
            <div className="flex gap-2">
              {["semantic", "keyword", "hybrid"].map((m) => (
                <button
                  key={m}
                  onClick={() => setSettings({ ...settings, searchMode: m })}
                  className={cn(
                    "px-4 py-2 rounded-full text-sm capitalize transition-all",
                    settings.searchMode === m
                      ? "bg-spotify-green text-black font-semibold"
                      : "bg-spotify-dark-highlight text-spotify-subdued hover:text-white border border-white/10"
                  )}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* Top K */}
          <div>
            <label className="block text-sm text-spotify-subdued mb-1.5">
              Top-K Retrieval: {settings.topK}
            </label>
            <input
              type="range"
              min={3}
              max={20}
              value={settings.topK}
              onChange={(e) => setSettings({ ...settings, topK: Number(e.target.value) })}
              className="w-full accent-spotify-green"
            />
          </div>

          {/* Model */}
          <div>
            <label className="block text-sm text-spotify-subdued mb-1.5">Groq Model</label>
            <select
              value={settings.groqModel}
              onChange={(e) => setSettings({ ...settings, groqModel: e.target.value })}
              className="w-full bg-spotify-dark-highlight border border-white/10 text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-spotify-green/50"
            >
              {GROQ_MODELS.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>

          {/* Save */}
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-6 py-2.5 bg-spotify-green text-black font-semibold rounded-full hover:bg-spotify-green-light transition-all active:scale-95"
          >
            <Save size={15} />
            {saved ? "Saved!" : "Save Settings"}
          </button>
        </div>

        <div className="mt-8 p-4 bg-spotify-dark-elevated border border-white/5 rounded-2xl">
          <h3 className="text-white font-semibold text-sm mb-2">Setup Instructions</h3>
          <ol className="text-xs text-spotify-subdued space-y-1.5 list-decimal list-inside">
            <li>Add your Groq API key to <code className="text-spotify-green">solution/configs/config.json</code></li>
            <li>Add Reddit credentials to the same config file</li>
            <li>Run <code className="text-spotify-green">pip install -r backend/requirements.txt</code></li>
            <li>Start backend: <code className="text-spotify-green">uvicorn backend.api.main:app --reload --port 8000</code></li>
            <li>Go to Data Sources and click Ingest to populate the knowledge base</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
