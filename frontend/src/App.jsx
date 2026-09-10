import { useEffect, useState } from "react";
import AnalyticsOverview from "./components/AnalyticsOverview.jsx";
import Correlations from "./components/Correlations.jsx";
import ClusterExplorer from "./components/ClusterExplorer.jsx";
import RecommendPanel from "./components/RecommendPanel.jsx";

const TABS = [
  { id: "overview", label: "Analytics Overview" },
  { id: "correlations", label: "Audio Feature Correlations" },
  { id: "clusters", label: "Cluster Explorer" },
  { id: "recommend", label: "Search & Recommend" },
];

export default function App() {
  const [tab, setTab] = useState("overview");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const initial = params.get("tab");
    if (TABS.some((item) => item.id === initial)) {
      setTab(initial);
    }
  }, []);

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-white/10 bg-black/40 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-spotify-green">HDFS · Hive · PySpark · K-Means</p>
            <h1 className="text-2xl font-semibold">Spotify Cluster Analytics</h1>
          </div>
          <p className="max-w-md text-sm text-spotify-muted">
            9 audio features, Hive aggregations, 8 clusters, cosine recommendations.
          </p>
        </div>
        <nav className="mx-auto flex max-w-7xl gap-2 overflow-x-auto px-6 pb-3">
          {TABS.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setTab(item.id)}
              className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition ${
                tab === item.id
                  ? "bg-spotify-green text-black"
                  : "bg-white/5 text-zinc-300 hover:bg-white/10"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        {tab === "overview" && <AnalyticsOverview />}
        {tab === "correlations" && <Correlations />}
        {tab === "clusters" && <ClusterExplorer />}
        {tab === "recommend" && <RecommendPanel />}
      </main>
    </div>
  );
}
