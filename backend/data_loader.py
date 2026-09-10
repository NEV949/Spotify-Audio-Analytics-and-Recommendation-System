"""Load clustered Spotify Parquet from HDFS via WebHDFS (Docker), never a local export."""

from __future__ import annotations

import io
import os
import socket
from functools import lru_cache
from typing import Any
from urllib.parse import urlparse, urlunparse

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import requests

AUDIO_FEATURES = [
    "danceability",
    "energy",
    "loudness",
    "acousticness",
    "valence",
    "tempo",
    "speechiness",
    "instrumentalness",
    "liveness",
]

COLUMN_ALIASES = {
    "track_id": ["track_id", "id", "song_id", "uri", "spotify_id"],
    "track_name": ["track_name", "name", "song", "title", "track"],
    "artists": ["artists", "artist", "artist_name", "artist_names"],
    "album_name": ["album_name", "album"],
    "popularity": ["popularity", "track_popularity", "pop"],
    "genre": ["track_genre", "genre", "genres", "playlist_genre"],
    "cluster": ["cluster", "prediction", "cluster_id"],
}

NORM_ALIASES = [
    "normFeatures",
    "normalized_features",
    "features_norm",
    "norm_features",
    "cosine_features",
]

DEFAULT_HDFS = "hdfs://namenode:9000/data/spotify/processed/songs_clustered"


def _resolves(host: str) -> bool:
    try:
        socket.getaddrinfo(host, None)
        return True
    except OSError:
        return False


def _hdfs_path(uri: str) -> str:
    parsed = urlparse(uri)
    path = parsed.path if parsed.scheme else uri.replace("\\", "/")
    if not path.startswith("/"):
        path = "/" + path
    return path.rstrip("/")


def _pick_column(df: pd.DataFrame, logical: str) -> str | None:
    for name in COLUMN_ALIASES[logical]:
        if name in df.columns:
            return name
        matches = [c for c in df.columns if c.lower() == name.lower()]
        if matches:
            return matches[0]
    return None


def _stringify(series: pd.Series) -> pd.Series:
    def _one(value: Any) -> str:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return ""
        if isinstance(value, (list, tuple, np.ndarray)):
            return ", ".join(str(x) for x in value)
        if isinstance(value, dict):
            return ", ".join(str(x) for x in value.values())
        return str(value)

    return series.map(_one)


