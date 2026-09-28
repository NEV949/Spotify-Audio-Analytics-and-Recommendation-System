import React from "react";
import { useState } from "react";

import Dashboard from "./components/Dashboard";
import SongExplorer from "./components/SongExplorer";
import GenreAnalytics from "./components/GenreAnalytics";
import ArtistAnalytics from "./components/ArtistAnalytics";
import PopularityAnalytics from "./components/PopularityAnalytics";
import ClusterExplorer from "./components/ClusterExplorer";
import MoodExplorer from "./components/MoodExplorer";
import RecommendPanel from "./components/RecommendPanel";
import Correlations from "./components/Correlations";

const pages = [
  ["dashboard", "Dashboard", "⌂"],
  ["songs", "Song Explorer", "♫"],
  ["genres", "Genre Analytics", "◈"],
  ["artists", "Artist Analytics", "♟"],
  ["popularity", "Popularity", "★"],
  ["clusters", "Clusters", "◎"],
  ["moods", "Mood Explorer", "◌"],
  ["recommend", "Recommendations", "✦"],
  ["correlations", "Correlations", "⌁"]
];

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const currentPage =
    pages.find(([id]) => id === page)?.[1] || "Dashboard";

  function navigate(id) {
    setPage(id);
    setSidebarOpen(false);
  }

  return (
    <div className="app-shell">

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>

        <div className="brand">
          <div className="brand-icon">♫</div>

          <div>
            <h1>Music Insight</h1>
            <span>Big Data Analytics</span>
          </div>
        </div>

        <div className="sidebar-section">
          <span className="sidebar-label">ANALYTICS</span>

          <nav className="sidebar-nav">
            {pages.map(([id, label, icon]) => (
              <button
                key={id}
                className={`nav-item ${
                  page === id ? "active" : ""
                }`}
                onClick={() => navigate(id)}
              >
                <span className="nav-icon">{icon}</span>
                <span>{label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="sidebar-bottom">

          <div className="tech-card">
            <div className="tech-status">
              <span className="status-dot"></span>
              System Online
            </div>

            <p>
              PySpark · HDFS · FastAPI
            </p>
          </div>

          <div className="sidebar-footer">
            Spotify Big Data Project
          </div>

        </div>
      </aside>

      {/* Main application */}
      <div className="main-shell">

        {/* Top bar */}
        <header className="topbar">

          <button
            className="mobile-menu"
            onClick={() => setSidebarOpen(true)}
          >
            ☰
          </button>

          <div className="topbar-page">
            <span className="breadcrumb">
              Analytics
            </span>

            <span className="breadcrumb-separator">
              /
            </span>

            <strong>{currentPage}</strong>
          </div>

          <div className="topbar-right">

            <div className="system-pill">
              <span className="status-dot"></span>
              Live
            </div>

          </div>

        </header>

        {/* Page content */}
        <main className="content">
          {page === "dashboard" && <Dashboard />}
          {page === "songs" && <SongExplorer />}
          {page === "genres" && <GenreAnalytics />}
          {page === "artists" && <ArtistAnalytics />}
          {page === "popularity" && <PopularityAnalytics />}
          {page === "clusters" && <ClusterExplorer />}
          {page === "moods" && <MoodExplorer />}
          {page === "recommend" && <RecommendPanel />}
          {page === "correlations" && <Correlations />}
        </main>

      </div>
    </div>
  );
}