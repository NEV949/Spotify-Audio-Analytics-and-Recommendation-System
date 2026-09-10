"""Run HiveQL against HiveServer2 (Beeline in Docker), with pandas fallback."""

from __future__ import annotations

import io
import os
import subprocess
from pathlib import Path

import pandas as pd

HIVE_TABLE = "spotify.songs_clustered"
REPO_ROOT = Path(__file__).resolve().parent.parent
INIT_HQL = REPO_ROOT / "hive" / "init.hql"
HIVE_CONTAINER = os.getenv("HIVE_CONTAINER", "hiveserver2")

KPI_SQL = f"""
SELECT
  COUNT(*) AS tracks,
  COUNT(DISTINCT artists) AS artists,
  COUNT(DISTINCT track_genre) AS genres,
  COUNT(DISTINCT cluster) AS clusters,
  AVG(popularity) AS avg_popularity,
  AVG(danceability) AS avg_danceability,
  AVG(energy) AS avg_energy,
  AVG(valence) AS avg_valence
FROM {HIVE_TABLE}
"""

TOP_TRACKS_SQL = f"""
SELECT track_id, track_name, artists, album_name, track_genre AS genre, popularity, cluster,
       danceability, energy, loudness, acousticness, valence, tempo, speechiness, instrumentalness, liveness
FROM {HIVE_TABLE}
ORDER BY popularity DESC
LIMIT 10
"""

TOP_ARTISTS_SQL = f"""
SELECT artists AS artist, COUNT(*) AS tracks, AVG(popularity) AS avg_popularity
FROM {HIVE_TABLE}
GROUP BY artists
ORDER BY tracks DESC, avg_popularity DESC
LIMIT 10
"""

GENRES_SQL = f"""
SELECT
  track_genre AS genre,
  COUNT(*) AS tracks,
  AVG(popularity) AS avg_popularity,
  AVG(danceability) AS avg_danceability,
  AVG(energy) AS avg_energy,
  AVG(loudness) AS avg_loudness,
  AVG(acousticness) AS avg_acousticness,
  AVG(valence) AS avg_valence,
  AVG(tempo) AS avg_tempo
FROM {HIVE_TABLE}
GROUP BY track_genre
ORDER BY tracks DESC
LIMIT 15
"""


def hive_available() -> bool:
    try:
        probe = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", HIVE_CONTAINER],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        return probe.stdout.strip().lower() == "true"
    except (OSError, subprocess.SubprocessError):
        return False


def _beeline(sql: str) -> str:
    one_line = " ".join(sql.strip().rstrip(";").split())
    cmd = [
        "docker",
        "exec",
        HIVE_CONTAINER,
        "/opt/hive/bin/beeline",
        "-u",
        "jdbc:hive2://localhost:10000",
        "-n",
        os.getenv("HIVE_USER", "hive"),
        "--silent=true",
        "--showHeader=true",
        "--outputformat=tsv2",
        "-e",
        one_line,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=25, check=False)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "beeline failed").strip()[:2000])
    return result.stdout


def _parse_tsv(stdout: str) -> pd.DataFrame:
    rows = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("+") or stripped.startswith("|"):
            continue
        lower = stripped.lower()
        if lower.startswith("slf4j") or "beeline" in lower or lower.startswith("connecting"):
            continue
        rows.append(stripped)
    if not rows:
        return pd.DataFrame()
    return pd.read_csv(io.StringIO("\n".join(rows)), sep="\t")


def hive_query(sql: str) -> pd.DataFrame:
    return _parse_tsv(_beeline(sql))


def ensure_hive_table() -> None:
    subprocess.run(
        ["docker", "exec", "namenode", "hdfs", "dfs", "-mkdir", "-p", "/user/hive/warehouse"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if not INIT_HQL.exists():
        return
    statements = [part.strip() for part in INIT_HQL.read_text(encoding="utf-8").split(";") if part.strip()]
    for stmt in statements:
        hive_query(stmt)


def hive_status() -> dict:
    if not hive_available():
        return {"ok": False, "engine": "pandas", "detail": f"container {HIVE_CONTAINER} is not running"}
    return {
        "ok": True,
        "engine": "hive",
        "detail": "HiveServer2 is running. Dashboard KPIs use the in-memory catalog; pass engine=hive to run Beeline SQL.",
    }
