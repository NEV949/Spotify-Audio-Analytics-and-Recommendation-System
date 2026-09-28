from utils import records_to_json

from utils import records_to_json


def search_songs(
    df,
    query=None,
    genre=None,
    min_popularity=None,
    max_popularity=None,
    cluster=None,
    sort_by="popularity",
    descending=True,
    limit=100
):
    result = df.copy()

    # --------------------------------------------------
    # 1. Search by song name, artist, OR genre
    # --------------------------------------------------
    if query and query.strip():
        q = query.strip().lower()

        result = result[
            result["track_name"]
            .fillna("")
            .str.lower()
            .str.contains(q, regex=False)
            |
            result["artists"]
            .fillna("")
            .str.lower()
            .str.contains(q, regex=False)
            |
            result["track_genre"]
            .fillna("")
            .str.lower()
            .str.contains(q, regex=False)
        ]

    # --------------------------------------------------
    # 2. Exact genre filter
    # --------------------------------------------------
    if genre:
        result = result[
            result["track_genre"]
            .fillna("")
            .str.lower()
            == genre.lower()
        ]

    # --------------------------------------------------
    # 3. Popularity filters
    # --------------------------------------------------
    if min_popularity is not None:
        result = result[
            result["popularity"] >= min_popularity
        ]

    if max_popularity is not None:
        result = result[
            result["popularity"] <= max_popularity
        ]

    # --------------------------------------------------
    # 4. Cluster filter
    # --------------------------------------------------
    if cluster is not None:
        result = result[
            result["cluster"] == cluster
        ]

    # --------------------------------------------------
    # 5. Remove duplicate occurrences of the same song
    # --------------------------------------------------
    result = result.drop_duplicates(
        subset=["track_id"]
    )

    # --------------------------------------------------
    # 6. Allowed sorting columns
    # --------------------------------------------------
    allowed = {
        "popularity",
        "track_name",
        "artists",
        "tempo",
        "energy",
        "danceability",
        "valence"
    }

    if sort_by not in allowed:
        sort_by = "popularity"

    # --------------------------------------------------
    # 7. Sort and limit results
    # --------------------------------------------------
    result = result.sort_values(
        sort_by,
        ascending=not descending,
        na_position="last"
    ).head(limit)

    # --------------------------------------------------
    # 8. Columns returned to frontend
    # --------------------------------------------------
    columns = [
        "track_id",
        "track_name",
        "artists",
        "album_name",
        "track_genre",
        "popularity",
        "cluster"
    ]

    return records_to_json(result[columns])


def song_detail(df, track_id):
    result = df[df["track_id"] == track_id]

    if result.empty:
        return None

    return records_to_json(result.head(1))[0]
def song_detail(df, track_id):
    result = df[df["track_id"] == track_id]

    if result.empty:
        return None

    return records_to_json(result.head(1))[0]
