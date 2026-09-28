import io
import os
from functools import lru_cache

import pandas as pd
import requests

HDFS_HOST = os.getenv("HDFS_HOST", "localhost:9871")
HDFS_BASE = f"http://{HDFS_HOST}/webhdfs/v1"

HDFS_PATH = os.getenv(
    "SPOTIFY_PARQUET_PATH",
    "/data/spotify/processed/songs_clustered"
)

def _get(path, op, **params):
    response = requests.get(
        f"{HDFS_BASE}{path}",
        params={"op": op, **params},
        allow_redirects=False,
        timeout=60
    )

    # WebHDFS redirects OPEN requests to the DataNode.
    if response.status_code in (301, 302, 307, 308):
        location = response.headers.get("Location")

        if not location:
            raise RuntimeError("WebHDFS returned a redirect without Location")

        # Docker exposes DataNode HTTP 9864 as host port 9865.
        location = location.replace(
            "host.docker.internal:9864",
            "host.docker.internal:9865"
        )

        response = requests.get(location, timeout=60)

    response.raise_for_status()
    return response

def _list_parquet_files():
    data = _get(HDFS_PATH, "LISTSTATUS").json()
    files = data.get("FileStatuses", {}).get("FileStatus", [])
    return [
        f["pathSuffix"]
        for f in files
        if f.get("type") == "FILE"
        and f["pathSuffix"].endswith(".parquet")
    ]

def _download_parquet(filename):
    path = f"{HDFS_PATH.rstrip('/')}/{filename}"
    return _get(path, "OPEN").content

@lru_cache(maxsize=1)
def load_raw_frame():
    parquet_files = _list_parquet_files()

    if not parquet_files:
        raise RuntimeError(
            f"No Parquet files found in HDFS path: {HDFS_PATH}"
        )

    frames = [
        pd.read_parquet(
            io.BytesIO(_download_parquet(filename)),
            engine="pyarrow"
        )
        for filename in parquet_files
    ]

    df = pd.concat(frames, ignore_index=True)
    return df.replace([float("inf"), float("-inf")], pd.NA)

def get_dataframe():
    return load_raw_frame()

def reload_data():
    load_raw_frame.cache_clear()
    return load_raw_frame()
