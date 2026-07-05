"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, LineChart, Line, Legend
} from "recharts";
import { RefreshCw, TrendingUp, MessageSquare, Star, Smile } from "lucide-react";
import { getAnalytics, refreshAnalytics } from "@/lib/api";
import type { AnalyticsData } from "@/types";
import { cn } from "@/lib/utils";

const SPOTIFY_COLORS = ["#1DB954", "#1ed760", "#169c46", "#0f6630", "#ffffff20"];
const SENTIMENT_COLORS = { positive: "#1DB954", neutral: "#A7A7A7", negative: "#E74C3C" };

export default function Dashboard() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { loadAnalytics(); }, []);

  async function loadAnalytics() {
    setLoading(true);
    setError(null);
    try {
      const d = await getAnalytics();
      setData(d);
    } catch {
      setError("No analytics available. Run ingestion first.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRefresh() {
    setRefreshing(true);
    try {
      const d = await refreshAnalytics();
      setData(d);
    } catch { } finally {
      setRefreshing(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-spotify-green border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-spotify-subdued">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-spotify-subdued mb-4">{error || "No data available"}</p>
          <button
            onClick={loadAnalytics}
            className="px-6 py-2 bg-spotify-green text-black font-semibold rounded-full hover:bg-spotify-green-light transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const sentimentData = [
    { name: "Positive", value: data.sentiment_distribution.positive, color: SENTIMENT_COLORS.positive },
    { name: "Neutral", value: data.sentiment_distribution.neutral, color: SENTIMENT_COLORS.neutral },
    { name: "Negative", value: data.sentiment_distribution.negative, color: SENTIMENT_COLORS.negative },
  ];

  const sourceData = Object.entries(data.reviews_by_source).map(([name, value]) => ({ name, value }));
  const topicData = Object.entries(data.topic_distribution).slice(0, 10).map(([name, value]) => ({ name: name.replace(/_/g, " "), value }));
  const ratingData = Object.entries(data.rating_distribution).map(([star, count]) => ({ star: `${star}★`, count }));

  return (
    <div className="flex flex-col h-screen overflow-y-auto bg-spotify-dark-base">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 sticky top-0 bg-spotify-dark-base/95 backdrop-blur-sm z-10">
        <div>
          <h1 className="text-white font-bold text-lg">Analytics Dashboard</h1>
          <p className="text-spotify-subdued text-xs">
            Last updated: {new Date(data.generated_at).toLocaleString()}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-spotify-dark-highlight text-white text-sm hover:bg-white/10 transition-colors"
        >
          <RefreshCw size={14} className={cn(refreshing && "animate-spin")} />
          Refresh
        </button>
      </div>

      <div className="p-6 space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: "Total Reviews", value: data.total_reviews.toLocaleString(), icon: MessageSquare, color: "text-spotify-green" },
            { label: "Avg Rating", value: Object.values(data.avg_rating_by_platform).length ? (Object.values(data.avg_rating_by_platform).reduce((a, b) => a + b, 0) / Object.values(data.avg_rating_by_platform).length).toFixed(1) : "N/A", icon: Star, color: "text-yellow-400" },
            { label: "Positive Sentiment", value: `${Math.round((data.sentiment_distribution.positive / data.total_reviews) * 100)}%`, icon: Smile, color: "text-green-400" },
            { label: "Data Sources", value: Object.keys(data.reviews_by_source).length, icon: TrendingUp, color: "text-blue-400" },
          ].map(({ label, value, icon: Icon, color }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-spotify-dark-elevated border border-white/5 rounded-2xl p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <p className="text-spotify-subdued text-xs">{label}</p>
                <Icon size={16} className={color} />
              </div>
              <p className="text-white text-2xl font-bold">{value}</p>
            </motion.div>
          ))}
        </div>

        {/* Charts row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Sentiment Pie */}
          <ChartCard title="Sentiment Distribution">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={sentimentData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="value" paddingAngle={3}>
                  {sentimentData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#1A1A1A", border: "1px solid #282828", borderRadius: "12px", color: "#fff" }} />
                <Legend iconType="circle" iconSize={10} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Reviews by Source Bar */}
          <ChartCard title="Reviews by Source">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={sourceData} barSize={32}>
                <CartesianGrid strokeDasharray="3 3" stroke="#282828" />
                <XAxis dataKey="name" tick={{ fill: "#A7A7A7", fontSize: 11 }} />
                <YAxis tick={{ fill: "#A7A7A7", fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "#1A1A1A", border: "1px solid #282828", borderRadius: "12px", color: "#fff" }} />
                <Bar dataKey="value" fill="#1DB954" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* Timeline */}
        {data.timeline_trends.length > 0 && (
          <ChartCard title="Review Volume Over Time">
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={data.timeline_trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#282828" />
                <XAxis dataKey="month" tick={{ fill: "#A7A7A7", fontSize: 11 }} />
                <YAxis tick={{ fill: "#A7A7A7", fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "#1A1A1A", border: "1px solid #282828", borderRadius: "12px", color: "#fff" }} />
                <Legend />
                <Line type="monotone" dataKey="positive" stroke="#1DB954" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="negative" stroke="#E74C3C" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="neutral" stroke="#A7A7A7" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
        )}

        {/* Charts row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Topic Distribution */}
          <ChartCard title="Topic Distribution">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={topicData} layout="vertical" barSize={16}>
                <CartesianGrid strokeDasharray="3 3" stroke="#282828" />
                <XAxis type="number" tick={{ fill: "#A7A7A7", fontSize: 10 }} />
                <YAxis type="category" dataKey="name" width={120} tick={{ fill: "#A7A7A7", fontSize: 10 }} />
                <Tooltip contentStyle={{ background: "#1A1A1A", border: "1px solid #282828", borderRadius: "12px", color: "#fff" }} />
                <Bar dataKey="value" fill="#1DB954" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Rating Distribution */}
          <ChartCard title="Rating Distribution">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={ratingData} barSize={40}>
                <CartesianGrid strokeDasharray="3 3" stroke="#282828" />
                <XAxis dataKey="star" tick={{ fill: "#A7A7A7", fontSize: 12 }} />
                <YAxis tick={{ fill: "#A7A7A7", fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "#1A1A1A", border: "1px solid #282828", borderRadius: "12px", color: "#fff" }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {ratingData.map((_, i) => (
                    <Cell key={i} fill={SPOTIFY_COLORS[i % SPOTIFY_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* Feature Requests */}
        {data.feature_requests?.length > 0 && (
          <ChartCard title="Top Feature Requests">
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {data.feature_requests.slice(0, 10).map((req, i) => (
                <div key={i} className="flex items-start gap-3 text-sm">
                  <span className="text-spotify-green font-bold text-xs mt-0.5">{i + 1}</span>
                  <p className="text-spotify-text">{req}</p>
                </div>
              ))}
            </div>
          </ChartCard>
        )}

        {/* Word Cloud (keyword frequency as badges) */}
        {data.top_keywords?.length > 0 && (
          <ChartCard title="Top Keywords">
            <div className="flex flex-wrap gap-2">
              {data.top_keywords.slice(0, 40).map(({ text, value }, i) => {
                const size = Math.max(11, Math.min(18, 11 + Math.floor(value / 3)));
                return (
                  <span
                    key={i}
                    className="px-2.5 py-1 bg-spotify-dark-highlight rounded-full text-spotify-green border border-spotify-green/20 hover:border-spotify-green/60 transition-colors cursor-default"
                    style={{ fontSize: size }}
                  >
                    {text}
                    <span className="text-spotify-subdued text-xs ml-1">({value})</span>
                  </span>
                );
              })}
            </div>
          </ChartCard>
        )}
      </div>
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-spotify-dark-elevated border border-white/5 rounded-2xl p-5">
      <h3 className="text-white font-semibold text-sm mb-4">{title}</h3>
      {children}
    </div>
  );
}