def _vector_to_array(value: Any, expected_dim: int = 9) -> np.ndarray | None:
    """Decode Spark ML Vector parquet payloads or plain Python lists."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, dict):
        values = value.get("values")
        if values is None:
            return None
        arr = np.asarray(values, dtype=np.float64)
        return arr if arr.size == expected_dim else None
    if hasattr(value, "tolist"):
        arr = np.asarray(value.tolist(), dtype=np.float64)
        if arr.ndim == 0:
            return None
        flat = arr.reshape(-1)
        return flat if flat.size == expected_dim else None
    if isinstance(value, (list, tuple)):
        arr = np.asarray(value, dtype=np.float64).reshape(-1)
        return arr if arr.size == expected_dim else None
    return None


def _candidate_uris(raw: str) -> list[str]:
    """WebHDFS only. Use Docker DNS when it resolves, otherwise host-mapped ports."""
    path = _hdfs_path(raw)
    uris: list[str] = []
    namenode_host = os.getenv("WEBHDFS_HOST", "namenode")
    if _resolves(namenode_host):
        uris.append(f"webhdfs://{namenode_host}:9870{path}")
    uris.append(f"webhdfs://127.0.0.1:9870{path}")

    seen: set[str] = set()
    unique: list[str] = []
    for uri in uris:
        if uri not in seen:
            seen.add(uri)
            unique.append(uri)
    return unique


def _webhdfs_host_fallback(location: str) -> str:
    """Namenode redirects to a datanode container hostname; map that to the published port."""
    parsed = urlparse(location)
    host = parsed.hostname or ""
    port = parsed.port or 9864
    if host in {"localhost", "127.0.0.1"}:
        return location
    if _resolves(host):
        return location
    return urlunparse(parsed._replace(netloc=f"127.0.0.1:{port}"))


def _download_webhdfs_file(session: requests.Session, open_url: str) -> bytes:
    redirect = session.get(open_url, allow_redirects=False, timeout=20)
    location = redirect.headers.get("Location")
    if redirect.status_code in {301, 302, 307, 308} and location:
        data_url = _webhdfs_host_fallback(location)
        payload = session.get(data_url, timeout=60)
    else:
        payload = redirect
    payload.raise_for_status()
    return payload.content


def _read_webhdfs_dataset(host: str, port: int, path: str) -> pd.DataFrame:
    """Read a Parquet directory from HDFS through the namenode WebHDFS API."""
    user = os.getenv("HDFS_USER", "root")
    session = requests.Session()
    list_url = f"http://{host}:{port}/webhdfs/v1{path}?op=LISTSTATUS&user.name={user}"
    listing = session.get(list_url, timeout=20)
    listing.raise_for_status()
    statuses = listing.json()["FileStatuses"]["FileStatus"]
    parts = [item["pathSuffix"] for item in statuses if item["pathSuffix"].endswith(".parquet")]
    if not parts:
        raise FileNotFoundError(f"No parquet parts under hdfs://{host}{path}")

    frames: list[pd.DataFrame] = []
    for part in parts:
        open_url = f"http://{host}:{port}/webhdfs/v1{path}/{part}?op=OPEN&user.name={user}"
        raw = _download_webhdfs_file(session, open_url)
        frames.append(pq.read_table(io.BytesIO(raw)).to_pandas())
    return pd.concat(frames, ignore_index=True)


def _read_parquet(uri: str) -> pd.DataFrame:
    parsed = urlparse(uri)
    if parsed.scheme not in {"webhdfs", "hdfs"}:
        raise ValueError(f"Refusing local path {uri}; dataset must be read from HDFS.")
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (9870 if parsed.scheme == "webhdfs" else 9870)
    if host == "namenode" and not _resolves(host):
        host = "127.0.0.1"
    return _read_webhdfs_dataset(host, port, parsed.path)


def load_raw_frame() -> pd.DataFrame:
    configured = os.getenv("SPOTIFY_PARQUET_PATH", DEFAULT_HDFS)
    errors: list[str] = []
    for uri in _candidate_uris(configured):
        try:
            df = _read_parquet(uri)
            if df is not None and not df.empty:
                return df
        except Exception as exc:  # noqa: BLE001 - collect all backend attempts
            errors.append(f"{uri}: {exc}")
    detail = " | ".join(errors) if errors else "no paths tried"
    raise RuntimeError(
        "Could not read clustered Parquet from HDFS via WebHDFS. "
        "Keep namenode:9870 and datanode:9864 published. Errors: "
        f"{detail}"
    )


def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return matrix / norms


def prepare_catalog(df: pd.DataFrame) -> dict[str, Any]:
    renamed = df.copy()
    mapping: dict[str, str] = {}
    for logical in COLUMN_ALIASES:
        source = _pick_column(renamed, logical)
        if source and source != logical:
            mapping[source] = logical
    if mapping:
        renamed = renamed.rename(columns=mapping)

    missing_features = [f for f in AUDIO_FEATURES if f not in renamed.columns]
    if missing_features:
        raise RuntimeError(f"Missing audio feature columns: {missing_features}")

    if "track_id" not in renamed.columns:
        renamed["track_id"] = renamed.index.astype(str)
    else:
        renamed["track_id"] = renamed["track_id"].astype(str)

    if "track_name" not in renamed.columns:
        renamed["track_name"] = "Unknown Track"
    if "artists" not in renamed.columns:
        renamed["artists"] = "Unknown Artist"
    else:
        renamed["artists"] = _stringify(renamed["artists"])

    if "album_name" not in renamed.columns:
        renamed["album_name"] = ""
    else:
        renamed["album_name"] = _stringify(renamed["album_name"])

    if "genre" not in renamed.columns:
        renamed["genre"] = "unknown"
    else:
        renamed["genre"] = _stringify(renamed["genre"]).replace("", "unknown")

    if "popularity" not in renamed.columns:
        renamed["popularity"] = 0
    renamed["popularity"] = pd.to_numeric(renamed["popularity"], errors="coerce").fillna(0)

    if "cluster" not in renamed.columns:
        raise RuntimeError("Missing `cluster` column from K-Means output.")
    renamed["cluster"] = pd.to_numeric(renamed["cluster"], errors="coerce").fillna(-1).astype(int)

    for feature in AUDIO_FEATURES:
        renamed[feature] = pd.to_numeric(renamed[feature], errors="coerce")

    renamed = renamed.dropna(subset=AUDIO_FEATURES).reset_index(drop=True)

    feature_matrix = renamed[AUDIO_FEATURES].to_numpy(dtype=np.float64)

    norm_col = next((c for c in NORM_ALIASES if c in renamed.columns), None)
    if norm_col:
        decoded = [_vector_to_array(v) for v in renamed[norm_col].tolist()]
        if all(v is not None for v in decoded):
            unit_matrix = np.vstack(decoded)
        else:
            unit_matrix = _l2_normalize(feature_matrix)
    else:
        unit_matrix = _l2_normalize(feature_matrix)

    display_cols = [
        "track_id",
        "track_name",
        "artists",
        "album_name",
        "genre",
        "popularity",
        "cluster",
        *AUDIO_FEATURES,
    ]
    catalog = renamed[display_cols].copy()
    id_to_index = {tid: i for i, tid in enumerate(catalog["track_id"].tolist())}

    return {
        "catalog": catalog,
        "feature_matrix": feature_matrix,
        "unit_matrix": unit_matrix,
        "id_to_index": id_to_index,
        "source_columns": list(df.columns),
    }


@lru_cache(maxsize=1)
def get_store() -> dict[str, Any]:
    return prepare_catalog(load_raw_frame())
